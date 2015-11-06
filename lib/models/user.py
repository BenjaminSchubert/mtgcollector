#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Iterable

from lib.models import Model
from lib.db import sql_commands as sql


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
    def table_creation_command(cls) -> str:
        """ The command to create the user table """
        return sql.create_table_user

    @classmethod
    def table_constraints(cls) -> Iterable[str]:
        """ list of constraints on table user """
        return sql.user_constraints

    @property
    def is_authenticated(self) -> bool:
        """
        Checks if the user is authenticated

        :return: True as we only create user instance on login
        """
        return True

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
    def is_admin(self) -> bool:
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

    @classmethod
    def get_user_by_name_or_mail(cls, identifier: str):
        """
        Checks for a user having the given identifier as name or email and returns it

        :param identifier: the identifier for email or username
        :return: User instance for the given user or None
        """
        data = cls.get(sql.select_user, identifier=identifier)
        return User(**data[0]) or None

    @classmethod
    def get_user_by_id(cls, user_id: int):
        """
        Fetches a user by id and returns it

        :param user_id: the wanted user id
        :return: User instance or None
        """
        data = cls.get(sql.get_user_by_id, user_id=user_id)
        if len(data):
            return User(**data[0])

    @classmethod
    def get_users(cls, limit: int=None) -> list:
        """
        Returns users with a given limit

        :param limit: maximum number of users to return
        :return: list of User
        """
        if limit is not None:
            users = cls.get(sql.get_users_with_limit, limit=limit)
        else:
            users = cls.get(sql.get_users)
        return [User(**data) for data in users]

    @classmethod
    def create_user(cls, username: str, email: str, password: str) -> id:
        """
        Inserts a new user in the database

        :param username
        :param email
        :param password
        :return: the id of the inserted user
        """
        new_user = cls.insert(sql.create_user, username=username, email=email, password=password)
        return cls.get_user_by_id(new_user)

    def set_admin(self, admin: bool=True) -> None:
        """
        Sets the user identified by user_id to be an admin if admin is True (default)
        Else remove the right of being admin to the user

        :param admin: whether to turn the user as admin or remove him the rights to be
        """
        self.__is_admin = admin
        self.insert(sql.set_admin, user_id=self.get_id(), admin=admin)
