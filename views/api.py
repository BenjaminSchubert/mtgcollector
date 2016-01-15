#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
RESTful API for mtgcollector
"""

import os

import flask
import werkzeug.wrappers
from flask import send_from_directory
from flask.ext.login import login_required, current_user

import mtgcollector
from lib import models

__author__ = "Benjamin Schubert, <ben.c.schubert@gmail.com>"


@mtgcollector.app.route("/api/images/<card_id>")
def get_image(card_id: int) -> werkzeug.wrappers.Response:
    """
    Get image for the given card

    :param card_id: card for which to get the image
    :return: an http response for the image
    """
    filename = mtgcollector.app.downloader.get_image_path(card_id)
    if not os.path.exists(os.path.join(mtgcollector.app.static_folder, filename)):
        mtgcollector.app.downloader.download_image(card_id, getattr(flask.g, "db"))

    return send_from_directory(os.path.dirname(filename), os.path.split(filename)[1])


@mtgcollector.app.route("/api/icons/<icon>")
def get_icon(icon: str) -> werkzeug.wrappers.Response:
    """
    Returns the image icon corresponding to the given name

    :param icon: icon name to fetch
    :return: an http response for the icon
    """
    filename = mtgcollector.app.downloader.get_icon_path(icon)
    if not os.path.exists(os.path.join(mtgcollector.app.static_folder, filename)):
        mtgcollector.app.downloader.download_icon(icon)

    return send_from_directory(os.path.dirname(filename), icon)


@mtgcollector.app.route("/api/cards/<card_id>")
def get_card_info(card_id: int) -> werkzeug.wrappers.Response:
    """
    Gets information about the given card

    :param card_id: card for which to fetch information
    :return: an http response containing the Card information, json formatted
    """
    card = models.Card.get(card_id)
    if len(card) == 1:
        return flask.jsonify(**card[0])
    elif len(card) > 1:
        mtgcollector.app.logger.error("Got multiple cards for %(card_id)s", dict(card_id=card_id))
        return flask.jsonify(**card[0])
    else:
        mtgcollector.app.logger.error("Got no information for card %(card_id)s", dict(card_id=card_id))
        flask.abort(404)


@mtgcollector.app.route("/api/collection/", methods=["POST"])
@login_required
def add_to_collection() -> werkzeug.wrappers.Response:
    """
    adds the given card to the collection.

    The 'normal' and 'foil' argument are expected in the POST request.
    They must be integers

    :return: a json formatted response containing the card_id, the new number of foil and normal iteration
    """
    card_id = flask.request.form.get("id", type=int)
    normal = flask.request.form.get('n_normal', type=int)
    foil = flask.request.form.get('n_foil', type=int)

    current_user.collection.insert(card_id=card_id, normal=normal, foil=foil)

    return flask.jsonify(card_id=card_id, normal=normal, foil=foil)


@mtgcollector.app.route("/api/decks", methods=["GET"])
@login_required
def list_decks() -> werkzeug.wrappers.Response:
    """ Gets the list of decks a given user has """
    return flask.jsonify(decks=current_user.decks.list())


@mtgcollector.app.route("/api/decks", methods=["POST"])
@login_required
def add_deck() -> werkzeug.wrappers.Response:
    """ adds a new deck with the given name """
    return flask.jsonify(dict(deck=current_user.decks.add(flask.request.form["name"])))


@mtgcollector.app.route("/api/decks/<name>", methods=["POST"])
@login_required
def modify_deck(name: str) -> werkzeug.wrappers.Response:
    """
    Allows the user to customize its deck

    The following POST data are checked :
        name : the new name for the deck
        index : the new user_index to give to the deck

    :param name: name of the deck to rename
    """
    new_name = flask.request.form.get("name")
    index = flask.request.form.get("index")

    if new_name:
        current_user.decks.rename(name, new_name)
    if index:
        current_user.decks.set_index(name, index)

    return ('', 200)


@mtgcollector.app.route("/api/decks/<name>/<card_id>", methods=["POST"])
@login_required
def add_card_to_deck(name: str, card_id: int) -> werkzeug.wrappers.Response:
    """
    Adds a new card to the given deck

    :param name: name of the deck to which to add the card
    :param card_id: id of the card to add
    :return: the number of card of this id now in the deck
    """
    number = flask.request.form.get('n_cards', type=int)
    side = bool(flask.request.form.get("side", type=int))

    if card_id is None or number is None or side is None:
        return flask.abort(400)

    return flask.jsonify(dict(card=current_user.decks.add_card(name, card_id, number, side)))


@mtgcollector.app.route("/api/decks/<name>", methods=["DELETE"])
@login_required
def delete_deck(name) -> werkzeug.wrappers.Response:
    """
    deletes the given deck

    :param name: name of the deck to delete
    :return: 200 OK on completion
    """
    current_user.decks.delete(name)
    return ('', 200)
