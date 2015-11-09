#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This module tests entry of the data into the database
"""

import mysql.connector
import tempfile
import unittest
from flask import Flask

from lib.db.maintenance import MaintenanceDB
from lib.parser import JSonCardParser
from tests import DBConnectionMixin, DownloadProxy


class TestMaintenanceDB(unittest.TestCase):
    """
    Tests the maintenance database
    """
    def setUp(self):
        """ Creates a temporary directory and sets an app up before running """
        self.directory = tempfile.TemporaryDirectory()
        self.app = Flask(__name__, static_folder=self.directory.name)
        self.app.config.from_object(DBConnectionMixin)
        self.maintenance = MaintenanceDB(self.app)
        self.maintenance.setup_db()

    def tearDown(self):
        """ Connects to the database and empties it """
        conn = mysql.connector.connect(
            user=self.app.config["DATABASE_USER"], password=self.app.config["DATABASE_PASSWORD"],
            host=self.app.config["DATABASE_HOST"], port=self.app.config["DATABASE_PORT"]
        )
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS {}".format(self.app.config["DATABASE_NAME"]))
        conn.commit()
        conn.close()
        self.directory.cleanup()

    def test_update_empty_db(self):
        """ Try loading the test data in the database """
        with DownloadProxy(JSonCardParser(self.app)):
            self.maintenance.update()
