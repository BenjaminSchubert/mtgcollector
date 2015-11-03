# -*- coding: utf-8 -*-
import os

import mtgcollector
from flask import redirect, url_for


@mtgcollector.app.route("/api/images/<card_id>")
def get_image(card_id):
    filename = mtgcollector.lib.db.get_image_path(mtgcollector.app, card_id)
    if not os.path.exists(os.path.join(mtgcollector.app.static_folder, filename)):
        mtgcollector.app.download.put(card_id)
        return redirect(mtgcollector.lib.db.get_image_url(card_id))

    return redirect(url_for("static", filename=filename))
