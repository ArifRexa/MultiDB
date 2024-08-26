"""
    DynamicFilter
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import logging

from sqlalchemy import and_, asc, desc, or_
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql.schema import Table

""" Valid operators """
OPERATORS = {
    "like": lambda f, a: f.like(a),
    "equals": lambda f, a: f == a,
    "is_null": lambda f, a: f.is_(None) if a == "True" else f.isnot(None),
    "gt": lambda f, a: f > a,
    "gte": lambda f, a: f >= a,
    "lt": lambda f, a: f < a,
    "lte": lambda f, a: f <= a,
    "in": lambda f, a: f.in_(a),
    "not_in": lambda f, a: ~f.in_(a),
    "not_equal_to": lambda f, a: f != a,
}


class OperatorNotFound(Exception):
    pass


class DynamicFilter:
    def __init__(self, model, session, query, enabled_fields=None, page_size=10):
        """Initializator of the class 'DynamicFilter'"""
        self.model = model
        self.query = self.query_to_kwargs(query)
        self.model_query = session.query(model)
        self.enabled_fields = enabled_fields
        self.page_size = page_size

    def search(self):
        filters = self.query
        result = self.model_query
        keys = filters.keys()
        count = 0

        if "or_and" in keys:
            result = self.or_and_perser(filters["or_and"])
            filters.pop("or_and")
            logging.info(filters)
        if "filter" in keys:
            result = self.parse_filter(filters["filter"])
        if "sort" in keys:
            result = result.order_by(*self.sort(filters["sort"]))
        count = result.count()
        page = self.page(
            result, filters.get("offset", None), filters.get("limit", None)
        )
        return result, count, page

    def page(self, query, offset, limit):
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query

    def parse_filter(self, filters):
        """This method process the filters"""
        try:
            for filter_type, filter_value in filters.items():
                if filter_type in ["or", "and"]:
                    conditions = []
                    for field in filters[filter_type]:
                        if self.is_field_allowed(field):
                            conditions.extend(
                                self.create_query(attr)
                                for attr in self.parse_field(field, filter_value[field])
                            )

                    if filter_type == "or":
                        self.model_query = self.model_query.filter(or_(*conditions))
                    elif filter_type == "and":
                        self.model_query = self.model_query.filter(and_(*conditions))
        except OperatorNotFound:
            return self.model_query
        return self.model_query

    def parse_field(self, field, field_value):
        """Taking field names and their value"""
        if type(field_value) is dict:
            operators = list(field_value)
            for operator in operators:
                if self.verify_operator(operator) is False:
                    raise OperatorNotFound()
                value = field_value[operator]
                if value == "":
                    for i in range(2):
                        if i == 0:
                            yield field, operator, ""
                        yield field, operator, "-1"
                else:
                    yield field, operator, value
        elif type(field_value) is str:
            operator = "equals"
            value = field_value
        else:
            raise OperatorNotFound()
        yield field, operator, value

    @staticmethod
    def verify_operator(operator):
        """Verify if the operator is valid"""
        try:
            return bool(hasattr(OPERATORS[operator], "__call__"))
        except (ValueError, KeyError):
            return False

    def is_field_allowed(self, field):
        return field in self.enabled_fields if self.enabled_fields else True

    def create_query(self, attr):
        """Mix all values and make the query"""
        field = attr[0]
        operator = attr[1]
        value = attr[2]
        model = self.model

        if "." in field:
            field_items = field.split(".")
            attr = None

            for field_item in field_items:
                attr = getattr(model, field_item, None)
                if isinstance(attr.property, RelationshipProperty):
                    model = attr.property.mapper.class_
                    secondary = attr.property.secondary
                    if isinstance(secondary, Table):
                        self.model_query = self.model_query.join(secondary)
                    self.model_query = self.model_query.join(model)
                else:
                    break

            return OPERATORS[operator](attr, value)

        return OPERATORS[operator](getattr(model, field, None), value)

    def make_or_query(self, filter_dict: dict):
        for key, value in filter_dict["or_conditions"].items():
            if key[-4:] == "_not" and hasattr(self.model, key[:-4]):
                if any(value):
                    value = list(filter(None, value))
                    # yield  getattr(self.model, key[:-4], None).in_(value)
                    #     else:
                    #         yield getattr(self.model, key[:-4],None).isnot_(None)

                yield getattr(self.model, key[:-4], None).in_(value)
            else:
                yield getattr(self.model, key, None).in_(value)

    def or_and_perser(self, filter_dict):
        and_conditions = None
        if not filter_dict.get("and_conditions"):
            filter_dict.update({"and_conditions": {}})
            and_conditions = True

        if not filter_dict.get("or_conditions"):
            filter_dict.update({"or_conditions": {}})

        # Build the OR conditions
        or_conditions = or_(
            *[
                getattr(self.model, key, None).in_(value)
                if value not in ["null", "not_null"] and hasattr(self.model, key)
                else self.null_parser(key, value)
                for key, value in filter_dict["or_conditions"].items()
            ]
        )

        # Build the AND conditions
        and_conditions = (
            True
            if and_conditions
            else and_(
                getattr(self.model, key, None) == value
                for key, value in filter_dict["and_conditions"].items()
                if hasattr(self.model, key)
            )
        )
        logging.info(filter_dict)

        # Combine the AND and OR conditions
        combined_conditions = and_(and_conditions, or_conditions)

        # Build the query
        self.model_query = self.model_query.filter(combined_conditions)
        return self.model_query

    def null_parser(self, key, value):
        if value == "null":
            logging.info("Get null as field value")
            return or_(
                getattr(self.model, key, None) == "", getattr(self.model, key) is None
            )
        elif value == "not_null":
            logging.info("Get not_null as field value")
            return getattr(self.model, key) != ""

    def sort(self, sort):
        """Sort"""
        order = []
        for field, direction in sort.items():
            if direction == "asc":
                order.append(asc(getattr(self.model, field, None)))
            elif direction == "desc":
                order.append(desc(getattr(self.model, field, None)))
        return order

    def update_dict(self, d: dict, keys: list, values: list):
        if len(keys) == 1:
            d[keys[0]] = values[0]
        else:
            key = keys[0]
            if key not in d:
                d[key] = {}
            self.update_dict(d[key], keys[1:], values)

    def substitute_null(self, value: list):
        logging.info(value)
        for i in range(len(value)):
            if value[i] in ["null", "not_null"]:
                value[i] = ""
                value.append(None)
                return value

    def query_to_kwargs(self, query: dict):
        """Convert Query Parameters to kwargs dictionary"""
        try:
            kwargs = {}
            page = query.get("page", None)
            limit = query.get("limit", None)
            if page and limit and int(page[0]) > 0:
                offset = str((int(page[0]) - 1) * int(limit[0]))
                query["offset"] = [offset]
                query.pop("page")
            elif page and not limit and int(page[0]) > 0:
                offset = str((int(page[0]) - 1) * int(10))
                query["offset"] = [offset]
                query["limit"] = [10]
                query.pop("page")

            for key, value in query.items():
                if key == "limit":
                    kwargs[key] = value[0]
                elif key == "offset":
                    kwargs[key] = value[0]
                elif key == "sort":
                    if value[0].endswith("__desc") or value[0].endswith("__asc"):
                        sort_key, sort_order = value[0].rsplit("__", 1)
                        kwargs.setdefault("sort", {})[sort_key] = sort_order
                else:
                    if key.startswith("or__"):
                        key = key[4:]
                        if len(key.split("__")) == 1:
                            value = self.substitute_null(value[0].split(","))
                            kwargs.setdefault("or_and", {}).setdefault(
                                "or_conditions", {}
                            )[key] = value
                        else:
                            keys = key.split("__")
                            self.update_dict(
                                kwargs.setdefault("filter", {}).setdefault("or", {}),
                                keys,
                                value,
                            )
                    else:
                        if len(key.split("__")) == 1:
                            kwargs.setdefault("filter", {}).setdefault("and", {})[
                                key
                            ] = value[0]
                        else:
                            if value[0] == "null":
                                value[0] = ""
                            keys = key.split("__")
                            self.update_dict(
                                kwargs.setdefault("filter", {}).setdefault("and", {}),
                                keys,
                                value,
                            )

            # logging.info(f"kwargs : {kwargs}")
            return kwargs
        except Exception as e:
            logging.error(f"Exception occurred {self.query_to_kwargs.__name__}: {e}")
