#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Base setup for the sql backend

For now only supports MySQL but others can be easily implemented
"""

from lib.db.sql import mysql as sql_commands
import lib.db.populate

get_connection = sql_commands.get_connection
