# -*- coding: utf-8 -*-
from io import BytesIO
import json
import os
import re
import zipfile

import flask
import requests
import requests.exceptions


class CardUpdater:
    def __init__(self, app: flask.Flask):
        self.app = app

    def latest_version(self) -> str:
        current_version = "0"

        os.makedirs(os.path.join(self.app.static_folder, "downloads"), exist_ok=True)
        for _file in os.listdir(os.path.join(self.app.static_folder, "downloads")):
            match = re.match(r"cards-([0-9\.]+?)\.json", _file)
            if match is not None and match.group(1) > current_version:
                current_version = match.group(1)

        if current_version != "0":
            return os.path.join(self.app.static_folder, "downloads", "cards-{}.json".format(current_version))

        raise Exception("No Version were found")

    def __get_latest_version(self) -> str:
        try:
            request = requests.get("http://mtgjson.com/json/version-full.json")
            if request.status_code == requests.codes.ok:
                return json.loads(request.content.decode("UTF-8"))["version"]
        except requests.exceptions.ConnectionError:
            return self.latest_version()

    def __download_latest_version(self, version: str) -> str:
        request = requests.get("http://mtgjson.com/json/AllSets-x.json.zip", stream=True)
        if request.status_code != requests.codes.ok:
            raise request.raise_for_status()

        os.makedirs(os.path.join(self.app.static_folder, "downloads"), exist_ok=True)

        with BytesIO() as zipped_data:
            for chunk in request.iter_content(chunk_size=4096):
                if chunk:
                    zipped_data.write(chunk)
            zipped_data.seek(0)

            zipped = zipfile.ZipFile(zipped_data)

            with open(os.path.join(self.app.static_folder, "downloads", "cards-{}.json".format(version)), "wb") as _file:
                _file.write(zipped.read(zipped.namelist()[0]))

        return os.path.join(self.app.static_folder, "downloads", "cards-{}.json".format(version))

    def check_update(self) -> bool:
        latest_remote_version = str(self.__get_latest_version())
        current_version = "0"

        os.makedirs(os.path.join(self.app.static_folder, "downloads"), exist_ok=True)
        for _file in os.listdir(os.path.join(self.app.static_folder, "downloads")):
            match = re.match(r"cards-([0-9\.]+)\.json", _file)
            if match is not None and match.group(1) > current_version:
                current_version = match.group(1)

        if current_version < latest_remote_version:
            self.__download_latest_version(latest_remote_version)
            return True

        return False
