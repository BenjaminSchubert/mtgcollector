import abc
import flask
import os

import mysql.connector
from typing import Iterable


class TestCaseWithDB(metaclass=abc.ABCMeta):
    class DummyG:
        db = None

    db_user = os.environ.get("MTG_TEST_DB_USER", "root")
    db_password = os.environ.get("MTG_TEST_DB_PASSWORD", "")
    db_host = os.environ.get("MTG_TEST_DB_HOST", "127.0.0.1")
    db_port = os.environ.get("MTG_TEST_DB_PORT", 3306)
    db_name = os.environ.get("MTG_TEST_DB_NAME", "mtg_test")
    old_g = None

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.conn = None

    @classmethod
    @abc.abstractmethod
    def table_creation_commands(cls) -> Iterable[str]:
        """ list of commands to create necessary tables for the test """

    @property
    @abc.abstractmethod
    def tables_to_truncate(self) -> Iterable[str]:
        """ list of tables to empty after each tests """

    @classmethod
    def get_connection(cls, database=None):
        kwargs = {
            "user": cls.db_user,
            "password": cls.db_password,
            "host": cls.db_host,
            "port": cls.db_port,
            "raise_on_warnings": True
        }
        if database:
            kwargs["database"] = database
        return mysql.connector.connect(**kwargs)

    @classmethod
    def setUpClass(cls):
        flask.g = cls.DummyG()
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE {} CHARACTER SET utf8".format(cls.db_name))
        cursor.execute("USE {}".format(cls.db_name))
        for command in cls.table_creation_commands():
            cursor.execute(command)
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE {}".format(cls.db_name))
        conn.commit()
        conn.close()
        flask.g = cls.old_g

    def setUp(self):
        flask.g.db = self.get_connection(database=self.db_name)

    def tearDown(self):
        cursor = flask.g.db.cursor()
        for table in self.tables_to_truncate:
            cursor.execute("TRUNCATE TABLE {}".format(table))
        flask.g.db.commit()
        flask.g.db.close()
        flask.g.db = None
