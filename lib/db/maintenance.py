#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Database Maintenance utilities
"""

import datetime

import flask
import mysql.connector
import mysql.connector.errorcode
import mysql.connector.errors

import lib
import lib.db
import lib.models
from lib.parser import JSonCardParser


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class MaintenanceDB:
    """
    Database Maintenance utilities
    """
    class DBManager:
        """
        Database context manager
        """
        def __init__(self, app):
            self.app = app
            self.conn = None

        def __enter__(self):
            self.conn = lib.db.get_connection(self.app)
            return self.conn

        # noinspection PyUnusedLocal
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.conn.close()

    def __init__(self, app: flask.Flask):
        self.app = app

    def __update(self, card_parser: JSonCardParser) -> None:
        """
        Uses the given JSonCardParser to insert all its information into the database

        :param card_parser: jsonCardParser entity containing the values to enter in the database
        """
        with self.DBManager(self.app) as connection:
            lib.models.Edition.bulk_insert(card_parser.editions, connection=connection)
            lib.models.Format.bulk_insert(card_parser.formats, connection=connection)
            lib.models.Metacard.bulk_insert(card_parser.metacards, connection=connection)
            lib.models.Card.bulk_insert(card_parser.cards, connection=connection)
            lib.models.LegalInFormat.bulk_insert(card_parser.legal_in_format, connection=connection)

    def setup_db(self) -> None:
        """ Configures the database with the models subclassing lib.models.Model """
        conn = mysql.connector.connect(
            user=self.app.config["DATABASE_USER"], password=self.app.config["DATABASE_PASSWORD"],
            host=self.app.config["DATABASE_HOST"], port=self.app.config["DATABASE_PORT"], raise_on_warnings=True
        )
        try:
            cursor = conn.cursor()
            cursor.execute(
                    "CREATE DATABASE IF NOT EXISTS {} CHARACTER SET utf8".format(self.app.config["DATABASE_NAME"])
            )
            conn.commit()
        except:
            raise
        else:
            with self.DBManager(self.app) as connection:
                for model in sorted(lib.get_subclasses(lib.models.Model), key=lambda x: x.index):
                    model.setup_table(connection=connection)
        finally:
            conn.close()

    def update(self) -> None:
        """ Updates the database by checking on the internet for new files before committing them """
        self.app.notifier.set_value("Database update started on {}".format(datetime.datetime.now().strftime("%c")))
        self.app.notifier.clear()
        self.app.logger.info("Starting database update")
        card_parser = JSonCardParser(self.app)
        card_parser.check_update()
        try:
            self.__update(card_parser)
        except mysql.connector.errors.ProgrammingError as exc:
            if exc.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.setup_db()
                self.__update(card_parser)
            else:
                raise
        else:
            self.app.logger.info("Finished database update")
            self.app.notifier.set_value("Database update finished on {}".format(datetime.datetime.now().strftime("%c")))
            self.app.notifier.clear()
