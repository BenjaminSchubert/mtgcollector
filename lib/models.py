#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Models for MtgCollector
"""

import abc
import shlex

import flask
import datetime
import typing

from lib.exceptions import IntegrityException
from lib.db import sql_commands as sql


class Model(metaclass=abc.ABCMeta):
    """
    Abstract class representing a model used in an application. Allows for an ORM view of the used objects
    """
    index = 0

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
        models = list(models)
        chunks = [models[i:i+chunk_size] for i in range(0, len(models), chunk_size)]

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
        self.__colors = colors
        self.__cmc = cmc
        self.__instances = []
        self.__legalities = []

        try:
            self.__power = float(power)
        except TypeError:
            self.__power = None
        except ValueError:
            self.__power = -1

        try:
            self.__toughness = float(toughness)
        except TypeError:
            self.__toughness = None
        except ValueError:
            self.__toughness = -1

    @classmethod
    def table_creation_command(cls) -> str:
        """ The command to create the metacard table"""
        return sql.Metacard.create_table()

    @classmethod
    def insertion_command(cls) -> str:
        """ The command used to insert a metacard in the database """
        return sql.Metacard.insert()

    @classmethod
    def get_ids_where(cls, user_id: int=None, card_name: str="", card_type: str="", card_text: str="",
                      card_context: str="", card_number: str="", artist: str="", in_collection: bool=False,
                      power: str="", toughness: str="", cmc: str="", colors: str="", only_selected_colors: bool=False,
                      all_selected_colors: bool=False,
                      order_by="metacard.name"):
        def add_to_parameters(params: str, value: str):
            if params == "":
                params = "WHERE " + value
            else:
                params += " AND " + value
            return params

        def add_wildcard(entry: str):
            return "%" + "%".join(shlex.split(entry.strip())) + "%"

        def treat_range(query_parameters_, value, entry_name):
            if value:
                entry_max = "{}_max".format(entry_name)
                entry_min = "{}_min".format(entry_name)
                kwargs[entry_min], max_value = map(int, value.split(","))
                if max_value == cls.maximum(entry_name):
                    return add_to_parameters(query_parameters_, "metacard.{name} >= %({name_min})s").format(
                            name=entry_name, name_min=entry_min
                    )
                else:
                    kwargs[entry_max] = max_value
                    return add_to_parameters(
                        query_parameters_, "metacard.{name} BETWEEN %({name_min})s AND %({name_max})s"
                    ).format(name=entry_name, name_min=entry_min, name_max=entry_max)
            else:
                return query_parameters_

        def sum_colors(colors):
            return sum([color_translation[color] for color in colors])

        color_translation = {"Red": 1, "Green": 2, "White": 4, "Blue": 8, "Black": 16}
        all_colors = {"Red", "Green", "White", "Blue", "Black"}
        query_parameters = ""
        having = ""
        kwargs = dict()

        if user_id:
            command = sql.Metacard.get_ids_with_collection_information()
            add_to_parameters(query_parameters, "user.user_id = %(user_id)s")
            kwargs["user_id"] = user_id
        else:
            command = sql.Metacard.get_ids()

        if card_name:
            query_parameters = add_to_parameters(query_parameters, "metacard.name LIKE %(name)s")
            kwargs["name"] = add_wildcard(card_name)

        if card_type:
            query_parameters = add_to_parameters(query_parameters, "metacard.types LIKE %(type)s")
            kwargs["type"] = add_wildcard(card_type)

        if card_text:
            query_parameters = add_to_parameters(query_parameters, "metacard.orig_text LIKE %(card_text)s")
            kwargs["card_text"] = add_wildcard(card_text)

        if card_context:
            query_parameters = add_to_parameters(query_parameters, "card.flavor LIKE %(flavor)s")
            kwargs["flavor"] = add_wildcard(card_context)

        if card_number:
            query_parameters = add_to_parameters(query_parameters, "card.number = %(card_number)s")
            kwargs["card_number"] = card_number

        if artist:
            query_parameters = add_to_parameters(query_parameters, "card.artist LIKE %(artist)s")
            kwargs["artist"] = add_wildcard(artist)

        if in_collection:
            having = ("HAVING (IFNULL(SUM(card_in_collection.normal), 0)"
                      " + IFNULL(SUM(card_in_collection.foil), 0)) > 0")

        if "Colorless" in colors and len(colors) == 1:
            query_parameters = add_to_parameters(query_parameters, "metacard.colors IS NULL")
        elif colors:
            colors = set(colors)
            if all_selected_colors:
                if only_selected_colors:
                    query_parameters = add_to_parameters(query_parameters, "metacard.colors = %(colors)s")
                    kwargs["colors"] = sum_colors(colors & all_colors)
                else:
                    query_parameters = add_to_parameters(query_parameters, "(metacard.colors & %(colors)s) = %(colors)s")
                    kwargs["colors"] = sum_colors(colors & all_colors)
            else:
                if only_selected_colors:
                    query_parameters = add_to_parameters(
                            query_parameters, "(((metacard.colors & %(colors)s) = 0) {colorless})"
                    )
                    kwargs["colors"] = sum_colors(all_colors - colors)
                else:
                    query_parameters = add_to_parameters(
                            query_parameters, "(((metacard.colors & %(colors)s) > 0) {colorless})")
                    kwargs["colors"] = sum_colors(colors & all_colors)

                query_parameters = query_parameters.format(colorless=" OR (metacard.colors IS NULL)")

        query_parameters = treat_range(query_parameters, power, "power")
        query_parameters = treat_range(query_parameters, toughness, "toughness")
        query_parameters = treat_range(query_parameters, cmc, "cmc")

        query = command.format(selection=query_parameters, order=order_by, having=having)
        return [value for value in cls._get(query, **kwargs)]

    @classmethod
    def maximum(cls, maximum) -> typing.Union[int, None]:
        """
        The maximum value in the Metacard table for the given field

        :param maximum: the field for which to take the max
        :return the maximum value
        """
        try:
            return cls._get(sql.Metacard.maximum().format(maximum=maximum))[1]["max"]
        except IndexError:  # this might happen if the database if not yet initialized, let's return a safe value
            return None

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
    index = 1

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

    @classmethod
    def get_image_url(cls, card_id, logger, **kwargs):
        cards = cls._get(sql.Card.get_multiverseid(), card_id=card_id, **kwargs)
        if len(cards):
            return "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={}&type=card".format(
                    cards[0]["multiverseid"]
            )
        logger.warning("Could not download image for {}".format(card_id))
        flask.abort(404)

    @classmethod
    def get_default_image_url(cls):
        return (
            "http://gatherer.wizards.com/Handlers/Image.ashx?size=small&type=card&"
            "name=The%20Ultimate%20Nightmare%20of%20Wizards%20of%20the%20Coast%20Customer%20Service&options="
        )


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


class Collection(Model):
    """
    Collection model

    :param user_id
    """
    index = 2

    def __init__(self, user_id: int):
        self.user_id = user_id

    @classmethod
    def table_creation_command(cls) -> str:
        return sql.Collection.create_table()

    @classmethod
    def insertion_command(cls) -> str:
        return sql.Collection.insert()

    def insert(self, card_id, normal, foil):
        self._modify(self.insertion_command(), user_id=self.user_id, card_id=card_id, normal=normal, foil=foil)

    def delete(self, card_id):
        self._modify(sql.Collection.delete(), user_id=self.user_id, card_id=card_id)

    def as_database_object(self) -> dict:
        pass

    def primary_key(self) -> dict:
        return self.user_id


class Deck(Model):
    """
    Deck model

    :param user_id
    """
    index = 2

    def __init__(self, user_id: int):
        self.user_id = user_id

    @classmethod
    def table_creation_command(cls) -> str:
        """ table creation command """
        return sql.Deck.create_table()

    @classmethod
    def insertion_command(cls) -> str:
        """ command to insert a new deck """
        sql.Deck.insert()

    @classmethod
    def list(cls, user_id: int) -> typing.List[typing.Dict[str, str]]:
        """
        Gets a list of decks for the given user_id

        :param user_id: the id of the user for which to get decks
        :return: list of Decks
        """
        return cls._get(sql.Deck.list(), user_id=user_id)


    def primary_key(self) -> dict:
        pass

    def as_database_object(self) -> dict:
        pass


class CardInDeck(Model):
    """
    Represents a card in a deck
    """
    index = 3

    @classmethod
    def table_creation_command(cls) -> str:
        """ command to create the database table """
        return sql.CardInDeck.create_table()

    def as_database_object(self) -> dict:
        pass

    @classmethod
    def insertion_command(cls) -> str:
        pass

    def primary_key(self) -> dict:
        pass


class CardInSide(Model):
    """
    Represents a card in a side deck
    """
    index = 3

    @classmethod
    def table_creation_command(cls) -> str:
        """ command to create the database table """
        return sql.CardInSide.create_table()

    def primary_key(self) -> dict:
        pass

    @classmethod
    def insertion_command(cls) -> str:
        pass

    def as_database_object(self) -> dict:
        pass


class DeckList:
    """
    Proxy to obtain lists for a

    :param user_id
    """
    def __init__(self, user_id: int):
        self.user_id = user_id

    def list(self) -> typing.List[typing.Dict[str, str]]:
        """
        Returns the list of decks

        :return: list of deck
        """
        return Deck.list(self.user_id)


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
        self.collection = Collection(self.__user_id)
        self.decks = DeckList(self.__user_id)

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
