#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Full test for the application
"""

import mysql.connector
from tests import LiveServerTestCase, DBConnectionMixin


class IntegrationTest(LiveServerTestCase):
    def tearDown(self):
        """ Cleans up everything at the end of each test """
        conn = mysql.connector.connect(
            user=DBConnectionMixin.DATABASE_USER, password=DBConnectionMixin.DATABASE_PASSWORD,
            host=DBConnectionMixin.DATABASE_HOST, port=DBConnectionMixin.DATABASE_PORT
        )
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS {}".format(DBConnectionMixin.DATABASE_NAME))
        conn.commit()
        conn.close()
        super().tearDown()

    def test_complete(self):
        """ Tests that everything more or less works as it should """
        pass
