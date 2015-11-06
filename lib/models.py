# -*- coding: utf-8 -*-
from typing import NamedTuple
from typing import Iterable
import datetime
import typing
from flask.ext import login


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


class User(login.UserMixin):
    def __init__(self, user_id, username, email, password, is_admin):
        self.__user_id = user_id
        self.username = username
        self.email = email
        self.__password = password
        self.__is_admin = is_admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return self.__user_id

    def check_password(self, password):
        return self.__password == password
