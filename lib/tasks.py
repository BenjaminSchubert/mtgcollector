#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Background tasks utilities
"""

import os
import tempfile
import threading

import flask
import requests

import lib.db
import lib.db.maintenance
import lib.models


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class ImageHandler:
    """
    Card downloader, for caching and pre-caching
    """
    def __init__(self, app: flask.Flask):
        super().__init__()
        app.image_handler = self
        self.db = lib.db.maintenance.MaintenanceDB(app)
        self.download_folder = os.path.join(app.static_folder, "images")
        self.logger = app.logger

    def get_image_path(self, card_id: int) -> str:
        """
        Get's the card's image's storage path

        :param card_id:
        :return: image's storage location
        """
        if card_id == "default.png":
            return os.path.join(self.download_folder, card_id)
        data_folder_path = [str(card_id)[n] if len(str(card_id)) > n else "0" for n in range(4)]
        data_folder_path.append(str(card_id) + ".jpg")
        return os.path.join(self.download_folder, *data_folder_path)

    def get_icon_path(self, icon: str) -> str:
        """
        Returns the icon path for the given name

        :param icon: name of the icon
        :return: icon's storage location
        """
        return os.path.join(self.download_folder, "icons", icon)

    @staticmethod
    def download_item(url: str, file_path: str) -> None:
        """
        Downloads a file from the given url to the given file_path

        :param url: where to fetch the resource
        :param file_path: where to store the resource
        """
        request = requests.get(url, stream=True)

        if request.status_code != requests.codes.ok:
            raise request.raise_for_status()

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        temp_fd, path_name = tempfile.mkstemp(suffix=".tmp", prefix=file_path, dir=os.path.dirname(file_path))
        temp_file = os.fdopen(temp_fd, "wb")
        for chunk in request.iter_content(chunk_size=1024):
            if chunk:  # this is to filter out keepalive chunks
                temp_file.write(chunk)
        temp_file.close()

        if not os.path.exists(file_path):
            os.rename(path_name, file_path)
        else:
            os.remove(path_name)

    def download_image(self, image: int, connection) -> None:
        """
        Downloads the given image

        :param image: card_id of the card to download
        :param connection: database connection to obtain image information
        """
        if image == "default.png":
            url = lib.models.Card.get_default_image_url()
        else:
            url = lib.models.Card.get_image_url(image, logger=self.logger, connection=connection)
        file_path = self.get_image_path(image)
        self.download_item(url, file_path)

    def download_icon(self, icon: str) -> None:
        """
        Downloads the given icon

        :param icon: icon name to download
        """
        icon_name = icon.split(".")[0]
        if icon_name == "T":
            icon_name = "tap"
        elif icon_name == "Q":
            icon_name = "untap"
        url = "http://gatherer.wizards.com/Handlers/Image.ashx?size=small&name={}&type=symbol".format(icon_name)
        file_path = self.get_icon_path(icon)
        self.download_item(url, file_path)


class DBUpdater(threading.Thread):
    """
    Database updater. Waits for a signal and, on signal, tries to update the database

    :param app: flask application to obtain database information
    """
    def __init__(self, app: flask.Flask):
        super().__init__()
        self.db = lib.db.maintenance.MaintenanceDB(app)
        self.event = threading.Event()
        app.update_db = self.event
        self.daemon = True

    def run(self):
        """ Waits for a signal and updates the database when it gets it """
        try:
            while True:
                self.event.wait()
                self.event.clear()
                self.db.update()
        except KeyboardInterrupt:
            exit(0)
