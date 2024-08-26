import logging
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.exc import MultipleResultsFound, OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
from config.db import DbConfig
from services.dynamic_filter import DynamicFilter

Base = declarative_base()


class Model:
    """
    Base model for CRUD methods. All database models would extend this model

    methods:

    - get_all_objects:      Retrieve objects from the table using the Dynamic Filter.
    - create:               Create a new object and store it in the database.
    - get_or_create:        Retrieve an object from the database or create a new one if not found.
    - bulk_create:          Retrieve objects from the database or create new if not found.
    - get_single_object:    Retrieve a single object from the database based on provided criteria.
    - update:               Update the attributes of the object in the database.
    - delete:               Delete the object from the database.

    """

    @classmethod
    def get_all_objects(cls, **kwargs):
        """
        Retrieve data from the table using the Dynamic Filter.

        Parameters:
            kwargs: Additional keyword arguments to filter the query (e.g., filters, sorting).

        Returns:
            List: A list of objects retrieved from the table.
        """

        try:
            engine = create_engine(
                DbConfig().database_connection_url,
                pool_size=100,
                max_overflow=0,
                connect_args={"connect_timeout": 60},
                echo=True,
            )

            with sessionmaker(
                bind=engine, expire_on_commit=True, autoflush=False
            )() as database_session:
                query_result = DynamicFilter(
                    cls, session=database_session, query=kwargs
                )
                result, count, page = query_result.search()
                result = page.all()

            engine.dispose()
            return result
        except OperationalError as ex:
            raise ex
        except Exception as ex:
            logging.error(f"Exception from {cls.get_all_objects.__name__} :  {ex}")
            raise Exception(str(ex)) from ex

    @classmethod
    def create(cls, engine=None, **kwargs):
        """
        Create a new object and store it in the database.

        This method creates a new object based on the provided keyword arguments and saves it to the database.

        Parameters:
            engine (optional): An engine for connecting to the database.
            **kwargs: Additional keyword arguments representing the attributes of the object.

        Returns:
            The newly created object.
        """
        try:
            instance = cls(**kwargs)

            if engine is None:
                engine = create_engine(
                    DbConfig().database_connection_url,
                    pool_size=100,
                    max_overflow=0,
                    connect_args={"connect_timeout": 60},
                )

            with sessionmaker(
                bind=engine, expire_on_commit=True, autoflush=False
            )() as database_session:
                database_session.add(instance)
                database_session.commit()
                instance = database_session.query(cls).filter_by(**kwargs).one_or_none()

            engine.dispose()
            return instance

        except MultipleResultsFound:
            instance = cls.db_session.query(cls).filter_by(**kwargs)[0]
            cls.db_session.close()
            return instance

        except OperationalError as ex:
            raise Exception(f"Database not found for the provided database name")
        except Exception as ex:
            logging.error(f"Exception from {cls.create.__name__}: {ex}")
            raise ex

    @classmethod
    def get_or_create(cls, **kwargs):
        """
        Retrieve an object from the database or create a new one if not found.

        This method retrieves an object from the database based on the provided keyword arguments. If the object is found,
        it is returned. If not found, a new object is created using the provided keyword arguments and saved to the database.

        Parameters:
            **kwargs: Keyword arguments representing the attributes used to query the object.

        Returns:
            Tuple: object instance
        """
        try:
            kwarg_string = {
                key: kwargs[key] for key, value in kwargs.items() if value is not None
            }

            engine = create_engine(
                DbConfig().database_connection_url,
                pool_size=100,
                max_overflow=0,
                connect_args={"connect_timeout": 60},
            )

            with sessionmaker(
                bind=engine, expire_on_commit=True, autoflush=False
            )() as database_session:
                try:
                    instance = (
                        database_session.query(cls)
                        .filter_by(**kwarg_string)
                        .one_or_none()
                    )
                except MultipleResultsFound:
                    instance = database_session.query(cls).filter_by(**kwarg_string)[0]

            if instance:
                engine.dispose()
                return instance, True

            instance = cls.create(**kwarg_string)
            engine.dispose()
            return instance, False

        except OperationalError as ex:
            raise Exception(f"Database not found for the provided database name")
        except Exception as ex:
            logging.error(f"Exception from { cls.get_or_create.__name__ }: {ex}")
            raise ex

    @classmethod
    def get_or_create_bulk(cls, data_list):
        """
        Retrieve existing objects from the database or create new ones if not found.

        This method retrieves objects from the database based on the provided list of dictionaries.
        If an object is found, it is returned. If not found, a new object is created using the dictionary's attributes
        and saved to the database.

        Parameters:
            data_list (list of dictionaries): List of dictionaries where each dictionary represents attributes used to query
            the object.

        Returns:
            List of tuples: [(object instance, created), ...]
        """
        try:
            engine = create_engine(
                DbConfig().database_connection_url,
                pool_size=100,
                max_overflow=0,
                connect_args={"connect_timeout": 120},
            )

            instances = []
            created_flags = []
            failed_instance = []

            with sessionmaker(
                bind=engine, expire_on_commit=True, autoflush=False
            )() as database_session:
                for data in data_list:
                    kwarg_string = {
                        key: value for key, value in data.items() if value is not None
                    }
                    try:
                        instance = (
                            database_session.query(cls)
                            .filter_by(**kwarg_string)
                            .one_or_none()
                        )
                        if instance:
                            instances.append(instance)
                            created_flags.append(True)
                        else:
                            new_instance = cls.create(engine=engine, **kwarg_string)
                            instances.append(new_instance)
                            created_flags.append(False)

                    except Exception as ex:
                        logging.error(f"Error while processing data: {ex}")
                        failed_instance.append(
                            {"Error": ex.args[0], "data": kwarg_string}
                        )
                        continue

            engine.dispose()
            # return list(zip(instances, created_flags))
            return instances, failed_instance

        except OperationalError as ex:
            raise Exception(f"Database not found for the provided database name")
        except Exception as ex:
            logging.error(f"Exception from {cls.get_or_create_bulk.__name__}: {ex}")
            raise ex

    @classmethod
    def get_single_object(cls, **kwargs):
        """
        Retrieve a single object from the database based on provided criteria.

        This method retrieves a single object from the database based on the provided keyword arguments. The keyword
        arguments are used to filter the query and find the matching object. If multiple objects match the criteria,
        only the first object is returned.

        Parameters:
            **kwargs: Keyword arguments representing the criteria to filter the query.

        Returns:
            The retrieved object or None if no matching object is found.
        """

        try:
            filter_string = {
                key: kwargs[key] for key, value in kwargs.items() if value is not None
            }

            engine = create_engine(
                DbConfig().database_connection_url,
                pool_size=100,
                max_overflow=0,
                connect_args={"connect_timeout": 60},
            )

            with sessionmaker(
                bind=engine, expire_on_commit=True, autoflush=False
            )() as database_session:
                instance = (
                    database_session.query(cls).filter_by(**filter_string).one_or_none()
                )
                session = database_session

            engine.dispose()
            return instance, session

        except MultipleResultsFound:
            return (
                database_session.query(cls).filter_by(**filter_string).first(),
                database_session,
            )
        except OperationalError as ex:
            raise Exception(f"Database not found for the provided database name")
        except Exception as ex:
            logging.error(f"Exception from {cls.get_single_object.__name__}:  {ex}")
            raise Exception(str(ex)) from ex

    @classmethod
    def get_count(cls, **kwargs):
        """
        Retrieve number of rows count from the table using the Dynamic Filter.

        Parameters:
            kwargs: Additional keyword arguments to filter the query (e.g., filters, sorting).

        Returns:
            Integer: Number of the rows from the table.
        """

        try:
            engine = create_engine(
                DbConfig().database_connection_url,
                pool_size=100,
                max_overflow=0,
                connect_args={"connect_timeout": 60},
            )

            with sessionmaker(
                bind=engine, expire_on_commit=True, autoflush=False
            )() as database_session:
                query_result = DynamicFilter(
                    cls, session=database_session, query=kwargs
                )
                result, count, page = query_result.search()
                # result = page.all()

            engine.dispose()
            return count

        except OperationalError as ex:
            raise Exception(f"Database not found for the provided database name")
        except Exception as ex:
            logging.error(f"Exception from {cls.get_count.__name__} :  {ex}")
            raise Exception(str(ex)) from ex

    def update(self, session, **kwargs):
        """
        Update the attributes of the object in the database.

        This method updates the attributes of the object with the provided keyword arguments and saves the changes to
        the database using the provided session.

        Parameters:
            session: The sqlalchemy session used for the update operation.
            **kwargs: Keyword arguments representing the attributes to be updated.
        """
        try:
            for key in kwargs:
                if kwargs[key] is not None and hasattr(self, key):
                    setattr(self, key, kwargs[key])
            session.add(self)
            session.commit()

            return self.__class__.get_single_object(id=self.id)
        except MultipleResultsFound as ex:
            logging.error(f"Exception from {self.update.__name__}: {ex}")
            session.rollback()
            raise ex
        finally:
            session.close()

    def delete(self, session):
        """Delete the object from the database.

        This method deletes the object from the database using the provided session.

        Parameters:
            session: The sqlalchemy session used for the deletion.
        """
        try:
            session.delete(self)
            session.commit()
            session.close()
        except OperationalError as ex:
            raise Exception(f"Database not found for the provided database name")
        except MultipleResultsFound as ex:
            logging.error(f"Exception from {self.delete.__name__} : {ex}")
            raise ex


class User(Base, Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False, unique=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False, unique=False)

    def check_password(self, plain_text_pass):
        # salt = PASSWORD_SALT
        # input_hash = hashlib.sha512(
        #     plain_text_pass.encode("utf-8") + salt.encode("utf-8")
        # ).hexdigest()
        # return self.password == input_hash
        pass

    @property
    def get_refresh_token(self):
        # payload = dict(
        #     uid=self.id,
        #     exp=datetime.datetime.utcnow()
        #     + timedelta(hours=JWT_SETTINGS.get("refresh_token_lifetime")),
        #     type="refresh_token",
        # )
        # return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        pass

    def __repr__(self):
        return f"{self.full_name} [ {self.email} ]"
