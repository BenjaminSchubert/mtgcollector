# -*- coding: utf-8 -*-
import os
import requests

import mtgcollector
from flask import redirect, send_from_directory

default_card_url = "http://gatherer.wizards.com/Handlers/Image.ashx?size=small&type=card&name=The%20Ultimate%20Nightmare%20of%20Wizards%20of%20the%20Coast%20Customer%20Service&options="


@mtgcollector.app.route("/api/images/<card_id>")
def get_image(card_id):
    filename = mtgcollector.lib.db.get_image_path(mtgcollector.app, card_id)
    if not os.path.exists(os.path.join(mtgcollector.app.static_folder, filename)):
        mtgcollector.app.download.put(card_id)
        return redirect(mtgcollector.lib.db.get_image_url(card_id))

    return send_from_directory(
        os.path.join(mtgcollector.app.static_folder, os.path.dirname(filename)),
        os.path.split(filename)[1])


@mtgcollector.app.route("/api/images/default.png")
def get_default_image():
    # TODO : factorize this
    filename = os.path.join("images", "default.png")
    if not os.path.exists(os.path.join(mtgcollector.app.static_folder, filename)):
        request = requests.get(default_card_url, stream=True)

        if request.status_code != requests.codes.ok:
            raise request.raise_for_status()

        os.makedirs(os.path.dirname(os.path.join(mtgcollector.app.static_folder, filename)), exist_ok=True)
        with open(os.path.join(mtgcollector.app.static_folder, filename), "wb") as _file_:
            for chunk in request.iter_content(chunk_size=1024):
                if chunk:  # this is to filter out keepalive chunks
                    _file_.write(chunk)

    return send_from_directory(os.path.join(mtgcollector.app.static_folder, "images"), "default.png")
