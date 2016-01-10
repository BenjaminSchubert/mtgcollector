#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MySQL implementation of the commands needed to run MTGCollector application
"""


import mysql.connector
import mysql.connector.conversion


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


# We need to match mysql converter to be able to accept list and sets
mysql.connector.conversion.MySQLConverter._list_to_mysql = lambda self, value: ",".join(value).encode()
mysql.connector.conversion.MySQLConverter._set_to_mysql = lambda self, value: ",".join(value).encode()


def get_connection(app):
    return mysql.connector.connect(
        user=app.config["DATABASE_USER"], password=app.config["DATABASE_PASSWORD"],
        host=app.config["DATABASE_HOST"], database=app.config["DATABASE_NAME"], port=app.config["DATABASE_PORT"],
        raise_on_warnings=True
    )


class User:
    """
    MySQL commands related to the User model
    """
    @classmethod
    def create_table(cls):
        """ command to create the user table"""
        return """
            CREATE TABLE user (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN NOT NULL DEFAULT FALSE
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert a user in the table"""
        return """ INSERT INTO user (username, email, password) VALUES (%(username)s, %(email)s, %(password)s) """

    @classmethod
    def set_admin(cls):
        """ command to set a user administrator """
        return """ UPDATE user SET is_admin = %(admin)s WHERE user_id = %(user_id)s"""

    @classmethod
    def get(cls):
        """ command to get all users without limit """
        return """ SELECT * FROM user ORDER BY username """

    @classmethod
    def get_with_limit(cls):
        """ command to get %(limit)s users, at %(offset)s offset """
        return """ SELECT * FROM user ORDER BY username LIMIT %(limit)s OFFSET %(offset)s"""

    @classmethod
    def get_by_id(cls):
        """ get user by id"""
        return """ SELECT * FROM user WHERE user_id = %(user_id)s """

    @classmethod
    def get_by_mail_or_username(cls):
        """ get user by email or username """
        return """ SELECT * FROM user WHERE username = %(identifier)s OR email = %(identifier)s """


class Metacard:
    """
    MySQL commands related to the Metacard model
    """
    @classmethod
    def create_table(cls):
        """ table creation command to the Metacard model """
        return """
            CREATE TABLE metacard (
                name VARCHAR(150) PRIMARY KEY,
                types SET (
                    'Land', 'Creature', 'Sorcery', 'Instant', 'Artifact', 'Planeswalker', 'Enchantment', 'Tribal',
                    'Scheme', 'Eaturecray', 'Enchant', 'Vanguard', 'Plane', 'Scariest', 'You\\'ll', 'Ever', 'See',
                    'Conspiracy', 'Phenomenon', 'Player', 'Token'
                ) NOT NULL,
                subtypes VARCHAR(80),
                supertypes SET('Legendary', 'Snow', 'World', 'Basic', 'Ongoing'),
                manaCost VARCHAR(50),
                power VARCHAR(4),
                toughness VARCHAR(4),
                colors SET('Red', 'Green', 'White', 'Blue', 'Black'),
                cmc FLOAT NOT NULL,
                orig_text TEXT
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert a metacard """
        return """
            INSERT INTO metacard (name, types, subtypes, supertypes, manaCost, power, toughness, colors, cmc, orig_text)
            VALUES (
                %(name)s, %(types)s, %(subtypes)s, %(supertypes)s, %(manaCost)s, %(power)s, %(toughness)s, %(colors)s,
                 %(cmc)s, %(text)s
            )
            ON DUPLICATE KEY UPDATE
                name=VALUES(name), types=VALUES(types), subtypes=VALUES(subtypes), supertypes=VALUES(supertypes),
                manaCost=VALUES(manaCost), power=VALUES(power), toughness=VALUES(toughness), colors=VALUES(colors),
                cmc=VALUES(cmc), orig_text=VALUES(orig_text)
        """

    @classmethod
    def get_ids(cls):
        """ command to get a card id for a metacard"""
        return """
            SELECT card.card_id
            FROM metacard
            INNER JOIN card ON card.name = metacard.name
            WHERE {selection}
            GROUP BY metacard.name
            ORDER BY {order}
        """


class Card:
    """
    MySQL commands related to the Card model
    """
    @classmethod
    def create_table(cls):
        """ command to create the Card table """
        return """
            CREATE TABLE card (
                card_id INT PRIMARY KEY AUTO_INCREMENT,
                multiverseid INT,
                name VARCHAR(150) NOT NULL,
                edition VARCHAR(8) NOT NULL,
                rarity SET ('Basic Land', 'Common', 'Uncommon', 'Rare', 'Mythic Rare', 'Special') NOT NULL,
                number VARCHAR(4) NOT NULL,
                version TINYINT NOT NULL,
                artist VARCHAR(150) NOT NULL,
                flavor TEXT,
                price DECIMAL(7,2),

                FOREIGN KEY (name) REFERENCES metacard(name) ON DELETE RESTRICT ON UPDATE RESTRICT,
                FOREIGN KEY (edition) REFERENCES edition(code) ON DELETE RESTRICT ON UPDATE RESTRICT,
                UNIQUE (multiverseid, edition, number, version)
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert a card """
        return """
            INSERT INTO card (multiverseid, name, number, version, rarity, edition, artist, flavor)
            VALUES (%(multiverseid)s, %(name)s, %(number)s, %(version)s, %(rarity)s, %(edition)s, %(artist)s, %(flavor)s)
            ON DUPLICATE KEY UPDATE
                name=VALUES(name), number=VALUES(number), version=VALUES(version), rarity=VALUES(version),
                edition=VALUES(edition), artist=VALUES(artist), flavor=VALUES(flavor)
        """

    @classmethod
    def get(cls):
        """ command to get a card """
        return """
            SELECT
                multiverseid,
                metacard.name as name,
                edition.name as edition,
                rarity,
                number,
                supertypes,
                types,
                subtypes,
                manaCost,
                power,
                toughness,
                colors,
                cmc,
                orig_text,
                artist,
                flavor,
                price,
                (
                    SELECT COUNT(*)
                        FROM card
                        WHERE card.name = metacard.name
                ) AS versions
            FROM metacard
                INNER JOIN card
                    ON metacard.name = card.name
                INNER JOIN edition
                    ON card.edition = edition.code
            WHERE card_id = %(card_id)s;
        """

    @classmethod
    def get_multiverseid(cls):
        """ get the multiverseid for the given card id """
        return """
            SELECT multiverseid FROM card WHERE
            card_id=%(card_id)s
        """


class Edition:
    """
    MySQL commands related to the Edition model
    """
    @classmethod
    def create_table(cls):
        """ command to create the table for Edition """
        return """
            CREATE TABLE edition (
                code VARCHAR(8) PRIMARY KEY NOT NULL,
                releaseDate DATE NOT NULL,
                name VARCHAR(255) UNIQUE NOT NULL,
                type ENUM (
                    'core', 'expansion', 'duel deck', 'commander', 'promo', 'box', 'un', 'reprint', 'from the vault',
                    'planechase', 'masters', 'starter', 'premium deck', 'conspiracy', 'vanguard', 'archenemy'
                ) NOT NULL,
                block VARCHAR(50)
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert an edition """
        return """
            INSERT INTO edition (code, releaseDate, name, type, block)
            VALUES (%(code)s, %(releaseDate)s, %(name)s, %(type)s, %(block)s)
            ON DUPLICATE KEY UPDATE
                releaseDate=VALUES(releaseDate), name=VALUES(name), type=VALUES(type), block=VALUES(block)
        """

    @classmethod
    def get_name_id(cls):
        """ command to get all editions names and ids """
        return """ SELECT code, name FROM edition ORDER BY name """


class Tournament:
    """
    MySQL commands related to the Tournament model
    """
    @classmethod
    def create_table(cls):
        """ command to create the Tournament table """
        return """
            CREATE TABLE tournament (
                name VARCHAR(150) PRIMARY KEY
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert a tournament """
        return """
            INSERT INTO tournament (name)
            VALUES (%(name)s)
            ON DUPLICATE KEY UPDATE name=VALUES(name)
        """
