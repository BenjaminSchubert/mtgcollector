#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
User's model
"""

import hashlib
import logging
import os

import flask
import typing

from lib.db import sql
from lib.exceptions import DataManipulationException
from lib.models import Model, Collection, Deck


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class User(Model):
    """
    User model

    :param username: name of the user
    :param email: email of the user
    :param password: the user password
    :param is_admin: true if the user is an admin
    :param user_id: user's unique identifier
    :param salt: salt used to encrypt the user password
    """
    def __init__(self, username: str, email: str, password: str, is_admin: bool=False, user_id: int=None,
                 salt: bytes=None):
        self.__user_id = user_id
        self.__username = username
        self.__email = email

        self.__salt = salt
        self.__password = password

        if salt is None:  # this is a new user, we encode the password
            self.__hash_password()

        self.__is_admin = is_admin
        self.collection = Collection(self.__user_id)
        self.decks = Deck(self.__user_id)

    @classmethod
    def _insertion_command(cls) -> str:
        """ Command used to insert a user in the database """
        return sql.User.insert()

    @classmethod
    def _table_creation_command(cls) -> str:
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
            logging.error("Got multiple user with same email/username : {}".format(data))
            flask.abort(500)

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

    @property
    def username(self) -> str:
        """ username of the user """
        return self.__username

    @property
    def email(self) -> str:
        """ user's email """
        return self.__email

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
        return self.__password == hashlib.pbkdf2_hmac('sha512', password.encode("utf-8"), self.__salt, 1000000)

    def create(self):
        """
        Inserts the given user in the database

        :return: the newly created user
        """
        if User.get_user_by_name_or_mail(self.__email) or User.get_user_by_name_or_mail(self.__username):
            raise DataManipulationException(error="cannot add a user with the same name or email as another one")

        new_user_id = self._modify(sql.User.insert(), **self.__as_new_database_object())
        new_user = self.get_user_by_id(new_user_id)
        self.__user_id = new_user.__user_id
        self.__is_admin = new_user.__is_admin
        return self

    def update(self, username: str, email: str, password: str=None):
        """
        Updates the current user with the given values

        :param username: new username
        :param email: new email
        :param password: new password
        """
        if (User.get_user_by_name_or_mail(email) and self.__email != email) \
                or (User.get_user_by_name_or_mail(username) and self.__username != username):
            raise DataManipulationException(error="cannot add a user with the same name or email as another one")

        if password:
            self.__password = password
            self.__hash_password()

        if username:
            self.__username = username

        if email:
            self.__email = email

        self._modify(sql.User.update(), **self._as_database_object())

    def set_admin(self, admin: bool=True) -> None:
        """
        Sets the user identified by user_id to be an admin if admin is True (default)
        Else remove the right of being admin to the user

        :param admin: whether to turn the user as admin or remove him the rights to be
        """
        self._modify(sql.User.set_admin(), user_id=self.get_id(), admin=admin)
        self.__is_admin = admin

    def export(self):
        """ export the whole user's collection """
        data = {
            "decks": [self.decks.export(deck["name"]) for deck in self.decks.list()],
            "collection": self.collection.export()
        }
        return data

    def load(self, data: typing.Dict):
        """
        load the user's collection

        :param data: dictionary containing all the collection's information
        """
        for key in data.keys():
            if key not in ["collection", "decks"]:
                raise DataManipulationException("Incorrectly formatted data. Got {} as key".format(key))

        for entry in data.get("decks", []):
            for key in entry.keys():
                if key not in ["main", "side", "name"]:
                    raise DataManipulationException("Incorrectly formatted deck. Got {} as key".format(key))

        self.collection.load(data["collection"])
        for deck in data.get("decks", []):
            self.decks.load(deck)

    def __hash_password(self):
        """ hashes the user's password and set a new salt """
        self.__salt = os.urandom(255)
        self.__password = hashlib.pbkdf2_hmac('sha512', self.__password.encode("utf-8"), self.__salt, 1000000)

    def _as_database_object(self) -> dict:
        """ View of the user as a dictionary """
        new = self.__as_new_database_object()
        new["user_id"] = self.__user_id
        return new

    def __as_new_database_object(self) -> dict:
        return {
            "username": self.__username,
            "email": self.__email,
            "password": self.__password,
            "salt": self.__salt
        }

    @property
    def _primary_key(self):
        """ This is a value allowing to uniquely identify an instance of User """
        return self.__username
