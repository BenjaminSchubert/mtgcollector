#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Abstract base classes for models
"""

import abc

import flask
import typing


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class Model(metaclass=abc.ABCMeta):
    """
    Abstract class representing a model used in an application. Allows for an ORM view of the used objects
    """
    index = 0

    @classmethod
    @abc.abstractmethod
    def _table_creation_command(cls) -> str:
        """ Defines the sql command used to create the table for the model """

    @classmethod
    def _triggers(cls) -> typing.List[str]:
        """ list of triggers to add to the table """
        return []

    @classmethod
    @abc.abstractmethod
    def _insertion_command(cls) -> str:
        """ Saves the current object to the database. Should return the same user """

    @property
    @abc.abstractmethod
    def _as_database_object(self) -> dict:
        """ Returns the object as it should be when inserting it in the database as a dict"""

    @property
    @abc.abstractmethod
    def _primary_key(self) -> dict:
        """ This is a value that can uniquely identify any object (primary key) """

    @classmethod
    def bulk_insert(cls, models: typing.Iterable, connection=None, **kwargs) -> None:
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
        # noinspection PyArgumentList
        chunks = [models[i:i+chunk_size] for i in range(0, len(models), chunk_size)]

        for chunk in chunks:
            # noinspection PyProtectedMember
            cursor.executemany(cls._insertion_command(), [dict(model._as_database_object, **kwargs) for model in chunk])
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
    def setup_table(cls, connection=None) -> None:
        """
        Creates the table to be used with this model

        :param connection: the database connection to use. If None, will use flask.g.db
        """
        cls.__execute(cls._table_creation_command(), connection)
        for trigger in cls._triggers():
            cls.__execute(trigger, connection)

    @classmethod
    def __execute(cls, command: str, connection=None, **kwargs):
        """
        executes the given command on the database

        :param command: MySQL command to execute
        :param connection: the connection to the database to use. If not provided will try to get flask.g.db
        :param kwargs: parameters to give to the MySQL command
        :return: the MySQL cursor and connection
        """
        if connection is None:
            connection = getattr(flask.g, "db")
        cursor = connection.cursor(dictionary=True)
        cursor.execute(command, kwargs)
        return cursor, connection

    @classmethod
    def _modify(cls, command: str, connection=None, **kwargs) -> int:
        """
        executes a modification command on the database

        :param command: command to execute
        :param connection: connection to the database to use
        :param kwargs: arguments to give to the MySQL command
        :return: the last row id affected by the command
        """
        cursor, connection = cls.__execute(command, connection, **kwargs)
        connection.commit()
        return cursor.lastrowid

    def __eq__(self, other) -> bool:
        # noinspection PyProtectedMember
        return self._primary_key == other._primary_key

    def __hash__(self):
        return hash(self._primary_key)
