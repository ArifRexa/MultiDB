from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal


class Serialiazer(ABC):
    @abstractmethod
    def run_serializer(self):
        pass


class GenericSerializer(Serialiazer):
    def __init__(self, object, many=False):
        self.object = object
        self.many = many

    def run_serializer(self):
        try:
            data = []
            if self.many:
                for obj in self.object:
                    data.append(self.serialize(obj))
            else:
                data.append(self.serialize(self.object))
            return data
        except Exception as ex:
            raise Exception(f"Error occurred from run serializer: {str(ex)}")

    def serialize(self, obj):
        try:
            cols = self.get_columns(obj)
            obj_dict = {}
            for field in cols:
                if not field.startswith("_"):
                    data = getattr(obj, field, None)
                    data = self.convert_data(data)
                    obj_dict[field] = data
            return obj_dict
        except Exception as ex:
            raise Exception(f"Error encountered from serializer: {str(ex)}")

    def convert_data(self, data):
        data_type = type(data)
        if data_type == date:
            return data.isoformat()
        elif data_type == datetime:
            return data.isoformat()
        elif data_type == Decimal:
            return float(data)
        # Add more data type checks and conversion methods as needed
        return data

    def get_columns(self, obj):
        try:
            return vars(obj)
        except Exception as ex:
            raise Exception(f"Error encountered from get_columns: {str(ex)}")

    @property
    def data(self):
        if hasattr(self, "_data"):
            return getattr(self, "_data")
        else:
            self.data = self.run_serializer()
            return self._data

    @data.setter
    def data(self, value):
        setattr(self, "_data", value)
