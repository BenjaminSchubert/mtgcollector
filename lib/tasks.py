# -*- coding: utf-8 -*-
import os
import queue
import tempfile
import threading

import flask
import requests

import lib.db
import lib.models
import lib.db.maintenance


class Downloader(threading.Thread):
    def __init__(self, app: flask.Flask):
        super().__init__()
        app.downloader = self
        self.db = lib.db.maintenance.MaintenanceDB(app)
        self.app = app
        self.queue = queue.Queue()
        self.download_folder = os.path.join(app.static_folder, "images")
        self.setDaemon(True)
        self.rename_lock = threading.Lock()

    def get_image_path(self, card_id: int):
        data_folder_path = [str(card_id)[n] if len(str(card_id)) > n else "0" for n in range(4)]
        data_folder_path.append(str(card_id) + ".jpg")
        return os.path.join(self.app.static_folder, "images", *data_folder_path)

    def get_icon_path(self, icon: str):
        return os.path.join(self.app.static_folder, "images", "icons", icon)

    def run(self):
        entry = self.queue.get()
        with self.db.db_manager(self.app) as conn:
            while True:
                self.download_image(entry, conn)
                entry = self.queue.get()

    def download_item(self, url: str, file_path: str):
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

        with self.rename_lock:
            if not os.path.exists(file_path):
                os.rename(path_name, file_path)
            else:
                os.remove(path_name)

    def download_image(self, image, connection):
        url = lib.models.Card.get_image_url(image, logger=self.app.logger, connection=connection)
        file_path = self.get_image_path(image)
        self.download_item(url, file_path)

    def download_icon(self, icon):
        icon_name = icon.split(".")[0]
        if icon_name == "T":
            icon_name = "tap"
        elif icon_name == "Q":
            icon_name = "untap"
        url = "http://gatherer.wizards.com/Handlers/Image.ashx?size=small&name={}&type=symbol".format(icon_name)
        file_path = self.get_icon_path(icon)
        self.download_item(url, file_path)


class DBUpdater(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.db = lib.db.maintenance.MaintenanceDB(app)
        self.event = threading.Event()
        app.update_db = self.event
        self.setDaemon(True)

    def run(self):
        while True:
            self.event.wait()
            self.event.clear()
            self.db.update()
