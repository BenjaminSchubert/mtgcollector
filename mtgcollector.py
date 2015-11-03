# -*- coding: utf-8 -*-
import contextlib
import os

from flask import Flask

import lib.db
import lib.tasks

app = Flask(__name__)

CONF_PATH = os.path.join(app.root_path, "config.cfg")
with contextlib.suppress(FileNotFoundError):
    app.config.from_pyfile(CONF_PATH)

lib.tasks.Downloader(app).start()
lib.tasks.DBUpdater(app).start()

# noinspection PyPep8
from views import *

if __name__ == '__main__':
    app.run(debug=os.environ.get("DEBUG", False))
