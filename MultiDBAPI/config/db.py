import logging

import sqlalchemy.exc
from urllib.parse import quote
from config.settings import DB_ENGINE, DB_HOST, DB_PORT, DB_APPLICATION_NAME
from exceptions.custom_exceptions import DatabaseInfoError
from psycopg2 import OperationalError
import sqlalchemy as sql
from sqlalchemy import inspect, text


class DbConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def generate_database(self):
        # self._user = DB_USER
        # self._password = DB_PASS
        self._application_name = (
            quote(DB_APPLICATION_NAME) if DB_APPLICATION_NAME else None
        )
        self._engine = DB_ENGINE
        self._host = DB_HOST
        self._port = DB_PORT
        return self

    def set_database_name(self, database_name: str):
        self._name = database_name

    def set_database_user_pass(self, database_name: str, user_name: str, password: str):
        self._name = database_name
        self._user = user_name
        self._password = quote(password)

    @property
    def database_connection_url(self):
        # logging.info("application name: %s", self._application_name)
        if self._application_name:
            # logging.info(
            #     f"{self._engine}://{self._user}:{self._password}@{self._host}:{self._port}/{self._name}?application_name={self._application_name}"
            # )
            return f"{self._engine}://{self._user}:{self._password}@{self._host}:{self._port}/{self._name}?application_name={self._application_name}"
        else:
            # logging.info(
            #     f"{self._engine}://{self._user}:{self._password}@{self._host}:{self._port}/{self._name}"
            # )
            return f"{self._engine}://{self._user}:{self._password}@{self._host}:{self._port}/{self._name}"

    @property
    def database_name(self):
        return self._name

    def get_db_columns(self, model_name: str):
        """Get and Return Table Information from Database after processing"""
        try:
            engine = sql.create_engine(self.database_connection_url)
            with engine.connect() as connection:
                inspector = inspect(connection)
                if not inspector.has_table(model_name):
                    raise DatabaseInfoError(
                        f"Table not found for the provided table name: {model_name}."
                    )
                columns = inspector.get_columns(model_name)

            engine.dispose()
            return columns
        except DatabaseInfoError as ex:
            raise Exception(
                f"Table not found for the provided table name: {model_name}."
            )
        except OperationalError as ex:
            raise Exception(
                f"Database not found for the provided database name: {self.database_name}"
            )
        except sqlalchemy.exc.OperationalError as ex:
            raise Exception(
                f"password authentication failed for user: {self._user}",
                {"status_code": 403},
            )
        except Exception as ex:
            raise Exception(
                f"Database not found for the provided database name: {self.database_name}"
            )

    def get_model_permissions(self, model_name: str) -> list:
        """
        Return Table permission for the specific user
        :param model_name:
        :return: list of permission
        """
        query = text(
            f"""SELECT privilege_type FROM information_schema.table_privileges WHERE table_name = '{model_name}' AND grantee = '{self._user}'"""
        )
        try:
            engine = sql.create_engine(self.database_connection_url)
            with engine.connect() as connection:
                result = connection.execute(query)
                privileges = [row[0] for row in result.fetchall()]
            engine.dispose()
            return privileges
        except DatabaseInfoError as ex:
            raise Exception(
                f"Table not found for the provided table name: {model_name}."
            )
        except OperationalError as ex:
            raise Exception(
                f"Database not found for the provided database name: {self.database_name}"
            )
        except sqlalchemy.exc.OperationalError as ex:
            raise Exception(
                f"password authentication failed for user: {self._user}",
                {"status_code": 403},
            )
        except Exception as ex:
            raise Exception(
                f"Database not found for the provided database name: {self.database_name}"
            )
