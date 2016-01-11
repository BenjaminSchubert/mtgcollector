#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Full test for the application
"""

import mysql.connector
import requests
import selenium.webdriver

from tests import LiveServerTestCase, DBConnectionMixin
from tests.forms import InstallForm, AdminForm

class IntegrationTest(LiveServerTestCase):
    def drop_database(self):
        conn = mysql.connector.connect(
            user=DBConnectionMixin.DATABASE_USER, password=DBConnectionMixin.DATABASE_PASSWORD,
            host=DBConnectionMixin.DATABASE_HOST, port=DBConnectionMixin.DATABASE_PORT
        )
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS {}".format(DBConnectionMixin.DATABASE_NAME))
        conn.commit()
        conn.close()

    def tearDown(self):
        """ Cleans up everything at the end of each test """
        self.browser.close()
        self.drop_database()
        super().tearDown()

    def setUp(self):
        super().setUp()
        self.drop_database()
        self.links = set()
        self.browser = selenium.webdriver.Firefox()

    def find_links(self):
        href_links = self.browser.find_elements_by_xpath("//*[@href]")
        source_links = self.browser.find_elements_by_xpath("//*[@src]")

        self.links.update([link.get_attribute("href") for link in href_links])
        self.links.update([link.get_attribute("src") for link in source_links])

    def check_no_40X(self):
        for link in self.links:
            status = requests.get(link).status_code
            if link.split("/")[-1] in {"logout", "parameters", "decks"}:
                self.assertEqual(401, status, "{} have been accessed but shouldn't have".format(link))
            else:
                self.assertGreaterEqual(400, status, "{} sent back {} error".format(link, status))

    def test_complete(self):
        """ Tests that everything more or less works as it should """
        self.browser.get("localhost:{}".format(DBConnectionMixin.SERVER_PORT))

        # we should be redirected to install
        self.assertRegex(self.browser.current_url, r"/install$")
        self.find_links()

        # test the installation form
        InstallForm().test(self, self.browser)
        self.assertRegex(self.browser.current_url, r"/install$")
        AdminForm().test(self, self.browser)
        self.find_links()
        self.assertRegex(self.browser.current_url, r"/parameters$")

        self.check_no_40X()
