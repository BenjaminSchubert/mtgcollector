#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
An update handler and card parser for cards retrieved on mtgjson.com
"""

import datetime
import json
import os
import re
import zipfile
from io import BytesIO

import flask
import requests
import requests.exceptions
import typing

from lib.models import Edition, Metacard, Card, Format
from lib.models import LegalInFormat

CardList = typing.Dict[str, typing.Dict[str, typing.Union[str, typing.List]]]


class NoJSonFileException(Exception):
    """
    Exception for when a json file can't be downloaded from the internet
    """


class JSonCardParser:
    """
    A parser for fetching card information from mtgjson.com
    """
    def __init__(self, app: flask.Flask):
        self.__app = app
        self.__editions = set()  # type: typing.Set[Edition]
        self.__metacards = set()  # type: typing.Set[Metacard]
        self.__cards = set()  # type: typing.Set[Card]
        self.__formats = set()  # type: typing.Set[Format]
        self.__legal_in_format = set()  # type: typing.Set[LegalInFormat]
        self.__json = None  # type: CardList
        self.__pending_update = False  # type: bool
        self.download_directory = os.path.join(self.__app.static_folder, "downloads")
        os.makedirs(os.path.join(self.download_directory), exist_ok=True)
        self.__full_path_format = os.path.join(self.download_directory, "cards-{}.json")

    @staticmethod
    def last_version_check_path():
        """ The download url for the version of the json file """
        return "http://mtgjson.com/json/version-full.json"

    @staticmethod
    def json_download_file_path():
        """ The download url for the json file """
        return "http://mtgjson.com/json/AllSets-x.json.zip"

    def load_file(self) -> CardList:
        """ loads the json data in memory """
        with open(self.__full_path_format.format(self.get_latest_local_version()), encoding="utf8") as _file:
            self.__json = json.load(_file)

    def check_update(self) -> bool:
        """
        Checks whether there is a new set of cards available or not
        """
        latest_remote_version = self.get_latest_remote_version()
        try:
            latest_local_version = self.get_latest_local_version()
        except NoJSonFileException:
            latest_local_version = "0"

        if latest_local_version < latest_remote_version:
            try:
                self.__download_latest_version(latest_remote_version)
            except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
                # TODO : log this error
                pass
            else:
                return True
        return False

    def __load_data(self):
        for edition in self.json.values():
            self.__editions.add(Edition(
                code=edition.get("code"),
                name=edition.get("name"),
                type=edition.get("type"),
                releaseDate=datetime.datetime.strptime(edition.get("releaseDate"), "%Y-%m-%d"),
                block=edition.get("block", None)
            ))

            for metacard in edition.get("cards"):
                if metacard.get("types") is None and "token" in metacard.get("name"):
                    metacard["types"] = ["Token"]

                self.__metacards.add(Metacard(
                    name=metacard.get("name"),
                    types=set(metacard.get("types")),
                    subtypes=set(metacard.get("subtypes")) if metacard.get("subtypes") else None,
                    supertypes=set(metacard.get("supertypes")) if metacard.get("supertypes") else None,
                    manaCost=metacard.get("manaCost"),
                    power=metacard.get("power"),
                    toughness=metacard.get("toughness"),
                    colors=metacard.get("colors"),
                    cmc=metacard.get("cmc", 0),
                    text=metacard.get("originalText"),
                ))

                version = ""
                counter = -1

                while metacard.get("imageName")[counter].isdigit():
                    version = metacard.get("imageName")[counter] + version
                    counter -= 1

                if counter == -1:
                    version = 0

                self.__cards.add(Card(
                    name=metacard.get("name"),
                    multiverseid=metacard.get("multiverseid"),
                    rarity=metacard.get("rarity"),
                    number=metacard.get("number", 0),
                    version=version,
                    edition=edition.get("code"),
                    artist=metacard.get("artist"),
                    flavor=metacard.get("flavor")
                ))

                for legality in metacard.get("legalities", []):
                    if not legality["format"].endswith("Block"):
                        self.__formats.add(Format(
                            legality["format"]
                        ))
                        self.__legal_in_format.add(LegalInFormat(
                            metacard.get("name"), legality["format"], legality["legality"]
                        ))

    def __download_latest_version(self, version: str) -> str:
        request = requests.get(self.json_download_file_path(), stream=True)
        if request.status_code != requests.codes.ok:
            raise request.raise_for_status()

        with BytesIO() as zipped_data:
            for chunk in request.iter_content(chunk_size=4096):
                if chunk:
                    zipped_data.write(chunk)

            zipped_data.seek(0)

            zipped = zipfile.ZipFile(zipped_data)

            with open(self.__full_path_format.format(version), "wb") as _file:
                _file.write(zipped.read(zipped.namelist()[0]))

    def get_latest_local_version(self) -> str:
        """ the latest local version for the json file """
        current_version = "0"

        for _file in os.listdir(self.download_directory):
            match = re.match(r"cards-([0-9\.]+?)\.json", _file)
            if match is not None and match.group(1) > current_version:
                current_version = match.group(1)

        if current_version != "0":
            return os.path.join(current_version)

        raise NoJSonFileException("No downloaded version were found")

    def get_latest_remote_version(self):
        """ The latest available version for the json file """
        try:
            request = requests.get(self.last_version_check_path())
        except requests.exceptions.ConnectionError:
            return self.get_latest_local_version()
        else:
            if request.status_code == requests.codes.ok:
                return json.loads(request.content.decode("UTF-8"))["version"]
            else:
                return self.get_latest_local_version()

    @property
    def json(self) -> CardList:
        """ Json loaded from the file"""
        if self.__json is None or self.__pending_update:
            self.load_file()
        return self.__json

    @property
    def editions(self) -> typing.Set[Edition]:
        """ Set of all editions retrieved from the file"""
        if len(self.__editions) == 0 or self.__pending_update:
            self.__load_data()
        return self.__editions

    @property
    def metacards(self) -> typing.Set[Metacard]:
        """ Set of all metacards retrieved from the file """
        if self.__metacards is None or self.__pending_update:
            self.__load_data()
        return self.__metacards

    @property
    def cards(self):
        """ Set of all cards retrieved from the file """
        if self.__cards is None or self.__pending_update:
            self.__load_data()
        return self.__cards

    @property
    def formats(self):
        """ Set of all tournaments retrieved from the file """
        if self.__formats is None or self.__pending_update:
            self.__load_data()
        return self.__formats

    @property
    def legal_in_format(self):
        """ Set of all legalities """
        if self.__legal_in_format is None or self.__pending_update:
            self.__load_data()
        return self.__legal_in_format
