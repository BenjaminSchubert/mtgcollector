# -*- coding: utf-8 -*-
import os
import queue
import threading

import flask
import requests

import lib.db
import lib.db.maintenance


class Downloader(threading.Thread):
    def __init__(self, app: flask.Flask):
        super().__init__()
        app.download = queue.Queue()
        self.db = lib.db.maintenance.MaintenanceDB(app)
        self.app = app
        self.queue = app.download
        self.download_folder = os.path.join(app.static_folder, "images")

    def run(self):
        entry = self.queue.get()
        with self.db.db_manager(self.app) as conn:
            while True:
                self.download_image(entry, conn)
                entry = self.queue.get()

    def download_image(self, card_id: int, connection):
        url = lib.db.get_image_url(card_id, connection=connection)
        request = requests.get(url, stream=True)

        if request.status_code != requests.codes.ok:
            raise request.raise_for_status()

        file_path = lib.db.get_image_path(self.app, card_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as _file_:
            for chunk in request.iter_content(chunk_size=1024):
                if chunk:  # this is to filter out keepalive chunks
                    _file_.write(chunk)


class DBUpdater(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.db = lib.db.maintenance.MaintenanceDB(app)
        self.event = threading.Event()
        app.update_db = self.event

    def run(self):
        while True:
            self.event.wait()
            self.event.clear()
            self.db.update()
