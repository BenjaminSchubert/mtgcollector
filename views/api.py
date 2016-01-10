# -*- coding: utf-8 -*-
import os

import flask
import requests
from flask import send_from_directory

import mtgcollector
from lib import models

default_card_url = (
    "http://gatherer.wizards.com/Handlers/Image.ashx?size=small&type=card&"
    "name=The%20Ultimate%20Nightmare%20of%20Wizards%20of%20the%20Coast%20Customer%20Service&options="
)


@mtgcollector.app.route("/api/images/<card_id>")
def get_image(card_id):
    filename = mtgcollector.app.downloader.get_image_path(card_id)
    if not os.path.exists(os.path.join(mtgcollector.app.static_folder, filename)):
        mtgcollector.app.downloader.download_image(card_id, getattr(flask.g, "db"))

    return send_from_directory(os.path.dirname(filename), os.path.split(filename)[1])


@mtgcollector.app.route("/api/icons/<icon>")
def get_icon(icon):
    filename = mtgcollector.app.downloader.get_icon_path(icon)
    if not os.path.exists(os.path.join(mtgcollector.app.static_folder, filename)):
        mtgcollector.app.downloader.download_icon(icon)

    return send_from_directory(os.path.dirname(filename), icon)


@mtgcollector.app.route("/api/images/default.png")
def get_default_image():
    # TODO : factorize this
    filename = os.path.join("images", "default.png")
    if not os.path.exists(os.path.join(mtgcollector.app.static_folder, filename)):
        request = requests.get(default_card_url, stream=True)

        if request.status_code != requests.codes.ok:
            raise request.raise_for_status()

        os.makedirs(os.path.dirname(os.path.join(mtgcollector.app.static_folder, filename)), exist_ok=True)
        with open(os.path.join(mtgcollector.app.static_folder, filename), "wb") as _file_:
            for chunk in request.iter_content(chunk_size=1024):
                if chunk:  # this is to filter out keepalive chunks
                    _file_.write(chunk)

    return send_from_directory(os.path.join(mtgcollector.app.static_folder, "images"), "default.png")


@mtgcollector.app.route("/api/cards/<card_id>")
def get_card_info(card_id):
    card = models.Card.get(card_id)
    if len(card) == 1:
        return flask.jsonify(**card[0])
    elif len(card) > 1:
        mtgcollector.app.logger.error("Got multiple cards for %(card_id)s", dict(card_id=card_id))
        return flask.jsonify(**card[0])
    else:
        mtgcollector.app.logger.error("Got no information for card %(card_id)s", dict(card_id=card_id))
        flask.abort(404)
