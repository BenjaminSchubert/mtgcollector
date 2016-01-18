#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Models for resources external to our application
"""

import datetime
import logging
import shlex

import flask
import typing

from lib.db import sql
from lib.models import Model


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class Edition(Model):
    """
    Class representing a MTG Edition

    :param type: type of the edition (normal, prerelease, etc)
    :param code: unique ID of the edition, as a 3 or 4 letter code
    :param releaseDate: date the edition was released
    :param name: name of the edition
    :param block: block in which the edition was published
    """
    # noinspection PyPep8Naming,PyShadowingBuiltins
    def __init__(self, type: str, code: str, releaseDate: datetime.datetime, name: str, block: str):
        self.__type = type
        self.__code = code
        self.__releaseDate = releaseDate
        self.__name = name
        self.__block = block

    @classmethod
    def _insertion_command(cls) -> str:
        """ The command used to insert an edition in the database """
        return sql.Edition.insert()

    @classmethod
    def _table_creation_command(cls) -> str:
        """ The command used to insert values in the database"""
        return sql.Edition.create_table()

    @classmethod
    def list(cls) -> typing.List[typing.Dict[str, str]]:
        """ returns a list of Editions of the form (code, name) """
        return cls._get(sql.Edition.list())

    @classmethod
    def blocks(cls) -> typing.List[typing.Dict[str, str]]:
        """ returns all existing blocs """
        return cls._get(sql.Edition.blocks())

    @property
    def _as_database_object(self) -> dict:
        """ A dictionary view of the edition """
        return {
            "type": self.__type,
            "code": self.__code,
            "releaseDate": self.__releaseDate,
            "name": self.__name,
            "block": self.__block
        }

    @property
    def _primary_key(self):
        """ This is a value allowing to uniquely identify an instance of Edition """
        return self.__code


class Metacard(Model):
    """
    Represents an abstract card, which can span on multiple representation and editions

    :param name: name of the card
    :param types: types of the card
    :param subtypes: subtypes of the card
    :param supertypes: supertypes of the card (Legendary, Snow,...)
    :param manaCost: mana cost as a string
    :param text: text of the card
    :param power: power of the card
    :param toughness: toughness of the card
    :param colors: colors of the card as a list
    :param cmc: converted mana cost
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
    def _table_creation_command(cls) -> str:
        """ The command to create the metacard table"""
        return sql.Metacard.create_table()

    @classmethod
    def _insertion_command(cls) -> str:
        """ The command used to insert a metacard in the database """
        return sql.Metacard.insert()

    # noinspection PyShadowingBuiltins
    @classmethod
    def get_ids_where(cls, user_id: int=None, name: str= "", subtypes: str= "", text: str= "", context: str= "",
                      number: str= "", artist: str= "", in_collection: bool=False, power: str="", toughness: str="",
                      cmc: str="", colors: typing.List[str]=list(), edition: str="", block: str="", format: str="",
                      rarity: str="", order_by="metacard.name", supertypes: str="", types: str="", **kwargs)\
            -> typing.List[typing.Dict[str, typing.Dict[str, str]]]:
        """
        This allows for extensive filtering and complex queries on the cards. It will return all ids of cards
        matching the given criteria

        :param user_id: if this is given, will add to the answer the number of each card owned by the player identified
                        by the id
        :param name: MySQL regex to be matched against the name of the card. wildcards will be added between each word
        :param subtypes: types the card must have. This will be matched against the card type with MySQL regex as for
                        name
        :param text: text that must be on the card. Will also be matched as a MySQL regex as for name
        :param context: text that must be in the context field of the card. MySQL regex as for name
        :param number: the number that each cards has in its edition
        :param artist: the artist that drew the card, will be treated as a MySQL regex as for name
        :param in_collection: whether the card is in the user's collection or not. Only working for logged in users
        :param power: minimum and maximum power the creature can have. Formatted as "min,max". min=-1 means "*" and when
                        max is at it's maximum value, it means no limit
        :param toughness: minimum and maximum toughness the creature can have. Formatted as for power
        :param cmc: the converted mana cost of the card, Formatted as for power
        :param colors: the colors the card must/can have. This behavior will depend on `only_selected_colors` and
                        `all_selected_colors`. If both are unchecked, this means that the card must have at least one
                        of the specified colors in its cost
        :param edition: the edition in which the card must be
        :param block: the block of editions in which the card must be
        :param format: the playable format in which the card must be legal
        :param rarity: the rarities the card can have
        :param order_by: in which order to sort the result
        :param supertypes: supertypes the card must have
        :param types: the types the card must have
        :param kwargs: garbage arguments
        :return: list of cards containing dictionaries with fields {"id", "normal", "foil"}
        """
        def add_to_parameters(params: str, value: str) -> str:
            """
            Adds the given value to the parameters already given

            :param params: the parameters to which to add the new postulate
            :param value: the new postulate to add
            :return: a new string containing both previous postulate
            """
            if params == "":
                params = "WHERE " + value
            else:
                params += " AND " + value
            return params

        def add_wildcard(entry: str) -> str:
            """
            Adds MySQL wildcards to the entry to allow for regexp checking

            :param entry: the entry to which to add the wildcards
            :return: the new entry with wildcards
            """
            return "%" + "%".join(shlex.split(entry.strip().replace("'", "\\\'"))) + "%"

        def treat_range(query_parameters_: str, value: str, entry_name: str) -> str:
            """
            Treats a value as a range, that is adds a MIN and MAX value for the parameter

            :param query_parameters_: the old parameters to update with the new constraint
            :param value: the "min,max" value for the field
            :param entry_name: the field name
            :return: a new query parameter string with the given constraint incorporated
            """
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

        def sum_colors(colors_: typing.Set) -> int:
            """
            Computes the total value of the given colors

            This is because MySQL stores the SET type as a sum of values.
            Using these values allow for much easier computing of all SET operation,
            which are not provided by default by MySQL

            :param colors_: the colors for which to compute the value
            :return: the value of all the colors given
            """
            return sum([color_translation[color_] for color_ in colors_])

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

        if name:
            query_parameters = add_to_parameters(query_parameters, "metacard.name LIKE %(name)s")
            kwargs["name"] = add_wildcard(name)

        if subtypes:
            query_parameters = add_to_parameters(query_parameters, "metacard.subtypes LIKE %(subtypes)s")
            kwargs["subtypes"] = add_wildcard(subtypes)

        if text:
            query_parameters = add_to_parameters(query_parameters, "metacard.orig_text LIKE %(card_text)s")
            kwargs["card_text"] = add_wildcard(text)

        if context:
            query_parameters = add_to_parameters(query_parameters, "card.flavor LIKE %(flavor)s")
            kwargs["flavor"] = add_wildcard(context)

        if number:
            query_parameters = add_to_parameters(query_parameters, "card.number = %(card_number)s")
            kwargs["card_number"] = number

        if artist:
            query_parameters = add_to_parameters(query_parameters, "card.artist LIKE %(artist)s")
            kwargs["artist"] = add_wildcard(artist)

        if in_collection:
            having = ("HAVING (IFNULL(SUM(card_in_collection.normal), 0)"
                      " + IFNULL(SUM(card_in_collection.foil), 0)) > 0")

        if edition:
            query_parameters = add_to_parameters(query_parameters, "card.edition = %(edition)s")
            kwargs["edition"] = edition

        if block:
            query_parameters = add_to_parameters(
                    query_parameters, "card.edition IN (SELECT code FROM edition WHERE block = %(block)s)"
            )
            kwargs["block"] = block

        if supertypes:
            query_parameters = add_to_parameters(query_parameters, "%(supertypes)s IN (metacard.supertypes)")
            kwargs["supertypes"] = supertypes

        if types:
            query_parameters = add_to_parameters(query_parameters, "metacard.types LIKE %(types)s")
            kwargs["types"] = types + "%"

        if format:
            query_parameters = add_to_parameters(
                    query_parameters,
                    ("card.name IN (SELECT card_name FROM card_legal_in_format WHERE format = %(format)s"
                        "AND type != 'Banned')")
            )
            kwargs["format"] = format

        if rarity:
            rarity_subquery = "card.rarity IN ("
            # noinspection PyArgumentList
            for rarity_, counter in zip(rarity, range(0, len(rarity))):
                rarity_subquery += "%(rarity_{})s,".format(counter)
                kwargs["rarity_{}".format(counter)] = rarity_
            rarity_subquery = rarity_subquery[:-1] + ")"
            query_parameters = add_to_parameters(query_parameters, rarity_subquery)

        all_selected_colors = "all_selected" in colors
        only_selected_colors = "only_selected" in colors

        if all_selected_colors:
            colors.remove("all_selected")
        if only_selected_colors:
            colors.remove("only_selected")

        if "Colorless" in colors and len(colors) == 1:
            query_parameters = add_to_parameters(query_parameters, "metacard.colors IS NULL")
        elif colors:
            colors = set(colors)
            if all_selected_colors:
                if only_selected_colors:
                    query_parameters = add_to_parameters(query_parameters, "metacard.colors = %(colors)s")
                    kwargs["colors"] = sum_colors(colors & all_colors)
                else:
                    query_parameters = add_to_parameters(
                            query_parameters, "(metacard.colors & %(colors)s) = %(colors)s"
                    )
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
        print(query % kwargs)
        return cls._get(query, **kwargs)

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
    def _as_database_object(self) -> typing.Dict[str, str]:
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
    def _primary_key(self) -> str:
        """ This is a value allowing to uniquely identify an instance of Metacard """
        return self.__name


class Card(Model):
    """
    A concrete representation of a card

    :param name: name of the card
    :param rarity: rarity of the card
    :param number: number of the card in the edition in which it was released, 0 for editions which did not have this
    :param edition: edition's code in which the card was released
    :param artist: artist that drew the card
    :param flavor: context text on the card
    :param multiverseid: official card ID given by Wizards of The Coast, can be null for promotional cards
    """
    index = 1

    def __init__(
            self, name: str, rarity: str, number: str, edition: str, artist: str, flavor: str,
            multiverseid: int=None
    ):
        self.__name = name
        self.__rarity = rarity
        self.__number = number
        self.__edition = edition
        self.__artist = artist
        self.__flavor = flavor
        self.__multiverseid = multiverseid

    @classmethod
    def _table_creation_command(cls):
        """ The command used to create the card table """
        return sql.Card.create_table()

    @classmethod
    def _insertion_command(cls) -> str:
        """ The command used to insert a table in the database """
        return sql.Card.insert()

    @property
    def _as_database_object(self) -> typing.Dict[str, typing.Union[str, float, int, list]]:
        """ A dictionary view of the card """
        return {
            "multiverseid": self.__multiverseid,
            "name": self.__name,
            "rarity": self.__rarity,
            "number": self.__number,
            "edition": self.__edition,
            "artist": self.__artist,
            "flavor": self.__flavor
        }

    @property
    def _primary_key(self) -> str:
        """ This is a value allowing to uniquely identify an instance of Card """
        return self.__name, self.__edition, self.__number

    @classmethod
    def get(cls, card_id: int):
        """
        Gets the information about the card with the given id

        :param card_id: id of the card to fetch
        :return: a Card instance
        """
        return cls._get(sql.Card.get(), card_id=card_id)

    @classmethod
    def get_image_url(cls, card_id: int, logger: logging.Logger, connection=None) -> str:
        """
        gets the url of the image for the given card

        :param card_id: card id for which to get the image
        :param logger: logger instance to save errors
        :param connection: connection to the database
        :return: the url to the requested card's image
        """
        cards = cls._get(sql.Card.get_multiverseid(), card_id=card_id, connection=connection)
        if len(cards):
            return "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={}&type=card".format(
                    cards[0]["multiverseid"]
            )
        logger.warning("Could not download image for {}".format(card_id))
        flask.abort(404)

    @classmethod
    def get_default_image_url(cls) -> str:
        """ url of a card's back to display when the original image could not be found """
        return (
            "http://gatherer.wizards.com/Handlers/Image.ashx?size=small&type=card&"
            "name=The%20Ultimate%20Nightmare%20of%20Wizards%20of%20the%20Coast%20Customer%20Service&options="
        )

    @classmethod
    def get_versions(cls, name, user_id=None):
        """
        Gets all different versions from the same card

        :param name: name of the card
        :param user_id: id of the user connected. If set, will show how much of each he has
        """
        if user_id:
            return cls._get(sql.Card.get_versions_with_collection_information(), user_id=user_id, name=name)
        else:
            return cls._get(sql.Card.get_versions(), name=name)

    @classmethod
    def rarities(cls) -> typing.List[str]:
        """ returns all the different rarity a card can have """
        return [card["rarity"].pop() for card in cls._get(sql.Card.rarities())]

    @classmethod
    def get_collection(cls, user_id: int) -> typing.List[typing.Dict[str, str]]:
        """
        returns all cards in the collection for the given user_id

        :param user_id: the user for which to get the collection
        :return list of cards
        """
        return cls._get(sql.Card.collection(), user_id=user_id)


class Format(Model):
    """
    Format model

    :param name: the name of the format
    """
    def __init__(self, name):
        self.__name = name

    @classmethod
    def _insertion_command(cls) -> str:
        """ Command to insert a tournament in the database """
        return sql.Format.insert()

    @classmethod
    def _table_creation_command(cls) -> str:
        """ Creation command for the tournament table """
        return sql.Format.create_table()

    @classmethod
    def list(cls) -> typing.List[typing.Dict[str, str]]:
        """ list all existing tournament formats """
        return cls._get(sql.Format.list())

    @property
    def _as_database_object(self) -> typing.Dict[str, str]:
        """ Dictionary view of a tournament """
        return {
            "name": self.__name
        }

    @property
    def _primary_key(self) -> str:
        """ This is a value allowing to uniquely identify an instance of Tournament """
        return self.__name


class LegalInFormat(Model):
    """
    Represents that a card is not legal in a tournament

    :param card_name: the name of the card
    :param _format: the format of the tournament
    :param _type: type of legality (Legal, Banned, Restricted)
    """
    index = 3

    def __init__(self, card_name, _format, _type):
        self.__card_name = card_name
        self.__format = _format
        self.__type = _type

    @classmethod
    def _table_creation_command(cls) -> str:
        """ command to create the database table """
        return sql.LegalInFormat.create_table()

    @property
    def _as_database_object(self) -> typing.Dict[str, str]:
        """ gets a dictionary view of the object for insertion in the database """
        return {
            "card_name": self.__card_name,
            "format": self.__format,
            "type": self.__type
        }

    @property
    def _primary_key(self) -> typing.Sequence:
        """ primary card for the card in format """
        return (self.__card_name, self.__format)

    @classmethod
    def _insertion_command(cls) -> str:
        """ command to insert an item in the database """
        return sql.LegalInFormat.insert()
