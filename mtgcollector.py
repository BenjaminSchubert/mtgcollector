# -*- coding: utf-8 -*-
import contextlib
import os

from flask import Flask

import lib.db
import lib.tasks
import flask_wtf.csrf
import flask_login


app = Flask(__name__)

CONF_PATH = os.path.join(app.root_path, "config.cfg")
with contextlib.suppress(FileNotFoundError):
    app.config.from_pyfile(CONF_PATH)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

flask_wtf.csrf.CsrfProtect(app)
lib.tasks.Downloader(app).start()
lib.tasks.DBUpdater(app).start()
app.secret_key = "NotVeryRandom"


from views import *

if __name__ == '__main__':
    app.run(debug=os.environ.get("DEBUG", False))
