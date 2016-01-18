#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
These are the main views for MTGCollector
"""

import flask
import mysql.connector.errorcode
import mysql.connector.errors
import typing
import werkzeug.wrappers
from flask_login import current_user, login_required

import lib.db.maintenance
import views.api
import views.auth
import views.conf
from lib.forms import SearchForm, ImportJSonForm
from lib.models import Metacard, Card
from mtgcollector import app, lib


__author__ = "Benjamin Schubert, <ben.c.schubert@gmail.com>"


@app.before_request
def setup_db() -> typing.Union[werkzeug.wrappers.Response, None]:
    """ setups a db object before serving the user """
    try:
        flask.g.db = lib.db.get_connection(app)
    except (mysql.connector.errors.ProgrammingError, KeyError) as exc:
        if app.config.get("DATABASE_NAME") is None:
            if type(exc) == KeyError or exc.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                if flask.request.endpoint in ["install", "static"]:
                    return
                else:
                    return flask.redirect(flask.url_for("install"))
        else:
            db = lib.db.maintenance.MaintenanceDB(app)
            db.setup_db()
            app.update_db.set()

            if flask.request.endpoint != 'install':
                return flask.redirect(flask.url_for("install"))


# noinspection PyUnusedLocal
@app.teardown_request
def close_db(exception) -> None:
    """
    Closes the database no matter what before finishing handling the request

    :param exception: the exception if one was thrown
    """
    db = getattr(flask.g, 'db', None)
    if db is not None:
        db.close()


@app.route("/")
def index() -> werkzeug.wrappers.Response:
    """ Main page """
    if current_user.is_authenticated:
        return flask.redirect("collection")
    return flask.redirect("search")


@app.route("/search")
def search() -> werkzeug.wrappers.Response:
    """ Search page """
    form = SearchForm(current_user.is_authenticated, flask.request.args)
    form.csrf_enabled = False  # TODO : investigate why this is needed

    if form.validate() and flask.request.args:
        return flask.render_template("result.html", cards=Metacard.get_ids_where(
                user_id=current_user.get_id(), **form.data
        ))
    return flask.render_template(
        "search.html", form=form, id_="form-search", title="Search", method="get",
        css_classes="col-md-10 col-md-offset-1", active_page="search"
    )


@app.route("/card/<name>")
def card_versions(name: str) -> werkzeug.wrappers.Response:
    """
    version page

    :param name: card's name
    """
    return flask.render_template("result.html", cards=Card.get_versions(user_id=current_user.get_id(), name=name))


@app.route("/collection")
@login_required
def collection() -> werkzeug.wrappers.Response:
    """ Collection page"""
    return flask.render_template(
            "result.html", active_page="collection", cards=Card.get_collection(user_id=current_user.get_id())
    )


@app.route("/decks")
@login_required
def decks() -> werkzeug.wrappers.Response:
    """ Decks page """
    return flask.render_template("deck_list.html", active_page="decks", form=ImportJSonForm("Deck save"))


@app.route("/decks/<name>")
@login_required
def deck(name) -> werkzeug.wrappers.Response:
    """
    displays a deck

    :param name: the name of the deck to display
    """
    return flask.render_template(
            "deck_information.html", active_page="decks", cards=current_user.decks.get_cards(name), name=name
    )


@app.route("/updates")
def send_updates() -> werkzeug.wrappers.Response:
    """
    EventStream handling function to be able to send push notifications to the clients

    :return: a event-stream object to the client
    """
    def get_update():
        """
        Generator function for getting the events to push

        return: correctly formatted data to push to client
        """
        while True:
            try:
                yield "data: {}\n\n".format(app.notifier.wait_value(10))
            except TimeoutError:
                yield "data: ping\n\n"
    return flask.Response(get_update(), mimetype="text/event-stream")
