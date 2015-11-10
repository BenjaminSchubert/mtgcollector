#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MTGCollector : an application to easily handle your Magic The Gathering collection !
"""

import random
import hashlib
from flask import Flask

import lib.db
import lib.tasks
import flask_wtf.csrf
import flask_login


def setup_app(_app):
    app.config["CONFIG_PATH"] = os.environ.get("MTG_COLLECTOR_CONFIG", os.path.join(_app.root_path, "config.cfg"))

    try:
        _app.config.from_pyfile(_app.config["CONFIG_PATH"])
    except FileNotFoundError:
        _app.secret_key = hashlib.sha512(str(random.randint(0, 2**64)).encode()).hexdigest()

        with open(_app.config["CONFIG_PATH"], "w") as _file:
            _file.write("SECRET_KEY = '{}'".format(_app.secret_key))

    flask_wtf.csrf.CsrfProtect(_app)
    lib.tasks.Downloader(_app).start()
    lib.tasks.DBUpdater(_app).start()


app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

from views import *

if __name__ == '__main__':
    setup_app(app)
    app.run(debug=os.environ.get("MTG_COLLECTOR_DEBUG", False))
