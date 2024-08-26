import logging
from blacksheep import Application, Request
from blacksheep.server.authorization import Policy, auth
from blacksheep.server.controllers import Controller
from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Info
from pydantic import BaseModel

from config.authenticator import CentralAuthHandler
from config.log_config import handler
from config.settings import DOCS_DESCRIPTION, SECRET_KEY
from helpers.response import make_response
from middlewares.middlewares import DBGenerationMiddleware, UrlVerificationMiddleware
from models import CustomDerivedModelFactory
from schemas import CustomDerivedSchemaFactory
from serializers import serializers
from exceptions.exception_handler import handle_exception

app = Application()
app.middlewares.extend([UrlVerificationMiddleware(), DBGenerationMiddleware()])
app.use_sessions(SECRET_KEY)
docs = OpenAPIHandler(
    info=Info(
        title="Centralize Dynamic API for Database ",
        version="0.1.0",
        description=DOCS_DESCRIPTION,
    )
)
docs.bind_app(app)

get = app.router.get
post = app.router.post
patch = app.router.patch
delete = app.router.delete

app.use_authentication().add(CentralAuthHandler())
authorization = app.use_authorization()
Authenticated = "authenticated"
authorization += Policy(Authenticated)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


class DatabaseInfo(BaseModel):
    database_name: str
    table_name: str
    username: str
    password: str


class GetRequestSchema(BaseModel):
    database_info: DatabaseInfo


class Generic_Request_Handler(Controller):
    @auth(Authenticated)
    @post("/get")
    async def get(self, request: Request, payload: GetRequestSchema):
        """This Request Handler handles the retrieval of existing resources."""

        try:
            payload = await request.json()

            #   Generate Custom Derived Model
            #   Get Object or Create Object
            table_name = payload.get("database_info", {}).get("table_name")

            DerivedModel = CustomDerivedModelFactory.get_custom_derived_model(
                table_name.capitalize()
            )

            query = request.query
            data = DerivedModel.get_all_objects(**query)

            #   Generate Custom Derived Model
            #   Get Object or Create Object
            serializer = serializers.GenericSerializer(data, many=True)
            serialized_data = serializer.data

            return make_response(status=200, data=serialized_data)

        except Exception as ex:
            logging.error(f"Exception happened from PATCH view function : {ex}")
            return handle_exception(ex=ex, payload=payload)

    @auth(Authenticated)
    @post("/create")
    async def create(self, request: Request, payload: GetRequestSchema):
        """This Request Handler handles the creation of new resources."""
        try:
            payload = await request.json()

            #   Generate Custom Derived Schema
            #   Validate and Structure Payload Through Schema
            table_name = payload.get("database_info", {}).get("table_name")

            DerivedSchema = CustomDerivedSchemaFactory.get_custom_derived_model(
                table_name.capitalize()
            )
            data_payload = payload.get("data")
            if not data_payload:
                raise Exception("Data payload is empty")

            data_payload = DerivedSchema(**data_payload)

            #   Generate Custom Derived Model
            #   Get Object or Create Object
            DerivedModel = CustomDerivedModelFactory.get_custom_derived_model(
                table_name.capitalize()
            )

            obj, already_exist = DerivedModel.get_or_create(**data_payload.dict())

            #   Serialized Object Data
            serializer = serializers.GenericSerializer(obj)
            serialized_data = serializer.data

            return make_response(status=201, data=serialized_data)

        except Exception as ex:
            logging.error(f"Exception happened from PATCH view function : {ex}")

            return handle_exception(ex=ex, payload=payload)

    @auth(Authenticated)
    @post("/bulk/create")
    async def bulk_create(self, request: Request, payload: GetRequestSchema):
        """This Request Handler handles the bulk creation of new resources for list of dict."""
        try:
            payload = await request.json()

            #   Generate Custom Derived Schema
            #   Validate annd Structure Payload Through Schema
            table_name = payload.get("database_info", {}).get("table_name")

            DerivedSchema = CustomDerivedSchemaFactory.get_custom_derived_model(
                table_name.capitalize()
            )
            data_payload = payload.get("data")
            if not data_payload:
                raise Exception("Data payload is empty")
            list_of_data_payload = []
            for data in data_payload:
                list_of_data_payload.append(DerivedSchema(**data))

            #   Generate Custom Derived Model
            #   Get Object or Create Object
            DerivedModel = CustomDerivedModelFactory.get_custom_derived_model(
                table_name.capitalize()
            )
            obj, failed_instances = DerivedModel.get_or_create_bulk(data_payload)
            #   Serialized Object Data
            serializer = serializers.GenericSerializer(obj, many=True)
            serialized_data = serializer.data

            return make_response(status=201, data=serialized_data + failed_instances)

        except Exception as ex:
            logging.error(f"Exception happened from PATCH view function : {ex}")

            return handle_exception(ex=ex, payload=payload)

    @auth(Authenticated)
    @patch("/update/{id}")
    async def update(self, request: Request, id: str, payload: GetRequestSchema):
        """This Request Handler handles the updating of existing resources."""
        try:
            payload = await request.json()

            #   Generate Custom Derived Schema
            #   Validate annd Structure Payload Through Schema
            table_name = payload.get("database_info", {}).get("table_name")

            DerivedSchema = CustomDerivedSchemaFactory.get_custom_derived_model(
                table_name.capitalize()
            )
            data_payload = payload.get("data")
            if not data_payload:
                raise Exception("Data payload is empty")

            data_payload = DerivedSchema(**data_payload)

            #   Generate Custom Derived Model
            #   Get Object then Update Object
            DerivedModel = CustomDerivedModelFactory.get_custom_derived_model(
                table_name.capitalize()
            )
            obj, session = DerivedModel.get_single_object(id=id)

            #   Return 400 If No object Found
            if not obj:
                return make_response(
                    status=400, data="No matching data found for the specified id."
                )

            obj.update(session, **data_payload.dict())

            #   Serialize Object Data
            serializer = serializers.GenericSerializer(obj)
            serialized_data = serializer.data

            return make_response(status=202, data=serialized_data)

        except Exception as ex:
            logging.error(f"Exception happened from PATCH view function : {ex}")

            return handle_exception(ex=ex, payload=payload)

    @auth(Authenticated)
    @delete("/delete/{id}")
    async def delete(self, request: Request, id: str, payload: GetRequestSchema):
        """This Request Handler handles the deletion of existing resources."""

        try:
            payload = await request.json()

            #   Generate Custom Derived Model
            #   Get Object then Delete Object
            table_name = payload.get("database_info", {}).get("table_name")

            DerivedModel = CustomDerivedModelFactory.get_custom_derived_model(
                table_name.capitalize()
            )

            obj, session = DerivedModel.get_single_object(id=id)

            #   Return 400 If No object Found
            if not obj:
                return make_response(
                    status=400, data="No matching data found for the specified id."
                )

            obj.delete(session)

            return make_response(status=202, data="Object deleted successfully.")
        except Exception as ex:
            logging.error(f"Exception happened from PATCH view function : {ex}")
            return handle_exception(ex=ex, payload=payload)


class Schema(Controller):
    @auth(Authenticated)
    @post("/schema")
    async def get_table_schema(self, request: Request, payload: GetRequestSchema):
        """This Request Handler will return schema of given table"""
        try:
            payload = await request.json()

            table_name = payload.get("database_info", {}).get("table_name")

            schema = CustomDerivedSchemaFactory.get_schema(table_name.lower())

            return make_response(status=200, data=schema)

        except Exception as ex:
            logging.error(f"Exception happened from PATCH view function : {ex}")

            return handle_exception(ex=ex, payload=payload)


class MetaData(Controller):
    @auth(Authenticated)
    @post("/get_count_rows")
    async def get_count_rows(self, request: Request, payload: GetRequestSchema):
        """This Request Handler will return number rows of given table"""
        try:
            payload = await request.json()

            #   Generate Custom Derived Model
            #   Get Object or Create Object
            table_name = payload.get("database_info", {}).get("table_name")

            DerivedModel = CustomDerivedModelFactory.get_custom_derived_model(
                table_name.capitalize()
            )
            query = request.query
            data = DerivedModel.get_count(**query)

            return make_response(status=200, data={"count": data})
        except Exception as ex:
            logging.error(f"Exception happened from Get Count view function : {ex}")
            return handle_exception(ex=ex, payload=payload)


if __name__ == "__main__":
    app.start()
