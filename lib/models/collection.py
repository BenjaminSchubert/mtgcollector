#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Models to handle collections
"""

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


class CardInCollection(Model):
    index = 2

    def _primary_key(self) -> dict:
        raise NotImplementedError()

    @classmethod
    def export(cls, user_id: int) -> typing.List:
        """
        exports user's cards

        :param user_id: id of the user owning the cards
        """
        return cls._get(sql.CardInCollection.export(), user_id=user_id)

    def __init__(self, name: str, edition: str, number: int, normal: int, foil: int):
        self.__name = name  # type: str
        self.__edition = edition  # type: str
        self.__number = number  # type: int
        self.__normal = normal  # type: int
        self.__foil = foil  # type: int

    def insert(self, user_id: int, card_id: int, n_normal: int, n_foil: int) -> None:
        """
        adds a new card to the collection.

        If both normal and foil are 0, will delete all instances of the card instead
        :param user_id: user owning the card
        :param card_id: card to add to the collection
        :param n_normal: number of normal copy
        :param n_foil: number of foil copy
        """
        if n_normal == n_foil == 0:
            self._modify(sql.CardInCollection.delete(), user_id=user_id, card_id=card_id)
        else:
            self._modify(
                    sql.CardInCollection.insert_by_id(), user_id=user_id, card_id=card_id, normal=n_normal, foil=n_foil
            )

    @classmethod
    def _insertion_command(cls) -> str:
        return sql.CardInCollection.insert()

    @classmethod
    def _table_creation_command(cls) -> str:
        return sql.CardInCollection.create_table()

    @property
    def _as_database_object(self) -> dict:
        return {
            "name": self.__name,
            "edition": self.__edition,
            "number": self.__number,
            "normal": self.__normal,
            "foil": self.__foil
        }


class CardInDeck(Model):
    """
    Represents a card in a deck, either side or not
    """
    index = 3

    def __init__(self, name, edition, ed_number, number):
        self.__name = name
        self.__edition = edition
        self.__ed_number = ed_number
        self.__number = number

    @classmethod
    def sql_class(cls) -> sql.CardInDeckEntity:
        """ the sql commands to the given entity """
        return sql.CardInDeck

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

    @property
    def _as_database_object(self) -> dict:
        """ this is never used """
        return {
            "name": self.__name,
            "edition": self.__edition,
            "ed_number": self.__ed_number,
            "number": self.__number
        }

    @classmethod
    def _insertion_command(cls) -> str:
        """ this is never used """
        return cls.sql_class().insert()

    def _primary_key(self) -> dict:
        """ this is never used """
        return self._as_database_object


class CardInSideDeck(CardInDeck):
    """
    Represents a card in a side deck
    """
    index = 3

    @classmethod
    def sql_class(cls) -> sql.CardInSide:
        """ gets the sql commands associated to this object """
        return sql.CardInSide


class Collection:
    """
    Collection model

    :param user_id: the id of the user owning the collection
    """
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.decks = Deck(self.user_id)

    def export(self):
        """ export the whole user's collection """
        data = {
            "decks": [self.decks.export(deck["name"]) for deck in self.decks.list()],
            "collection": CardInCollection.export(self.user_id)
        }
        return data

    def load(self, data: typing.Dict):
        """
        imports user's cards

        :param data: cards to import, json formatted
        """
        CardInCollection.bulk_insert(data.get("collection", []), user_id=self.user_id)
        for deck in data.get("decks", []):
            self.decks.load(deck)


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
            return CardInSideDeck.add(self.user_id, deck_name, card_id, n_cards)
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
            "side": CardInSideDeck.get_cards(self.user_id, deck_name),
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
            "side": CardInSideDeck.export_cards(self.user_id, deck_name)
        }

    def load(self, data: typing.Dict):
        """
        Saves the deck given into the database

        :param data: dictionary containing the deck
        """
        self.add(data["name"])
        CardInDeck.bulk_insert(data["main"], deck_name=data["name"], user_id=self.user_id)
        CardInSideDeck.bulk_insert(data["side"], deck_name=data["name"], user_id=self.user_id)

    def _primary_key(self) -> typing.Dict:
        """ unused """
        raise NotImplementedError()

    def _as_database_object(self) -> typing.Dict:
        """ unused """
        raise NotImplementedError()
