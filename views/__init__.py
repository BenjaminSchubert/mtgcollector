# -*- coding: utf-8 -*-
import os

import flask
import mysql.connector.errors
import mysql.connector.errorcode

from mtgcollector import app, lib
import views.conf
import views.api
import views.auth


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/search")
def search():
    return flask.render_template("search.html")


@app.before_request
def setup_db():
    try:
        flask.g.db = lib.db.get_connection(app)
    except (mysql.connector.errors.ProgrammingError, KeyError) as exc:
        if type(exc) == KeyError or exc.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            if flask.request.endpoint in ["install", "static"]:
                return
            else:
                return flask.redirect(flask.url_for("install"))


# noinspection PyUnusedLocal
@app.teardown_request
def close_db(exception):
    db = getattr(flask.g, 'db', None)
    if db is not None:
        db.close()
