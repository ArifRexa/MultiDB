from blacksheep import Request, Response, Content
from config.db import DbConfig
from exceptions.custom_exceptions import DatabaseInfoError
from helpers.response import make_response
import logging


class UrlVerificationMiddleware:
    async def __call__(self, request: Request, handler):
        if request.path in ["/docs", "/openapi.json"]:
            response = await handler(request)
            return response

        try:
            payload = await request.json()
            if (not payload) or not (
                payload.get("database_info", {}).get("table_name")
                and payload.get("database_info", {}).get("table_name")
            ):
                raise DatabaseInfoError("Missing required database information")
            elif (not payload) or not (
                payload.get("database_info", {}).get("username")
                and payload.get("database_info", {}).get("username")
            ):
                raise Exception(
                    "Missing required user or password information. Please check the request JSON body and ensure that all required keys are provided with correct spelling and complete data.",
                    {"status_code": 404},
                )
            elif (not payload) or not (
                payload.get("database_info", {}).get("password")
                and payload.get("database_info", {}).get("password")
            ):
                raise Exception(
                    "Missing required user or password information. Please check the request JSON body and ensure that all required keys are provided with correct spelling and complete data.",
                    {"status_code": 404},
                )
            response = await handler(request)
            return response
        except DatabaseInfoError as ex:
            return make_response(
                status=404,
                data="Missing database information. Please check the request JSON body and ensure that all required keys are provided with correct spelling and complete data.",
            )
        except Exception as ex:
            return make_response(data=ex)


class DBGenerationMiddleware:
    async def __call__(self, request: Request, handler):
        if request.path in ["/docs", "/openapi.json"]:
            response = await handler(request)
            return response

        try:
            payload = await request.json()
            database_name = payload.get("database_info", {}).get("database_name")
            username = payload.get("database_info", {}).get("username")
            password = payload.get("database_info", {}).get("password")
            DbConfig().generate_database().set_database_user_pass(
                database_name=database_name, user_name=username, password=password
            )
            response = await handler(request)
            return response
        except Exception as ex:
            logging.error("Error encountered")
