#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Custom JSON operations
"""

from decimal import Decimal

import typing
from flask.json import JSONEncoder


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


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
        if isinstance(obj, Decimal):  # TODO we should avoid this and return proper integers
            return int(obj)
        return JSONEncoder.default(self, obj)
