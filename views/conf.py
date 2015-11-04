# -*- coding: utf-8 -*-
import mysql.connector
import mysql.connector.errors
import mysql.connector.errorcode
import werkzeug.routing
from flask import redirect, url_for, render_template

import lib.db.maintenance
import views.forms.install
from mtgcollector import app, CONF_PATH


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
            form.username.errors.append("Could not connect with these credentials. Are they correct ?")
            raise werkzeug.routing.ValidationError()
    finally:
        for value in app.config.copy().keys():
            if value.startswith("DATABASE"):
                app.config.pop(value)


def update_conf(**kwargs):
    with open(CONF_PATH, "a") as _f:
        for key, value in kwargs.items():
            _f.write("{} = '{}'\n".format(key, value))

    app.config.from_pyfile(CONF_PATH)


@app.route("/install", methods=['GET', 'POST'])
def install():
    form = views.forms.install.InstallationForm()

    if form.validate_on_submit():
        try:
            validate_conf(form)
        except werkzeug.routing.ValidationError:
            return render_template("install.html", form=form)

        update_conf(
            DATABASE_USER=form.username.data,
            DATABASE_PASSWORD=form.password.data,
            DATABASE_HOST=form.host.data,
            DATABASE_NAME=form.database.data,
            DATABASE_PORT=form.port.data
        )
        app.update_db.set()
        return redirect(url_for("index"))

    return render_template('install.html', form=form)


@app.route("/update", methods=['GET', 'POST'])
def update():
    app.update_db.set()
    return redirect(url_for("index"))

