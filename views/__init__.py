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
from lib.forms.search import SearchForm
from lib.models import Metacard
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
    form.csrf_enabled = False

    if form.validate() and flask.request.args:
        return flask.render_template("result.html", cards=Metacard.get_ids_where(
                user_id=current_user.get_id(), **form.data
        ))
    return flask.render_template(
        "search.html", form=form, id_="form-search", title="Search", method="get",
        css_classes="col-md-10 col-md-offset-1"
    )


@app.route("/collection")
@login_required
def collection() -> werkzeug.wrappers.Response:
    """ Collection page"""
    return flask.render_template("result.html", cards=Metacard.get_collection(user_id=current_user.get_id()))


@app.route("/decks")
@login_required
def deck_list() -> werkzeug.wrappers.Response:
    """ Decks page """
    return flask.render_template("deck_list.html")


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
