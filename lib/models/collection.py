#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Models to handle collections
"""

import abc
from collections import OrderedDict

import mysql.connector.errors
import typing

from lib.db import sql
from lib.exceptions import DataManipulationException
from lib.models import Model


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


color_list = OrderedDict()
for color, color_code in ("Red", "{R}"), ("Green", "{G}"), ("White", "{W}"), ("Blue", "{U}"), ("Black", "{B}"):
    color_list[color] = color_code


class Collection(Model):
    """
    Collection model

    :param user_id: the id of the user owning the collection
    """
    index = 2

    class InsertionProxy:
        """
        Proxy to add a card in a collection
        """
        def __init__(self, data, user_id):
            self.data = data
            self.data["user_id"] = user_id

        @property
        def _as_database_object(self):
            return self.data

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.data = []

    @classmethod
    def _table_creation_command(cls) -> str:
        """ command to create the Collection table """
        return sql.Collection.create_table()

    @classmethod
    def _insertion_command(cls) -> str:
        """ command to add a card to a collection """
        return sql.Collection.bulk_insert()

    # noinspection PyShadowingBuiltins
    def insert(self, card_id: int, n_normal: int, n_foil: int) -> None:
        """
        adds a new card to the collection.

        If both normal and foil are 0, will delete all instances of the card instead
        :param card_id: card to add to the collection
        :param n_normal: number of normal copy
        :param n_foil: number of foil copy
        """
        if n_normal == n_foil == 0:
            self._modify(sql.Collection.delete(), user_id=self.user_id, card_id=card_id)
        else:
            self._modify(sql.Collection.insert(), user_id=self.user_id, card_id=card_id, normal=n_normal, foil=n_foil)

    def export(self) -> typing.List:
        """ exports user's cards """
        return self._get(sql.Collection.export(), user_id=self.user_id)

    def load(self, data: typing.Dict):
        """
        imports user's cards

        :param data: cards to import, json formatted
        """
        self.data = data
        self.bulk_insert(self)
        self.data = []

    def _as_database_object(self) -> dict:
        """ this is never used """
        raise NotImplementedError()

    def _primary_key(self) -> dict:
        """ this is never used """
        raise NotImplementedError()

    def __iter__(self):
        for data in self.data:
            yield self.InsertionProxy(data, self.user_id)


class Deck(Model):
    """
    Deck model

    :param user_id: id of the user owning the deck
    """
    index = 2

    def __init__(self, user_id: int):
        self.user_id = user_id

    @classmethod
    def _table_creation_command(cls) -> str:
        """ table creation command """
        return sql.Deck.create_table()

    @classmethod
    def _insertion_command(cls) -> str:
        """ command to insert a new deck """
        sql.Deck.insert()

    def list(self) -> typing.List[typing.Dict[str, str]]:
        """ Gets a list of decks for the given user_id """
        decks = self._get(sql.Deck.list(), user_id=self.user_id)
        for deck in decks:
            if deck["colors"]:
                deck_colors = deck["colors"].split(",")
                deck["colors"] = [color_list[color_] for color_ in color_list if color_ in deck_colors]

        return decks

    def add(self, name: str):
        """
        adds a new deck to the user's collection

        :param name: name of the deck
        :return: the new created deck
        """
        self._modify(sql.Deck.insert(), user_id=self.user_id, name=name)
        return self._get(sql.Deck.get(), user_id=self.user_id, name=name)[0]

    def delete(self, name: str):
        """
        Deletes the deck given in parameter

        :param name: name of the deck
        """
        self._modify(sql.Deck.delete(), user_id=self.user_id, name=name)

    def rename(self, name: str, new_name: str):
        """
        Gives a new name to a deck

        :param name: name of the old deck to rename
        :param new_name: new name for the deck
        """
        try:
            self._modify(sql.Deck.rename(), user_id=self.user_id, name=name, new_name=new_name)
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:
                raise DataManipulationException("Cannot give the same name to two different decks")
            raise

    def set_index(self, name: str, index: int):
        """
        sets a new index to the given deck

        :param name: name of the deck for which to change the index
        :param index: new index to give to the deck
        """
        self._modify(sql.Deck.set_index(), user_id=self.user_id, name=name, index=index)

    def add_card(self, deck_name: str, card_id: int, n_cards: int, side: bool):
        """
        add a card to the deck identified by the given name

        :param deck_name: name of the deck to which to add the card
        :param card_id: id of the card to add
        :param n_cards: number of time to add the card
        :param side: whether to add the card in the side or in the deck
        """
        if side:
            return CardInSide.add(self.user_id, deck_name, card_id, n_cards)
        return CardInDeck.add(self.user_id, deck_name, card_id, n_cards)

    def remove_card(self, deck_name: str, card_id: int, side: bool):
        """
        Removes a card from a deck

        :param deck_name: name of the deck from which to remove the card
        :param card_id: id of the card to remove
        :param side: whether the card is in the side or not
        """
        self.add_card(deck_name, card_id, 0, side)

    def get_cards(self, deck_name: str) -> typing.List[typing.Dict[str, typing.Union[str, int]]]:
        """
        gets the cards that are in the given deck

        :param deck_name: identifier of the deck
        :return: list of cards in the asked deck
        """
        return {
            "main": CardInDeck.get_cards(self.user_id, deck_name),
            "side": CardInSide.get_cards(self.user_id, deck_name),
            "missing": self._get(sql.Deck.get_missing(), user_id=self.user_id, deck_name=deck_name)
        }

    def export(self, deck_name) -> typing.Dict:
        """
        exports all data necessary to allow the user to import the in another instance

        :param deck_name: name of the deck to export
        :return: dictionary of all information concerning the deck
        """
        return {
            "name": deck_name,
            "main": CardInDeck.export_cards(self.user_id, deck_name),
            "side": CardInSide.export_cards(self.user_id, deck_name)
        }

    def load(self, data: typing.Dict):
        """
        Saves the deck given into the database

        :param data: dictionary containing the deck
        """
        for key in data.keys():
            if key not in ['main', 'side', 'name']:
                raise DataManipulationException("Incorrectly formatted data. Got {} as key".format(key))

        if data["name"] in [obj["name"] for obj in self.list()]:
            raise DataManipulationException("A deck with the same name exists")

        self.add(data["name"])
        CardInDeck.bulk_insert(CardInDeck(self.user_id, data["name"], data["main"]))
        CardInSide.bulk_insert(CardInSide(self.user_id, data["name"], data["side"]))

    def _primary_key(self) -> typing.Dict:
        """ unused """
        raise NotImplementedError()

    def _as_database_object(self) -> typing.Dict:
        """ unused """
        raise NotImplementedError()


class CardInDeckMeta(Model, metaclass=abc.ABCMeta):
    """
    Represents a card in a deck, either side or not
    """
    index = 3

    class DBProxy:
        """
        Proxy to insert cards in deck/side
        """
        def __init__(self, user_id, deck_name, data):
            self.data = data
            self.data["user_id"] = user_id
            self.data["deck_name"] = deck_name

        @property
        def _as_database_object(self):
            return self.data

    def __init__(self, user_id: int, deck_name: str, data: typing.Dict):
        self.user_id = user_id
        self.deck_name = deck_name
        self.data = data

    @classmethod
    @abc.abstractmethod
    def sql_class(cls) -> sql.CardInDeckEntity:
        """ the sql commands to the given entity """

    @classmethod
    def _table_creation_command(cls) -> str:
        """ command to create the database table """
        return cls.sql_class().create_table()

    @classmethod
    def add(cls, user_id: int, deck_name: str, card_id: int, number: int):
        """
        add a card to a deck

        :param user_id: user owning the deck
        :param deck_name: name of the deck
        :param card_id: id of the card
        :param number: number of time to add the card
        """
        if number == 0:
            cls._modify(cls.sql_class().delete(), user_id=user_id, name=deck_name, card_id=card_id)
        else:
            cls._modify(cls.sql_class().add(), user_id=user_id, deck_name=deck_name, card_id=card_id, number=number)

    @classmethod
    def get_cards(cls, user_id: int, deck_name: str) -> typing.List[typing.Dict[str, typing.Union[str, int]]]:
        """
        return all cards matching the given deck
        :param user_id: user owning the deck
        :param deck_name: name of the deck
        :return: cards in the given deck
        """
        return cls._get(cls.sql_class().get_cards(), user_id=user_id, deck_name=deck_name)

    @classmethod
    def export_cards(cls, user_id: int, deck_name: str):
        """
        Return all information allowing to reconstruct the entries for the corresponding deck

        :param user_id: id of the user owning the deck
        :param deck_name: name of the deck
        :return: list of cards in the deck
        """
        return cls._get(cls.sql_class().export(), user_id=user_id, deck_name=deck_name)

    def _as_database_object(self) -> dict:
        """ this is never used """
        raise NotImplementedError()

    @classmethod
    def _insertion_command(cls) -> str:
        """ this is never used """
        return cls.sql_class().insert()

    def _primary_key(self) -> dict:
        """ this is never used """
        raise NotImplementedError()

    def __iter__(self):
        for obj in self.data:
            yield self.DBProxy(self.user_id, self.deck_name, obj)


# noinspection PyAbstractClass
class CardInDeck(CardInDeckMeta):
    """
    Represents a card in a deck, either side or not
    """

    @classmethod
    def sql_class(cls) -> sql.CardInDeck:
        """ gets the sql commands associated to this object """
        return sql.CardInDeck


# noinspection PyAbstractClass
class CardInSide(CardInDeckMeta):
    """
    Represents a card in a side deck
    """
    index = 3

    @classmethod
    def sql_class(cls) -> sql.CardInSide:
        """ gets the sql commands associated to this object """
        return sql.CardInSide
