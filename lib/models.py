#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Models for MtgCollector
"""

import abc
import flask
import datetime
import typing

from lib.exceptions import IntegrityException
from lib.db import sql_commands as sql


class Model(metaclass=abc.ABCMeta):
    """
    Abstract class representing a model used in an application. Allows for an ORM view of the used objects
    """
    @classmethod
    @abc.abstractmethod
    def table_creation_command(cls) -> str:
        """ Defines the sql command used to create the table for the model """

    @classmethod
    @abc.abstractmethod
    def insertion_command(cls) -> str:
        """ Saves the current object to the database. Should return the same user """

    @property
    @abc.abstractmethod
    def as_database_object(self) -> dict:
        """ Returns the object as it should be when inserting it in the database as a dict"""

    @property
    @abc.abstractmethod
    def primary_key(self) -> dict:
        """ This is a value that can uniquely identify any object (primary key) """

    @classmethod
    def bulk_insert(cls, models: typing.List, connection=None) -> None:
        """
        Inserts many models into the database

        :param models: list of models to insert. They have to be all of the same type
        :param connection: the database connection to use. If None, will use flask.g.db
        """
        chunk_size = 2500  # magic number for the size of the query. This works, no idea why
        if connection is None:
            connection = getattr(flask.g, "db")
        cursor = connection.cursor()
        # TODO check if list(models) is a performance killer
        chunks = [list(models)[i:i+chunk_size] for i in range(0, len(models), chunk_size)]

        for chunk in chunks:
            cursor.executemany(cls.insertion_command(), [model.as_database_object for model in chunk])
        connection.commit()

    @classmethod
    def _get(cls, command: str, connection=None, **kwargs) -> typing.List:
        """
        Retrieves data from the database

        :param command: the sql command used to retrieve data
        :param connection: the database connection to use. If None , will use flask.g.db
        :param kwargs: additional arguments to add to the prepared sql statement
        :return: all retrieved values
        """
        cursor, _ = cls.__execute(command, connection, **kwargs)
        return cursor.fetchall()

    @classmethod
    def create_table(cls, connection=None) -> None:
        """
        Creates the table to be used with this model

        :param connection: the database connection to use. If None, will use flask.g.db
        """
        cls.__execute(cls.table_creation_command(), connection)

    def save(self, connection=None):
        """
        Insert the model into the database

        :param connection: the database connection to use. If None, will use flask.g.db
        :return: the last id inserted
        """
        return self._modify(self.insertion_command(), connection, **self.as_database_object)

    @classmethod
    def __execute(cls, command: str, connection=None, **kwargs):
        if connection is None:
            connection = getattr(flask.g, "db")
        cursor = connection.cursor(dictionary=True)
        cursor.execute(command, kwargs)
        return cursor, connection

    @classmethod
    def _modify(cls, command: str, connection=None, **kwargs) -> int:
        cursor, connection = cls.__execute(command, connection, **kwargs)
        connection.commit()
        return cursor.lastrowid

    def __eq__(self, other) -> bool:
        return self.primary_key == other.primary_key

    def __hash__(self):
        return hash(self.primary_key)


class Edition(Model):
    """
    Class representing a MTG Edition
    """
    # noinspection PyPep8Naming,PyShadowingBuiltins
    def __init__(self, type: str, code: str, releaseDate: datetime.datetime, name: str, block: str):
        self.__type = type
        self.__code = code
        self.__releaseDate = releaseDate
        self.__name = name
        self.__block = block

    @classmethod
    def insertion_command(cls) -> str:
        """ The command used to insert an edition in the database """
        return sql.Edition.insert()

    @classmethod
    def table_creation_command(cls) -> str:
        """ The command used to insert values in the database"""
        return sql.Edition.create_table()

    @property
    def as_database_object(self) -> dict:
        """ A dictionary view of the edition """
        return {
            "type": self.__type,
            "code": self.__code,
            "releaseDate": self.__releaseDate,
            "name": self.__name,
            "block": self.__block
        }

    @property
    def primary_key(self):
        """ This is a value allowing to uniquely identify an instance of Edition """
        return self.__code


class Metacard(Model):
    """
    Represents an abstract card, which can span on multiple representation and editions
    """
    # noinspection PyPep8Naming
    def __init__(
            self, name: str, types: typing.Set, subtypes: typing.Set, supertypes: typing.Set, manaCost: str,
            text: str, power: float, toughness: float, colors: typing.List, cmc: float
    ):
        self.__name = name
        self.__types = types
        self.__subtypes = subtypes
        self.__supertypes = supertypes
        self.__manaCost = manaCost
        self.__text = text
        self.__power = power
        self.__toughness = toughness
        self.__colors = colors
        self.__cmc = cmc
        self.__instances = []
        self.__legalities = []

    @classmethod
    def table_creation_command(cls) -> str:
        """ The command to create the metacard table"""
        return sql.Metacard.create_table()

    @classmethod
    def insertion_command(cls) -> str:
        """ The command used to insert a metacard in the database """
        return sql.Metacard.insert()

    @classmethod
    def get_ids_where(cls, card_name="", card_type="", order_by="metacard.name"):
        def add_to_parameters(params, value):
            if params == "":
                params += value
            else:
                params += " AND " + value
            return params

        query_parameters = ""
        kwargs = dict()

        if card_name:
            query_parameters = add_to_parameters(query_parameters, "metacard.name LIKE %(name)s")
            kwargs["name"] = "%" + card_name + "%"

        if card_type:
            query_parameters = add_to_parameters(query_parameters, "metacard.types LIKE %(type)s")
            kwargs["type"] = "%" + card_type + "%"

        query = sql.Metacard.get_ids().format(selection=query_parameters, order=order_by)
        return [value["card_id"] for value in cls._get(query, **kwargs)]

    @property
    def as_database_object(self) -> dict:
        """ A dictionary view of the metacard """
        return {
            "name": self.__name,
            "types": self.__types,
            "subtypes": self.__subtypes,
            "supertypes": self.__supertypes,
            "manaCost": self.__manaCost,
            "text": self.__text,
            "power": self.__power,
            "toughness": self.__toughness,
            "colors": self.__colors,
            "cmc": self.__cmc
        }

    @property
    def primary_key(self):
        """ This is a value allowing to uniquely identify an instance of Metacard """
        return self.__name


class Card(Model):
    """
    A concrete representation of a card
    """
    def __init__(
            self, name: str, rarity: str, number: str, edition: str, artist: str, flavor: str, version: int,
            multiverseid: int=None
    ):
        self.__name = name
        self.__rarity = rarity
        self.__number = number
        self.__edition = edition
        self.__artist = artist
        self.__flavor = flavor
        self.__version = version
        self.__multiverseid = multiverseid

    @classmethod
    def table_creation_command(cls):
        """ The command used to create the card table """
        return sql.Card.create_table()

    @classmethod
    def insertion_command(cls) -> str:
        """ The command used to insert a table in the database """
        return sql.Card.insert()

    @property
    def as_database_object(self) -> dict:
        """ A dictionary view of the card """
        return {
            "multiverseid": self.__multiverseid,
            "name": self.__name,
            "rarity": self.__rarity,
            "number": self.__number,
            "edition": self.__edition,
            "artist": self.__artist,
            "flavor": self.__flavor,
            "version": self.__version
        }

    @property
    def primary_key(self):
        """ This is a value allowing to uniquely identify an instance of Card """
        return self.__name, self.__edition, self.__number, self.__version

    @classmethod
    def get(cls, card_id):
        return cls._get(sql.Card.get(), card_id=card_id)


class Tournament(Model):
    """
    Tournament model

    :param name: the name of the tournament
    """
    def __init__(self, name):
        self.__name = name

    @classmethod
    def insertion_command(cls) -> str:
        """ Command to insert a tournament in the database """
        return sql.Tournament.insert()

    @classmethod
    def table_creation_command(cls) -> str:
        """ Creation command for the tournament table """
        return sql.Tournament.create_table()

    @property
    def as_database_object(self) -> dict:
        """ Dictionary view of a tournament """
        return {
            "name": self.__name
        }

    @property
    def primary_key(self):
        """ This is a value allowing to uniquely identify an instance of Tournament """
        return self.__name


class User(Model):
    """
    User model

    :param username: name of the user
    :param email: email of the user
    :param password: the user password
    :param is_admin: true if the user is an admin
    :param user_id: user's unique identifier
    """
    def __init__(self, username: str, email: str, password: str, is_admin: bool=False, user_id: int=None):
        self.__user_id = user_id
        self.__username = username
        self.__email = email
        self.__password = password
        self.__is_admin = is_admin

    @classmethod
    def insertion_command(cls) -> str:
        """ Command used to insert a user in the database """
        return sql.User.insert()

    @classmethod
    def table_creation_command(cls) -> str:
        """ The command to create the user table """
        return sql.User.create_table()

    @classmethod
    def get_user_by_name_or_mail(cls, identifier: str):
        """
        Checks for a user having the given identifier as name or email and returns it

        :param identifier: the identifier for email or username
        :return: User instance for the given user or None
        """
        data = cls._get(sql.User.get_by_mail_or_username(), identifier=identifier)
        if len(data) == 1:
            return User(**data[0])
        elif len(data) == 0:
            return None
        else:
            # TODO we can make this better
            raise Exception("got multiple users . {}".format(data))

    @classmethod
    def get_user_by_id(cls, user_id: int):
        """
        Fetches a user by id and returns it

        :param user_id: the wanted user id
        :return: User instance or None
        """
        data = cls._get(sql.User.get_by_id(), user_id=user_id)
        if len(data):
            return User(**data[0])

    @classmethod
    def get_users(cls, limit: int=None, offset: int=0) -> list:
        """
        Returns users with a given limit

        :param limit: maximum number of users to return
        :param offset: offset for the search
        :return: list of User
        """
        if limit is not None:
            users = cls._get(sql.User.get_with_limit(), limit=limit, offset=offset)
        else:
            users = cls._get(sql.User.get())
        return [User(**data) for data in users]

    @staticmethod
    def is_active() -> bool:
        """
        Checks whether the user is active

        :return: True as we don't handle blocked accounts
        """
        return True

    @staticmethod
    def is_anonymous() -> bool:
        """
        Checks whether the user is anonymous or not

        :return: False as we only have authenticated users
        """
        return False

    @property
    def is_authenticated(self) -> bool:
        """
        Checks if the user is authenticated

        :return: True as we only create user instance on login
        """
        return True

    @property
    def is_admin(self) -> bool:
        """ Determines if the user is an administrator or not """
        return self.__is_admin

    def get_id(self) -> str:
        """
        :return: the user unique id
        """
        return str(self.__user_id)

    def check_password(self, password: str) -> bool:
        """
        Checks that the user's password is valid

        :param password: password to check against
        :return: True if the password is valid
        """
        return self.__password == password

    def create(self):
        """
        Inserts the given user in the database

        :return: the newly created user
        """
        if User.get_user_by_name_or_mail(self.__email) or User.get_user_by_name_or_mail(self.__username):
            raise IntegrityException()

        new_user_id = self._modify(sql.User.insert(), **self.__as_new_database_object())
        new_user = self.get_user_by_id(new_user_id)
        self.__user_id = new_user.__user_id
        self.__is_admin = new_user.__is_admin
        return self

    def set_admin(self, admin: bool=True) -> None:
        """
        Sets the user identified by user_id to be an admin if admin is True (default)
        Else remove the right of being admin to the user

        :param admin: whether to turn the user as admin or remove him the rights to be
        """
        self._modify(sql.User.set_admin(), user_id=self.get_id(), admin=admin)
        self.__is_admin = admin

    def as_database_object(self) -> dict:
        """ View of the user as a dictionary """
        new = self.__as_new_database_object()
        new["user_id"] = self.__user_id
        return new

    def __as_new_database_object(self) -> dict:
        return {
            "username": self.__username,
            "email": self.__email,
            "password": self.__password
        }

    @property
    def primary_key(self):
        """ This is a value allowing to uniquely identify an instance of User """
        return self.__username
