#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Base classes for running tests in MTGCollector
"""

import abc
import flask
import multiprocessing
import os

import mysql.connector
import responses
import tempfile
import unittest
from typing import Iterable

import shutil

import mtgcollector
from mtgcollector import setup_app

download_file_resources = os.path.join(os.path.dirname(__file__), "resources", "AllSets-x.json.zip")


class DBConnectionMixin:
    """
    This mixin gives multiple helpers for dealing with database creation and deletion. It also take cares of setting
    default values if some are not provided in environment variables
    """
    DATABASE_USER = os.environ.get("MTG_TEST_DB_USER", "root")
    DATABASE_PASSWORD = os.environ.get("MTG_TEST_DB_PASSWORD", "")
    DATABASE_HOST = os.environ.get("MTG_TEST_DB_HOST", "127.0.0.1")
    DATABASE_PORT = os.environ.get("MTG_TEST_DB_PORT", 3306)
    DATABASE_NAME = os.environ.get("MTG_TEST_DB_NAME", "mtg_test")
    SERVER_PORT = os.environ.get("MTG_TEST_SERVER_PORT", 5050)

    @classmethod
    def get_connection(cls, database: str=None):
        """
        Creates a connection to the given mysql server

        :param database: if not None, will directly connect to this database
        :return: a connection to the database
        """
        kwargs = {
            "user": cls.DATABASE_USER,
            "password": cls.DATABASE_PASSWORD,
            "host": cls.DATABASE_HOST,
            "port": cls.DATABASE_PORT,
            "raise_on_warnings": True
        }
        if database:
            kwargs["database"] = database
        return mysql.connector.connect(**kwargs)

    @classmethod
    def drop_database(cls):
        """ Completely destroys the database """
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute("DROP DATABASE {}".format(cls.DATABASE_NAME))
            conn.commit()
        finally:
            if conn is not None:
                conn.close()

    @classmethod
    def create_database(cls):
        """ Creates the needed database """
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE {} CHARACTER SET utf8".format(cls.DATABASE_NAME))
            conn.commit()
        finally:
            if conn is not None:
                conn.close()


class ApplicationContextWrapper(unittest.TestCase):
    """
    Wraps flask application context in order to avoid wrong access to flask.g
    """
    class DummyG:
        """
        A dummy class emulating g behavior
        """
        db = None

    old_g = None

    @classmethod
    def setUpClass(cls):
        """ Replaces flask.g with a dummy representation of it """
        super().setUpClass()
        cls.old_g = flask.g
        flask.g = cls.DummyG()

    @classmethod
    def tearDownClass(cls):
        """ Restores the old g from before the tests """
        super().setUpClass()
        flask.g = cls.old_g


class TestCaseWithDB(DBConnectionMixin, ApplicationContextWrapper, metaclass=abc.ABCMeta):
    """
    Creates some tables before tests are run, empties them between tests and destroy the database at the end
    """
    @classmethod
    @abc.abstractmethod
    def table_creation_commands(cls) -> Iterable[str]:
        """ list of commands to create necessary tables """

    @classmethod
    @abc.abstractmethod
    def tables_to_truncate(cls) -> Iterable[str]:
        """ list of tables to empty """
        with cls.get_connection(cls.DATABASE_NAME) as connection:
            cursor = connection.cursor()
            for command in cls.table_creation_commands():
                cursor.execute(command)

    @classmethod
    def setUpClass(cls):
        """ Creates the database """
        super().setUpClass()
        cls.create_database()
        conn = None
        try:
            conn = cls.get_connection(cls.DATABASE_NAME)
            cursor = conn.cursor()
            for command in cls.table_creation_commands():
                cursor.execute(command)
        finally:
            if conn is not None:
                conn.close()

    @classmethod
    def tearDownClass(cls):
        """ Drops the database """
        cls.drop_database()
        super().tearDownClass()

    def setUp(self):
        """ Puts a database connection in the flask.g.db object """
        super().setUp()
        flask.g.db = self.get_connection(database=self.DATABASE_NAME)

    def tearDown(self):
        """ Truncates all tables defined and reset the flask.g.db object """
        cursor = flask.g.db.cursor()
        for table in self.tables_to_truncate():
            cursor.execute("TRUNCATE TABLE {}".format(table))
        flask.g.db.commit()
        flask.g.db.close()
        flask.g.db = None
        super().tearDown()


class DownloadProxy(responses.RequestsMock, metaclass=abc.ABCMeta):
    """
    Proxy to prevent tests to download real files from the internet

    By default, it will only catch calls to mtgjson version and download file paths
    """
    # noinspection PyUnresolvedReferences
    def __init__(self, parser):
        super().__init__()
        self.add(
                responses.GET, parser.last_version_check_path(), status=200,
                body='{{"version":"{}"}}'.format("3.3.3"), content_type="application/json"
        )
        self.add(
                responses.GET, parser.json_download_file_path(), status=200, content_type="application/zip",
                body=open(download_file_resources, "rb").read()
            )


class LiveServerTestCase(unittest.TestCase):
    """
    Base class to run tests with a flask server operating
    """
    class LiveServer(multiprocessing.Process):
        """
        Live server Process, to allow tests to be run from the main process
        """
        def __init__(self, directory):
            super().__init__()
            self.directory = directory

        def run(self):
            """ Creates flask app and setups it before launching it """
            os.environ["MTG_COLLECTOR_CONFIG"] = os.path.join(self.directory, "config.cfg")
            mtgcollector.app.static_folder = self.directory
            mtgcollector.app.config.from_object(TestCaseWithDB)
            setup_app(mtgcollector.app)
            mtgcollector.app.run(debug=True, port=TestCaseWithDB.SERVER_PORT, use_reloader=False)

    def setUp(self):
        """ Starts a server before each test. In another temporary directory to completely isolate tests """
        self.directory = tempfile.TemporaryDirectory()

        # copy all assets to the temporary directory
        for _dir in os.listdir(mtgcollector.app.static_folder):
            shutil.copytree(os.path.join(mtgcollector.app.static_folder, _dir), os.path.join(self.directory.name, _dir))

        self._process = self.LiveServer(self.directory.name)
        self._process.start()

    def tearDown(self):
        """ Kills the server and deletes the temporary directory """
        self._process.terminate()
        self.directory.cleanup()
