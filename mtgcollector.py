#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MTGCollector : an application to easily handle your Magic The Gathering collection !
"""

import hashlib
import os
import random

import flask_login
import flask_wtf.csrf
from flask import Flask

import lib.db
import lib.tasks
import lib.threading
from lib.json import CustomJSONEncoder
from lib.models import User


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


def setup_app(_app: Flask) -> None:
    """
    setups flask application

    :param _app: application to configure
    """
    _app.config["CONFIG_PATH"] = os.environ.get("MTG_COLLECTOR_CONFIG", os.path.join(_app.root_path, "config.cfg"))

    try:
        _app.config.from_pyfile(_app.config["CONFIG_PATH"])
    except FileNotFoundError:  # this is the first run
        from lib import conf
        conf.update_conf(
            SECRET_KEY=hashlib.sha512(str(random.randint(0, 2**64)).encode()).hexdigest(),
        )

    csrf.init_app(_app)
    login_manager.init_app(_app)
    lib.tasks.ImageHandler(_app)
    lib.tasks.DBUpdater(_app).start()

    _app.json_encoder = CustomJSONEncoder
    _app.notifier = lib.threading.Event()


app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.login_view = 'login'

# noinspection PyUnresolvedReferences
csrf = flask_wtf.CsrfProtect()


@login_manager.user_loader
def load_user(user_id: int) -> User:
    """
    Loads the user from the database

    :param user_id: id of the user to load
    :return: a User instance
    """
    return User.get_user_by_id(user_id)


# noinspection PyPep8
from views import *

if __name__ == '__main__':
    setup_app(app)
    app.run(threaded=True, debug=os.environ.get("MTG_COLLECTOR_DEBUG", False))
