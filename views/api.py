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
from lib.forms import AddToCollectionForm, RenameDeck, ChangeDeckIndex, AddToDeckForm

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
    return flask.jsonify(**models.Card.get(card_id)[0])


@mtgcollector.app.route("/api/collection/<card_id>", methods=["POST"])
@login_required
def add_to_collection(card_id) -> werkzeug.wrappers.Response:
    """
    adds the given card to the collection.

    The 'normal' and 'foil' argument are expected in the POST request.
    They must be integers

    :param card_id: id of the card to add to the collection
    """
    form = AddToCollectionForm()

    if form.validate_on_submit():
        current_user.collection.insert(card_id=card_id, **form.data)
        return ('', 200)
    else:
        return (form.errors, 400)


@mtgcollector.app.route("/api/decks", methods=["GET"])
@login_required
def list_decks() -> werkzeug.wrappers.Response:
    """ Gets the list of decks a given user has """
    return flask.jsonify(decks=current_user.decks.list())


@mtgcollector.app.route("/api/decks/<name>", methods=["POST"])
@login_required
def create_deck(name: str) -> werkzeug.wrappers.Response:
    """
    Creates a new deck for the authenticated user

    :param name: name of the deck to create
    """
    current_user.decks.add(name)
    return ('', 200)


@mtgcollector.app.route("/api/decks/<name>/rename", methods=["POST"])
@login_required
def rename_deck(name: str) -> werkzeug.wrappers.Response:
    """
    Renames the deck given in the url with the new name given in POST parameters

    :param name: name of the deck to rename
    """
    form = RenameDeck()
    if form.validate_on_submit():
        current_user.decks.rename(name, form.data["name"])
        return ('', 200)
    return (form.errors, 400)


@mtgcollector.app.route("/api/decks/<name>/index", methods=["POST"])
@login_required
def change_deck_index(name: str) -> werkzeug.wrappers.Response:
    """
    Changes the deck user index to the given value

    :param name: name of the deck for which to change the index
    """
    form = ChangeDeckIndex()
    if form.validate_on_submit():
        current_user.decks.set_index(name, form.data["index"])
        return ('', 200)
    return (form.errors, 400)


@mtgcollector.app.route("/api/decks/<name>/<card_id>", methods=["POST"])
@login_required
def add_card_to_deck(name: str, card_id: int) -> werkzeug.wrappers.Response:
    """
    Adds a new card to the given deck

    :param name: name of the deck to which to add the card
    :param card_id: id of the card to add
    :return: the number of card of this id now in the deck
    """
    form = AddToDeckForm()
    if form.validate_on_submit():
        current_user.decks.add_card(name, card_id, **form.data)
        return ('', 200)
    return (form.errors, 400)


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
