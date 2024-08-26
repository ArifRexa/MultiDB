from datetime import datetime, timedelta

import jwt
from blacksheep import Request
from guardpost.asynchronous.authentication import (AuthenticationHandler,
                                                   Identity)
from jwt.exceptions import InvalidSignatureError

from config.settings import AUTHORIZATION_STATUS, JWT_SETTINGS, SECRET_KEY
from models.models import User


class TokenParser:
    token_type = None

    def __init__(self, encoded_token):
        token_dict = self.decoder(encoded_token)
        if token_dict.get('type') != self.token_type:
            raise ValueError(f"Please provide a valid {self.token_type}, instead of {token_dict.get('type')}")
        self.uid = token_dict.get('uid')
        self.exp = token_dict.get('exp')
        self.token = encoded_token

    @staticmethod
    def encoder(uid, lifetime, type='access_token'):
        payload = dict(
            uid=uid,
            exp=datetime.utcnow() + timedelta(hours=lifetime),
            type=type
        )
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decoder(encoded_token):
        try:
            payload = jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])
        except InvalidSignatureError as ex:
            raise Exception(str(ex))
        return payload


class RefreshToken(TokenParser):
    token_type = "refresh_token"

    @property
    def access_token(self):
        if hasattr(self, 'uid'):
            uid = self.uid
        else:
            raise ValueError("Please initialize with a valid Token!")

        if datetime.now().timestamp() >= self.exp:
            raise ValueError("Token lifetime has expired! Generate a new refresh token!")

        return self.encoder(uid, JWT_SETTINGS.get('access_token_lifetime'), "access_token")


class AccessToken(TokenParser):
    token_type = "access_token"

    @property
    def get_user(self):
        user, session = User.get_single_object(id=self.uid)
        if not user:
            raise ValueError("Invalid token! No User found!")
        return user


class CentralAuthHandler(AuthenticationHandler):
    def __init__(self):
        pass

    async def authenticate(self, context: Request):
        if AUTHORIZATION_STATUS == "inactive":
            context.identity = Identity({}, "True")
        elif header_value := context.get_first_header(b"Authorization"):
            # header to get an actual user's identity
            access_token = header_value.decode("utf-8").split('Bearer ')[-1].strip()
            try:
                access_token_obj = AccessToken(access_token)
                user = access_token_obj.get_user
                context.identity = Identity({"user": user}, "True")
            except Exception as ex:
                print("exception happend in token authentication!")
                print("details; ", ex)
                context.identity = None
        else:
            context.identity = None

        return context.identity
