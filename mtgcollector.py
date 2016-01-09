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


def setup_app(_app):
    app.config["CONFIG_PATH"] = os.environ.get("MTG_COLLECTOR_CONFIG", os.path.join(_app.root_path, "config.cfg"))

    try:
        _app.config.from_pyfile(_app.config["CONFIG_PATH"])
    except FileNotFoundError:
        _app.secret_key = hashlib.sha512(str(random.randint(0, 2**64)).encode()).hexdigest()

        with open(_app.config["CONFIG_PATH"], "w") as _file:
            _file.write("SECRET_KEY = '{}'".format(_app.secret_key))

    csrf.init_app(_app)
    login_manager.init_app(_app)
    lib.tasks.Downloader(_app).start()
    lib.tasks.DBUpdater(_app).start()

    _app.json_encoder = CustomJSONEncoder
    _app.notifier = lib.threading.Event()


app = Flask(__name__)

login_manager = flask_login.LoginManager()
csrf = flask_wtf.CsrfProtect()


@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)


from views import *

if __name__ == '__main__':
    setup_app(app)
    app.run(threaded=True, debug=os.environ.get("MTG_COLLECTOR_DEBUG", False))
