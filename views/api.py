# -*- coding: utf-8 -*-
import os

import flask
from flask import send_from_directory
from flask.ext.login import login_required, current_user

import mtgcollector
from lib import models


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


@mtgcollector.app.route("/api/collection/<card_id>", methods=["POST"])
@login_required
def add_to_collection(card_id):
    normal = flask.request.form.get('normal', type=int)
    foil = flask.request.form.get('foil', type=int)

    if normal == foil == 0:
        current_user.collection.delete(card_id=card_id)

    current_user.collection.insert(card_id=card_id, normal=normal, foil=foil)

    return flask.jsonify(card_id=card_id, normal=normal, foil=foil)


@mtgcollector.app.route("/api/collection/<card_id>", methods=["DELETE"])
@login_required
def remove_from_collection(card_id):
    current_user.collection.delete(card_id=card_id)
    return flask.jsonify(card_id=card_id)