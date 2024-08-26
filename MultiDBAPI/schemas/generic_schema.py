from pydantic.main import create_model
from config.db import DbConfig


class Config:
    orm_mode = True
    allow_population_by_field_name = True
    arbitrary_types_allowed = True


class CustomDerivedSchemaFactory:
    """
    Factory to generate custom database schema.
    """

    __instance = None
    custom_schema_dict = {}
    schema = {}

    def __new__(cls):
        """
        Singleton: Return Single Unique Instance
        """

        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_custom_derived_model(cls, class_name: str):
        """
        Returns a Custom Base Schema:

        If the class name is not found in the `custom_schema_dict` dictionary,
        it generates a custom derived schema and add it to the `custom_schema_dict`.
        Finally, it returns schema from the `custom_schema_dict`.
        """

        class_name = "_".join(class_name.split("-"))

        if not cls.custom_schema_dict.get(class_name):
            cls.custom_schema_dict.update(
                {class_name: cls.custom_derived_model(class_name.lower())}
            )
        return cls.custom_schema_dict.get(class_name)

    @classmethod
    def custom_derived_model(cls, model_name: str):
        """
        Generate and Return Custom Model
        """
        table_info = cls.get_table_info(model_name)
        model = create_model("model_name", **table_info)
        model.Config = Config
        return model

    @classmethod
    def get_table_info(cls, tablename: str):
        """
        Get and Return Table Information from Database after processing
        """
        try:
            columns = DbConfig().get_db_columns(tablename)
            schema_fields = cls.get_schema_fields_dict(columns)
            return schema_fields
        except Exception:
            raise

    @staticmethod
    def get_schema_fields_dict(columns):
        """
        Return Schema Field Information as Python Dictionary
        """
        return {
            column["name"]: (column["type"].python_type, None)
            for column in columns
            if column["name"] not in ["id"]
        }

    @classmethod
    def get_schema(cls, table_name):
        """Get Table Schema from Database"""
        if not cls.schema.get(table_name):
            schema = cls.get_table_info(table_name)
            cls.convert_values_to_type(schema, str)
            cls.schema.update({table_name: schema})
        return cls.schema.get(table_name)

    @staticmethod
    def convert_values_to_type(dictionary: dict, new_type: type):
        """Convert Values to Type"""
        for key, value in dictionary.items():
            dictionary[key] = new_type(value[0].__name__)
        return dictionary
