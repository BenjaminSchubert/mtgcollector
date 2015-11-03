# -*- coding: utf-8 -*-
from typing import NamedTuple
from typing import Iterable
import datetime
import typing


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
