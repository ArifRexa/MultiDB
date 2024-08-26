from sqlalchemy import Column, Integer
from config.db import DbConfig
from models.models import Base, Model


class CustomDerivedModelFactory:
    """
    Factory to generate custom database models.
    """

    __instance = None
    custom_model_dict = {}

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
        Returns a Custom Base Model:

        If the class name is not found in the `custom_model_dict` dictionary,
        it generates a custom derived Model and adds it to the `custom_model_dict` with it's user permission.
        Finally, it returns the model from the `custom_model_dict`.
        """
        class_name = "_".join(class_name.split("-"))
        if not cls.custom_model_dict.get(class_name):
            cls.custom_model_dict.update(
                {class_name: cls.custom_derived_model(class_name.lower())}
            )
        return cls.custom_model_dict.get(class_name)

    @classmethod
    def custom_derived_model(cls, model_name: str):
        """Generate and Return Custom Model"""
        table_info = cls.get_table_info(model_name)
        bases = (
            Base,
            Model,
        )
        attrs = {
            "__tablename__": model_name,
            "__table_args__": {"extend_existing": True},
            "id": Column(Integer, primary_key=True),
        }
        attrs.update(table_info)
        return type(model_name, bases, attrs)

    @classmethod
    def get_table_info(cls, tablename: str):
        """Get and Return Table Information from Database after processing"""
        try:
            columns = DbConfig().get_db_columns(tablename)
            model_fields = cls.get_model_fields_dict(columns)
            return model_fields
        except Exception:
            raise

    @staticmethod
    def get_model_fields_dict(columns):
        """Return Model Field Information as Python Dictionary"""
        return {
            column["name"]: Column(type(column["type"]), nullable=True)
            for column in columns
            if column["name"] not in ["id"]
        }
