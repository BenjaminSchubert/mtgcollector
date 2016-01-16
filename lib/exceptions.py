#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Exceptions used across mtgcollector for error tracking
"""

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class DataManipulationException(Exception):
    """
    Exception raised when a data operation fails for example :

        - insertion in a database that doesn't meet some requirements
        - modification in a database that isn't correct
        - forbidden deletion
    """
    def __init__(self, error):
        super().__init__()
        self.error = error
