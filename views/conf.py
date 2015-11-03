# -*- coding: utf-8 -*-

from flask import request, redirect, url_for, render_template
from mtgcollector import app, CONF_PATH


def update_conf(**kwargs):
    with open(CONF_PATH, "a") as _f:
        for key, value in kwargs.items():
            _f.write("{} = '{}'\n".format(key, value))

    app.config.from_pyfile(CONF_PATH)


@app.route("/install", methods=['GET', 'POST'])
def install():
    if request.method == "POST":
        update_conf(
            DATABASE_USER=request.form["database_user"],
            DATABASE_PASSWORD=request.form["database_password"],
            DATABASE_HOST=request.form["database_host"],
            DATABASE_NAME=request.form["database_name"]
        )
        app.update_db.set()
        return redirect(url_for("index"))

    return render_template('install.html')


@app.route("/update", methods=['GET', 'POST'])
def update():
    app.update_db.set()
    return redirect(url_for("index"))

