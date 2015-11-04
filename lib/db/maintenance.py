# -*- coding: utf-8 -*-
import flask
import mysql.connector
import mysql.connector.errors
import mysql.connector.errorcode

import lib
import lib.db
import lib.update.parser


class MaintenanceDB:
    class DBManager:
        def __init__(self, app):
            self.app = app
            self.conn = None

        def __enter__(self):
            self.conn = lib.db.get_connection(self.app)
            return self.conn

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.conn.close()

    def __init__(self, app: flask.Flask):
        self.app = app

    def db_manager(self, app):
        return self.DBManager(app)

    def __update(self, card_updater):
        cards = lib.update.parser.load_file(card_updater.latest_version())
        with self.DBManager(self.app) as connection:
            lib.db.populate.add_editions(connection, lib.update.parser.get_editions(cards))
            lib.db.populate.add_tournaments(connection, lib.update.parser.get_tournaments(cards))
            lib.db.populate.add_metacards(connection, lib.update.parser.get_metacards(cards))

    def setup_db(self):
        conn = mysql.connector.connect(
            user=self.app.config["DATABASE_USER"], password=self.app.config["DATABASE_PASSWORD"],
            host=self.app.config["DATABASE_HOST"], port=self.app.config["DATABASE_PORT"], raise_on_warnings=True
        )
        try:
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE %(database_name)s CHARACTER SET utf8", self.app.config["DATABASE_NAME"])
            conn.commit()
        except:
            raise
        else:
            with self.DBManager(self.app) as connection:
                lib.db.populate.setup_tables(connection)
            card_updater = lib.update.CardUpdater(self.app)
            card_updater.check_update()
            self.__update(card_updater)
        finally:
            conn.close()

    def update(self, ) -> None:
        card_updater = lib.update.CardUpdater(self.app)
        card_updater.check_update()
        try:
            self.__update(card_updater)
        except mysql.connector.errors.ProgrammingError as exc:
            if exc.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.setup_db()
            else:
                raise
