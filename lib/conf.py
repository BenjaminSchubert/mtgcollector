#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Various helpers to handle flask application configuration
"""

import contextlib

from mtgcollector import app


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


def update_conf(**kwargs):
    """
    Writes the given kwargs in flask's configuration file

    :param kwargs: arguments to write
    """
    data = {}
    with contextlib.suppress(FileNotFoundError):
        with open(app.config["CONFIG_PATH"], encoding="utf-8") as old_data_file:
            for entry in old_data_file:
                key, _ = entry.split("=")
                data[key.strip()] = app.config[key.strip()]

    data.update(**kwargs)

    with open(app.config["CONFIG_PATH"], "w", encoding="utf-8") as new_data_File:
        for key, value in data.items():
            new_data_File.write("{} = '{}'\n".format(key, value))

    app.config.from_pyfile(app.config["CONFIG_PATH"])
