#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Views for user authentication, registration and login
"""

import flask
from flask_login import login_user, login_required, logout_user, current_user

from lib.forms.auth import LoginForm, RegisterForm
from mtgcollector import app, lib


@app.route('/login', methods=["GET", "POST"])
def login():
    """ login for the user """
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        login_user(form.user)

        return flask.redirect(flask.request.values.get("next") or flask.request.referrer or "index")

    return flask.render_template(
        'login.html', form=form, id_="login-form", title="Login", active_page="login",
        action_url=flask.url_for("login", next=flask.request.referrer)
    )


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """ logout for the user """
    logout_user()
    return flask.redirect(flask.request.referrer or "index")


@app.route("/register", methods=["GET", "POST"])
def register():
    """ user registration """
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("index"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = lib.models.User(username=form.username.data, email=form.email.data, password=form.password.data).create()
        login_user(user)
        return flask.redirect(flask.request.referrer or "index")

    return flask.render_template('form.html', form=form, id_="form-registration", title="Registration")
