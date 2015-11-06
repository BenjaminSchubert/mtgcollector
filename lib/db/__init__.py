# -*- coding: utf-8 -*-
import os

import flask
import mysql.connector
import mysql.connector.conversion
import mysql.connector.errors
import mysql.connector.errorcode

import lib.db.populate
from lib.models import User

mysql.connector.conversion.MySQLConverter._list_to_mysql = lambda self, value: ",".join(value).encode()


def __insert(command, connection=None, **kwargs):
    if connection is None:
        connection = getattr(flask.g, "db")
    cursor = connection.cursor(dictionary=True)
    cursor.execute(command, kwargs)
    connection.commit()
    return cursor.lastrowid


def __fetch(command, connection=None, **kwargs):
    if connection is None:
        connection = getattr(flask.g, "db")
    cursor = connection.cursor(dictionary=True)
    cursor.execute(command, kwargs)
    return cursor.fetchall()


def get_connection(app):
    return mysql.connector.connect(
        user=app.config["DATABASE_USER"], password=app.config["DATABASE_PASSWORD"],
        host=app.config["DATABASE_HOST"], database=app.config["DATABASE_NAME"], port=app.config["DATABASE_PORT"],
        raise_on_warnings=True
    )


def get_image_url(card_id, **kwargs):
    multiverseid = get_multiverseid(card_id, **kwargs)
    if multiverseid is not None:
        return "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={}&type=card".format(multiverseid)
    else:
        # TODO : handle this case
        print("WE GOT A PROBLEM")


def get_image_path(app, card_id: int):
    data_folder_path = [str(card_id)[n] if len(str(card_id)) > n else "0" for n in range(4)]
    data_folder_path.append(str(card_id) + ".jpg")
    return os.path.join(app.static_folder, "images", *data_folder_path)


def get_multiverseid(card_id, **kwargs):
    cards = __fetch(
        """
        SELECT multiverseid FROM card WHERE
        card_id=%(card_id)s
        """,
        card_id=card_id, **kwargs
    )

    if len(cards):
        return cards[0]["multiverseid"]
    else:
        return None


def get_user(username):
    data = __fetch(
        """
        SELECT * FROM user WHERE username = %(username)s or email = %(username)s
        """,
        username=username
    )
    return User(**data[0])


def get_user_by_id(user_id):
    data = __fetch(
        """
        SELECT * FROM user WHERE user_id = %(user_id)s
        """,
        user_id=user_id
    )
    return User(**data[0])

def get_users(limit=None):
    return __fetch(
        """
        SELECT username, email FROM user LIMIT %(limit)s
        """,
        limit=limit
    )


def create_user(username, email, password):
    return __insert(
        """
        INSERT INTO user (username, email, password) VALUES (%(username)s, %(email)s, %(password)s)
        """,
        username=username, email=email, password=password
    )


def set_admin(user_id):
    return __insert(
        """
        UPDATE user
        SET is_admin = TRUE
        WHERE user_id = %(user_id)s
        """,
        user_id=user_id
    )
