# -*- coding: utf-8 -*-
import abc
import flask
from typing import NamedTuple
from typing import Iterable
import datetime
import typing


class Model(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def table_creation_command(cls):
        """ Defines the sql command used to create the table for the model """

    @classmethod
    @abc.abstractmethod
    def table_constraints(cls) -> Iterable[str]:
        """ List of constraints to apply on the table """

    def __eq__(self, other):
        for current, other in zip(vars(self).values(), vars(other).values()):
            if current != other:
                return False

        return True

    @classmethod
    def insert(cls, command, connection=None, **kwargs):
        if connection is None:
            connection = getattr(flask.g, "db")
        cursor = connection.cursor(dictionary=True)
        cursor.execute(command, kwargs)
        connection.commit()
        return cursor.lastrowid

    @classmethod
    def get(cls, command, connection=None, **kwargs):
        if connection is None:
            connection = getattr(flask.g, "db")
        cursor = connection.cursor(dictionary=True)
        cursor.execute(command, kwargs)
        return cursor.fetchall()

    @classmethod
    def create_table(cls, connection=None):
        if connection is None:
            connection = getattr(flask.g, "db")
        cursor = connection.cursor()
        cursor.execute(cls.table_creation_command())

    @classmethod
    def create_table_constraints(cls, connection=None):
        if connection is None:
            connection = getattr(flask.g, "db")
        cursor = connection.cursor()
        for constraint in cls.table_constraints:
            cursor.execute(constraint)


def info(self, ignored: Iterable[str]=list(), **kwargs):
    objects = {key: getattr(self, key) for key in self._fields if key not in ignored}
    objects.update(kwargs)
    return objects


class Edition(NamedTuple("Edition",
                         [
                             ("type", str), ("code", str), ("releaseDate", datetime.datetime),
                             ("name", str), ("block", str)
                         ])
              ):
    info = info


class Metacard(NamedTuple("Metacard",
                          [
                              ("name", str), ("types", typing.Set), ("subtypes", typing.List),
                              ("supertypes", typing.List), ("manaCost", str), ("text", str), ("power", float),
                              ("toughness", float), ("colors", typing.List), ("cmc", float),
                              ("instances", typing.List), ("legalities", typing.List)
                          ])
               ):
    info = info


class Card(NamedTuple("Card",
                      [
                          ("multiverseid", int), ("rarity", str), ("number", str), ("edition", str), ("artist", str),
                          ("flavor", str), ("version", int)
                      ])
           ):
    info = info
