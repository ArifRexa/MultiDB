import json
from datetime import date, datetime
from serializers.serializers import Serialiazer


class ModelSerializer(Serialiazer):
    def __init__(self, object, many=False):
        self.object = object
        self.many = many

    def run_serializer(self):
        try:
            data = []
            if self.many:
                # if not isinstance(self.object, list):
                #     raise TypeError(
                #         f"many=True, Expecting a list of objects but got , {type(self.object)} type object"
                #     )
                for obj in self.object:
                    print(self.serialize(obj))
                    data.append(self.serialize(obj))
            else:
                data = self.serialize(self.object)
            return data
            # if len(self.data) == 1:
            #     self.data = self.data[0]
        except Exception as ex:
            # print("Exception happend >> ", self.__init__.__name__)
            # print("ERR: ", str(ex))
            raise Exception(str(ex))

    def serialize(self, obj):
        try:
            print(type(obj), type(self.Meta.model))
            # if not isinstance(type(obj), self.Meta.model):
            #     raise TypeError(
            #         f"serializer expecting {self.Meta.model} object but got {type(obj)}"
            #     )

            cols = self.get_columns(obj)
            print(cols)

            exclude = []
            if hasattr(self.Meta, "exclude"):
                exclude = getattr(self.Meta, "exclude")

            obj_dict = dict()

            for field in cols:
                if (
                    not field.startswith("_")
                    and field != "metadata"
                    and field not in exclude
                ):
                    print(field)
                    data = getattr(obj, field, None)

                    if isinstance(data, date) or isinstance(data, datetime):
                        data = data.isoformat()

                    json.dumps(data)
                    obj_dict[field] = data
            return obj_dict
        except Exception as ex:
            raise Exception(str(ex))

    def get_columns(self, obj):
        try:
            fields = getattr(self.Meta, "fields", None)
            if fields is not None and fields != "__all__":
                return self.Meta.fields
            else:
                return vars(obj)
        except Exception as ex:
            raise Exception(str(ex))

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


# From here every Serializer is for usage.
# Don't call ModelSerializer from above to anywhere.
# Just Extends ModelSerializer and made new one like below.


# TODO For Sample : Need to Remove

# class ProspectEmailSerializer(ModelSerializer):
#     class Meta:
#         model = ProspectEmail
#         fields = "__all__"
