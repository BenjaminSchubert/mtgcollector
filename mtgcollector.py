# -*- coding: utf-8 -*-
import contextlib
import os

from flask import Flask

import lib.db
import lib.tasks
import flask_wtf.csrf
import flask_login


def setup_app(_app):
    login_manager = flask_login.LoginManager()
    login_manager.init_app(_app)

    flask_wtf.csrf.CsrfProtect(_app)
    lib.tasks.Downloader(_app).start()
    lib.tasks.DBUpdater(_app).start()

app = Flask(__name__)

CONF_PATH = os.path.join(app.root_path, "config.cfg")
with contextlib.suppress(FileNotFoundError):
    app.config.from_pyfile(CONF_PATH)

# TODO fix this generation
app.secret_key = "NotVeryRandom"

setup_app(app)


from views import *

if __name__ == '__main__':
    app.run(debug=os.environ.get("DEBUG", False))
