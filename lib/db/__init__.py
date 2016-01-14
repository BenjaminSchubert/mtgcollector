#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Base setup for the sql backend

For now only supports MySQL but others can be easily implemented
"""

from lib.db import sql as sql_commands

get_connection = sql_commands.get_connection
