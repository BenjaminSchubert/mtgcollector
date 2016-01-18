#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Custom JSON operations
"""

from decimal import Decimal

import typing
from flask.json import JSONEncoder

from lib.models.collection import CardInCollection, CardInDeck


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class JSONDecodeError(Exception):
    """
    Error thrown when a json cannot be decoded
    """


class CustomJSONEncoder(JSONEncoder):
    """
    A custom JSONEncoder that is able to handle sets
    """
    def default(self, obj: typing.Any):
        """
        allows handling to set as list and decimals as int for flask json encoder

        :param obj: object to serialize
        :return: object json encoded
        """
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Decimal):
            return int(obj)
        return JSONEncoder.default(self, obj)


def deck_parser(parsed_dict: typing.Dict):
    """
    try to convert a dictionary into a deck

    :param parsed_dict: dictionary to parse
    :return: a new CardInDeck object
    """
    # CardInDeck (or Side)
    if set(parsed_dict.keys()) == {"name", "edition", "number", "ed_number"}:
        return CardInDeck(**parsed_dict)
    # this is the list of decks
    elif set(parsed_dict.keys()) == {"main", "side", "name"}:
        return parsed_dict
    else:
        raise JSONDecodeError("Unknown set of keys : {}".format(parsed_dict.keys()))


def collection_json_parser(parsed_dict: typing.Dict):
    """
    Try to parse the user's collection

    :param parsed_dict: dictionary to parse
    :return: user's collection
    """
    # CardInCollection
    if set(parsed_dict.keys()) == {"number", "name", "edition", "normal", "foil"}:
        return CardInCollection(**parsed_dict)
    # the deck is parsed
    elif set(parsed_dict.keys()) == {"collection", "decks"}:
        return parsed_dict
    else:
        return deck_parser(parsed_dict)
