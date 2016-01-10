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
        self.queue = qm'enfinueue.Queue()
        self.download_folder = os.path.join(app.static_folder, "images")
        self.setDaemon(True)
        self.rename_lock = threading.Lock()

    def get_image_path(self, card_id: int):
        data_folder_path = [str(card_id)[n] if len(str(card_id)) > n else "0" for n in range(4)]
        data_folder_path.append(str(card_id) + ".jpg")
        return os.path.join(self.app.static_folder, "images", *data_folder_path)

    def run(self):
        entry = self.queue.get()
        with self.db.db_manager(self.app) as conn:
            while True:
                self.download_image(entry, conn)
                entry = self.queue.get()

    def download_image(self, card_id: int, connection):
        url = lib.models.Card.get_image_url(card_id, logger=self.app.logger, connection=connection)
        request = requests.get(url, stream=True)

        if request.status_code != requests.codes.ok:
            raise request.raise_for_status()

        file_path = lib.db.get_image_path(self.app, card_id)
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
