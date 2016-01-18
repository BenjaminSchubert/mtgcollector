#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Tests the json card parser
"""

import os
import requests.exceptions
import responses
import tempfile
import unittest
import zipfile

from lib.parser import JSonCardParser, NoJSonFileException
from tests import download_file_resources, DownloadProxy


class TestJSonCardParser(unittest.TestCase):
    """
    Tests the json card parser
    """
    class DummyFlask:
        """
        A dummy Flask application having only a folder
        """
        class DummyLogger:
            """
            A dummy logger for tests
            """
            def error(self, dummy):
                pass

        def __init__(self, folder):
            self.static_folder = folder
            self.logger = self.DummyLogger()

    def add_to_response_version_correct(self, response):
        """
        Adds a new version to the response wrapper

        :param response: the response to which to add the version
        """
        response.add(
                responses.GET, self.parser.last_version_check_path(), status=200,
                body='{{"version":"{}"}}'.format("3.3.3"), content_type="application/json"
        )

    def add_file_as_version(self, version="3.3.3"):
        """
        Adds a new file with a given version to the local directory path

        :param version: version of the file to add
        """
        with open(download_file_resources, "rb") as _zip:
            with open(self.full_path_format.format(version), "wb") as destination:
                zip_file = zipfile.ZipFile(_zip)
                destination.write(zip_file.read(zip_file.namelist()[0]))

    def setUp(self):
        """ Isolates the running test in a new directory """
        self.directory = tempfile.TemporaryDirectory()
        # noinspection PyTypeChecker
        self.parser = JSonCardParser(self.DummyFlask(self.directory.name))
        self.file_format = "cards-{}.json"
        self.full_path_format = os.path.join(self.directory.name, "downloads", self.file_format)

    def tearDown(self):
        """ Cleans all files used during the test """
        self.directory.cleanup()

    def test_latest_remote_version(self):
        """ Checks correct retrieval of the latest version """
        with responses.RequestsMock() as response:
            self.add_to_response_version_correct(response)
            self.assertRegexpMatches(self.parser.get_latest_remote_version(), r"3.3.3")

        with responses.RequestsMock() as response:
            response.add(responses.GET, self.parser.last_version_check_path(), status=404)
            self.assertRaises(NoJSonFileException, self.parser.get_latest_remote_version)

        with responses.RequestsMock() as response:
            response.add(
                responses.GET, self.parser.last_version_check_path(),
                body=requests.exceptions.ConnectionError("No Connection")
            )
            self.assertRaises(NoJSonFileException, self.parser.get_latest_remote_version)

    def test_local_version(self):
        """ Checks that the version comparison works locally """
        v1 = "3.2.1"
        v2 = "2.4.2"
        v3 = "4.0.0"

        self.assertRaises(NoJSonFileException, self.parser.get_latest_local_version)

        open(self.full_path_format.format(v1), "a").close()
        self.assertEqual(self.parser.get_latest_local_version(), v1)

        open(self.full_path_format.format(v2), "a").close()
        self.assertEqual(self.parser.get_latest_local_version(), v1)

        open(self.full_path_format.format(v3), "a").close()
        self.assertEqual(self.parser.get_latest_local_version(), v3)

    def test_download_version_file_not_found(self):
        """ Checks that failing to find a newer version online does not trigger an update """
        with responses.RequestsMock() as response:
            self.add_to_response_version_correct(response)
            response.add(
                responses.GET, self.parser.json_download_file_path(), status=404
            )
            self.assertFalse(self.parser.check_update())

    def test_download_version_when_empty(self):
        """ Checks that the check works when there are no local files beforehand """
        with DownloadProxy(self.parser):
            self.assertTrue(self.parser.check_update())

    def test_download_version_no_new_available(self):
        """ Checks that there are no downloads when no new version is available """
        with responses.RequestsMock() as response:
            self.add_to_response_version_correct(response)
            self.add_file_as_version()
            self.assertFalse(self.parser.check_update())

    def test_get_new_version(self):
        """ Checks the retrieval of a new version """
        with DownloadProxy(self.parser):
            self.add_file_as_version(version="3.3.2")
            self.assertTrue(self.parser.check_update())
