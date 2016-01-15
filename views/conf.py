# -*- coding: utf-8 -*-

import flask
import mysql.connector
import mysql.connector.errorcode
import mysql.connector.errors
import werkzeug.routing
from flask import redirect, url_for, render_template
from flask.ext.login import login_required, login_user

import lib.db
import lib.db.maintenance
import lib.forms.install
import lib.models
from lib.conf import update_conf
from mtgcollector import app


def validate_conf(form):
    app.config.update({
        "DATABASE_USER": form.username.data,
        "DATABASE_HOST": form.host.data,
        "DATABASE_PASSWORD": form.password.data,
        "DATABASE_NAME": form.database.data,
        "DATABASE_PORT": form.port.data
    })

    db = lib.db.maintenance.MaintenanceDB(app)
    try:
        db.setup_db()
    except mysql.connector.errors.InterfaceError as exc:
        if exc.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
            form.host.errors.append("Could not connect to {} at port {}".format(form.host.data, form.port.data))
            raise werkzeug.routing.ValidationError()
    except mysql.connector.errors.ProgrammingError as exc:
        if exc.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            form.password.errors.append("Could not connect with these credentials. Are they correct ?")
            raise werkzeug.routing.ValidationError()
    finally:
        for value in app.config.copy().keys():
            if value.startswith("DATABASE"):
                app.config.pop(value)


def get_database_form():
    form = lib.forms.install.InstallationForm()
    if form.validate_on_submit():
        try:
            validate_conf(form)
        except werkzeug.routing.ValidationError:
            return render_template("form.html", form=form, id_="form-database-setup", title="Database Setup")

        update_conf(
            DATABASE_USER=form.username.data,
            DATABASE_PASSWORD=form.password.data,
            DATABASE_HOST=form.host.data,
            DATABASE_NAME=form.database.data,
            DATABASE_PORT=form.port.data
        )
        app.update_db.set()
        return redirect(url_for("install"))

    return render_template('form.html', form=form, id_="form-database", action=flask.url_for("install"))


def get_user_form():
    form = lib.forms.auth.RegisterForm()

    if form.validate_on_submit():
        user = lib.models.User(username=form.username.data, email=form.email.data, password=form.password.data).create()
        user.set_admin(True)
        login_user(user)
        return redirect(url_for("parameters"))

    return render_template('form.html', form=form, id_="form-admin", title="Admin Creation")


@app.route("/install", methods=['GET', 'POST'])
def install():
    # No db connection, it is not already setup
    if not getattr(flask.g, "db", None):
        return get_database_form()
    elif getattr(flask.g, "db") and not lib.models.User.get_users(limit=1):
        return get_user_form()
    else:
        return redirect(url_for("parameters"))


@app.route("/update", methods=['GET', 'POST'])
def update():
    app.update_db.set()
    return redirect(url_for("index"))


@app.route("/parameters", methods=['GET', 'POST'])
@login_required
def parameters():
    return render_template('parameters.html', active_page="parameters")
