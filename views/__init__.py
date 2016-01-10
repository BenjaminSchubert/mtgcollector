# -*- coding: utf-8 -*-

import flask
import mysql.connector.errors
import mysql.connector.errorcode
from flask_login import current_user

from lib.forms.search import SearchForm
from lib.models import Metacard
from mtgcollector import app, lib
import lib.db.maintenance

import views.conf
import views.api
import views.auth


@app.route("/")
def index():
    if current_user.is_authenticated:
        return flask.render_template("collection.html")
    return flask.render_template("search.html")


@app.route("/search")
def search():
    form = SearchForm(flask.request.args)
    form.csrf_enabled = False

    if form.validate() and flask.request.args:
        return flask.render_template("result.html", cards=Metacard.get_ids_where(
                user_id=current_user.get_id(), **form.data.copy()
        ))
    return flask.render_template("form.html", form=form, title="Search", method="get")


@app.before_request
def setup_db():
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
            # TODO first check if we can connect and create the database
            db = lib.db.maintenance.MaintenanceDB(app)
            db.setup_db()
            app.update_db.set()

            if flask.request.endpoint != 'install':
                return flask.redirect(flask.url_for("install"))

            # TODO then if not successful redirect to the setup page asking for correct values


# noinspection PyUnusedLocal
@app.teardown_request
def close_db(exception):
    db = getattr(flask.g, 'db', None)
    if db is not None:
        db.close()


@app.route("/updates")
def send_updates():
    def get_update():
        while True:
            try:
                yield "data: {}\n\n".format(app.notifier.wait_value(10))
            except TimeoutError:
                yield "data: ping\n\n"
    return flask.Response(get_update(), mimetype="text/event-stream")
