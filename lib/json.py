#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Custom JSON operations
"""
from flask.json import JSONEncoder


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class CustomJSONEncoder(JSONEncoder):
    """
    A custom JSONEncoder that is able to handle sets
    """
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)
