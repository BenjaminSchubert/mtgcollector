#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MySQL implementation of the commands needed to run MTGCollector application
"""

import abc

import mysql.connector
import mysql.connector.conversion

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


# Patches to make MySQL behave correctly
mysql.connector.conversion.MySQLConverter._list_to_mysql = lambda self, value: ",".join(value).encode()
mysql.connector.conversion.MySQLConverter._set_to_mysql = lambda self, value: ",".join(value).encode()
mysql.connector.conversion.MySQLConverter._bytearray_to_mysql = lambda self, value: bytes(value)


def get_connection(app):
    """
    returns a connection to the database

    :param app: Flask app containing the configuration
    :return: MySQL connection to the database
    """
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
                password BINARY(64) NOT NULL,
                salt BINARY(255) NOT NULL,
                is_admin BOOLEAN NOT NULL DEFAULT FALSE
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert a user in the table"""
        return """
            INSERT INTO user (username, email, password, salt)
            VALUES (%(username)s, %(email)s, %(password)s, %(salt)s)
        """

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

    @classmethod
    def update(cls):
        """ updates the user's information """
        return """
            UPDATE user
            SET username = %(username)s, email = %(email)s, password = %(password)s, salt = %(salt)s
            WHERE user_id = %(user_id)s
        """


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
                power DECIMAL(3,1),
                toughness DECIMAL(3,1),
                colors SET('Red', 'Green', 'White', 'Blue', 'Black'),
                cmc DECIMAL(8,1) NOT NULL,
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
                types=VALUES(types), subtypes=VALUES(subtypes), supertypes=VALUES(supertypes),
                manaCost=VALUES(manaCost), power=VALUES(power), toughness=VALUES(toughness), colors=VALUES(colors),
                cmc=VALUES(cmc), orig_text=VALUES(orig_text)
        """

    @classmethod
    def get_ids(cls):
        """ command to get card ids for metacards """
        return """
            SELECT card.card_id
            FROM metacard
            INNER JOIN card ON card.name = metacard.name
            {selection}
            GROUP BY metacard.name
            ORDER BY {order}
        """

    @classmethod
    def get_ids_with_collection_information(cls):
        """ command to get card ids for metacards with the number owned by the given user """
        return """
            SELECT card.card_id,
                IFNULL(SUM(collection.normal), 0) AS normal,
                IFNULL(SUM(collection.foil), 0) AS foil
            FROM metacard
            INNER JOIN card
                ON card.name = metacard.name
            LEFT OUTER JOIN (SELECT * FROM card_in_collection WHERE user_id = %(user_id)s) AS collection
                ON collection.card_id = card.card_id
            {selection}
            GROUP BY metacard.name
            {having}
            ORDER BY {order}
        """

    @classmethod
    def maximum(cls):
        """ command to get the minimum value for a column """
        return """ SELECT {maximum} AS max FROM metacard ORDER BY {maximum} DESC LIMIT 2"""


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
                artist VARCHAR(150) NOT NULL,
                flavor TEXT,
                price DECIMAL(7,2),

                FOREIGN KEY (name) REFERENCES metacard(name) ON DELETE RESTRICT ON UPDATE RESTRICT,
                FOREIGN KEY (edition) REFERENCES edition(code) ON DELETE RESTRICT ON UPDATE RESTRICT,
                UNIQUE (multiverseid, edition, number)
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert a card """
        return """
            INSERT INTO card (multiverseid, name, number, rarity, edition, artist, flavor)
            VALUES
                (%(multiverseid)s, %(name)s, %(number)s, %(rarity)s, %(edition)s, %(artist)s, %(flavor)s)
            ON DUPLICATE KEY UPDATE
                rarity=VALUES(rarity), edition=VALUES(edition), artist=VALUES(artist),
                flavor=VALUES(flavor)
        """

    @classmethod
    def get(cls):
        """ command to get a card """
        return """
            SELECT multiverseid,
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
    def get_versions(cls):
        """ command to get all versions of the same card """
        return """
            SELECT card_id, edition.releaseDate
            FROM card
            INNER JOIN edition ON card.edition = edition.code
            WHERE card.name = %(name)s
            ORDER BY edition.releaseDate DESC
        """

    @classmethod
    def get_versions_with_collection_information(cls):
        """ get all versions of the same card with the number owned by the given user """
        return """
            SELECT card.card_id,
                IFNULL(collection.normal, 0) AS normal,
                IFNULL(collection.foil, 0) AS foil
            FROM card
            INNER JOIN edition
                ON card.edition = edition.code
            LEFT OUTER JOIN (SELECT * FROM card_in_collection WHERE user_id = %(user_id)s) AS collection
                ON card.card_id = collection.card_id
            WHERE card.name = %(name)s
            ORDER BY edition.releaseDate DESC
        """

    @classmethod
    def get_multiverseid(cls):
        """ get the multiverseid for the given card id """
        return """ SELECT multiverseid FROM card WHERE card_id=%(card_id)s """

    @classmethod
    def rarities(cls):
        """ list all different rarity formats """
        return """ SELECT DISTINCT rarity FROM card """

    @classmethod
    def collection(cls):
        """ list all ids from the collection of the given user """
        return """
            SELECT card.card_id,
                card_in_collection.normal,
                card_in_collection.foil
            FROM card
            INNER JOIN card_in_collection
            ON card.card_id = card_in_collection.card_id
            WHERE user_id = %(user_id)s
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
    def insert(cls) -> str:
        """ command to insert an edition """
        return """
            INSERT INTO edition (code, releaseDate, name, type, block)
            VALUES (%(code)s, %(releaseDate)s, %(name)s, %(type)s, %(block)s)
            ON DUPLICATE KEY UPDATE
                releaseDate=VALUES(releaseDate), type=VALUES(type)
        """

    @classmethod
    def list(cls) -> str:
        """ command to get all editions names and ids """
        return """ SELECT code, name FROM edition ORDER BY name """

    @classmethod
    def blocks(cls) -> str:
        """ command to get all different blocs """
        return """ SELECT DISTINCT block FROM edition ORDER BY name """


class Format:
    """
    MySQL commands related to the Format model
    """
    @classmethod
    def create_table(cls):
        """ command to create the format table """
        return """
            CREATE TABLE format (
                name VARCHAR(150) PRIMARY KEY
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert a format """
        return """
            INSERT INTO format (name)
            VALUES (%(name)s)
            ON DUPLICATE KEY UPDATE name=VALUES(name)
        """

    @classmethod
    def list(cls) -> str:
        """ method to get all format """
        return """ SELECT * FROM format """


class CardInCollection:
    """
    MySQL commands related to the collection table
    """
    @classmethod
    def create_table(cls):
        """ command to create the collection table """
        return """
            CREATE TABLE card_in_collection (
                user_id INT NOT NULL,
                card_id INT NOT NULL,
                normal INT UNSIGNED NOT NULL DEFAULT 0,
                foil INT UNSIGNED NOT NULL DEFAULT 0,

                FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE RESTRICT,
                FOREIGN KEY (card_id) REFERENCES card(card_id) ON DELETE RESTRICT ON UPDATE RESTRICT,

                PRIMARY KEY (user_id, card_id)
            )
        """

    @classmethod
    def insert_by_id(cls):
        """ command to insert a new card in collection """
        return """
            INSERT INTO card_in_collection (user_id, card_id, normal, foil)
            VALUES (%(user_id)s, %(card_id)s, %(normal)s, %(foil)s)
            ON DUPLICATE KEY UPDATE normal=VALUES(normal), foil=VALUES(foil)
        """

    @classmethod
    def delete(cls):
        """ removes completely a card from the collection """
        return """
            DELETE FROM card_in_collection
            WHERE card_id=%(card_id)s AND user_id=%(user_id)s
        """

    @classmethod
    def export(cls):
        """ returns all cards owned by the given user """
        return """
            SELECT name, edition, number, foil, normal
            FROM card
            INNER JOIN card_in_collection
            ON card.card_id = card_in_collection.card_id
            WHERE user_id = %(user_id)s
        """

    @classmethod
    def insert(cls):
        """ insert a card in the collection """
        return """
            INSERT INTO card_in_collection (user_id, card_id, normal, foil)
            SELECT %(user_id)s, card_id, %(normal)s, %(foil)s
            FROM card
            WHERE name = %(name)s AND edition = %(edition)s AND number = %(number)s
        """


class Deck:
    """
    MySQL commands related to the DeckList model
    """
    @classmethod
    def create_table(cls):
        """ command to create the deck """
        return """
            CREATE TABLE deck (
                deck_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                user_index INT DEFAULT 0 NOT NULL,

                FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                UNIQUE(user_id, name)
            )
        """

    @classmethod
    def insert(cls):
        """ command to insert a new deck in the database """
        return """
            INSERT INTO deck (user_id, name)
            VALUES (%(user_id)s, %(name)s)
        """

    @classmethod
    def delete(cls):
        """ command to remove the given deck """
        return """ DELETE FROM deck WHERE name = %(name)s AND user_id = %(user_id)s """

    @classmethod
    def rename(cls) -> str:
        """ command to rename a deck """
        return """
            UPDATE deck
            SET name = %(new_name)s
            WHERE name = %(name)s AND user_id = %(user_id)s
        """

    @classmethod
    def set_index(cls) -> str:
        """ command to change the id of a deck """
        return """
            UPDATE deck
            SET user_index = %(index)s
            WHERE name = %(name)s AND user_id = %(user_id)s
        """

    @classmethod
    def list(cls):
        """ command to get a list of decks for the given user_id """
        return """
            SELECT name,
                user_index,
                IFNULL(deck.card_sum, 0) AS n_deck,
                IFNULL(side.card_sum, 0) AS n_side,
                colors.colors
            FROM deck AS decks
            LEFT JOIN (SELECT deck_id, SUM(number) AS card_sum FROM card_in_deck GROUP BY deck_id) AS deck
                ON deck.deck_id = decks.deck_id
            LEFT JOIN (SELECT deck_id, SUM(number) AS card_sum FROM card_in_side GROUP BY deck_id) AS side
                ON side.deck_id = decks.deck_id
            LEFT JOIN (
                SELECT GROUP_CONCAT(DISTINCT colors) AS colors, deck_id
                FROM metacard
                    INNER JOIN card
                        ON metacard.name = card.name
                    INNER JOIN (
                        SELECT card_id, deck_id
                              FROM card_in_deck
                        UNION SELECT card_id, deck_id
                              FROM card_in_side
                    ) AS cards
                      ON cards.card_id = card.card_id
                  GROUP BY deck_id) AS colors
              ON decks.deck_id = colors.deck_id
            WHERE user_id=%(user_id)s
                GROUP BY decks.deck_id
            ORDER BY user_index ASC
        """

    @classmethod
    def get(cls):
        """ command to get the deck corresponding to the given name and user_id """
        # TODO check if this is useful
        return """
            SELECT user_index, name
            FROM deck
            WHERE user_id = %(user_id)s AND name = %(name)s
        """

    @classmethod
    def get_missing(cls):
        """ get all missing card from given deck """
        return """
            SELECT deck_entity.card_id, SUM(deck_entity.number) - IFNULL(owned.number, 0) AS number
            FROM deck
            INNER JOIN (SELECT * FROM card_in_deck UNION ALL SELECT * FROM card_in_side) AS deck_entity
                ON deck_entity.deck_id = deck.deck_id
            LEFT JOIN (
                SELECT DISTINCT card_id,
                normal + foil AS number
                FROM card_in_collection WHERE user_id = %(user_id)s
            ) AS owned
                ON owned.card_id = deck_entity.card_id
            WHERE name = %(deck_name)s AND user_id = %(user_id)s
            GROUP BY deck_entity.card_id, owned.number
            HAVING owned.number IS NULL OR SUM(deck_entity.number) > owned.number
        """


# noinspection SqlResolve
class CardInDeckEntity(abc.ABCMeta):
    """
    Abstract helper for cardsInDeck and cardsInSide
    """
    @classmethod
    @abc.abstractmethod
    def table_name(mcs) -> str:
        """ the table name """

    @classmethod
    def create_table(mcs) -> str:
        """ command to create the table """
        return """
            CREATE TABLE {table_name} (
                deck_id INT NOT NULL,
                card_id INT NOT NULL,
                number SMALLINT UNSIGNED NOT NULL,

                FOREIGN KEY (deck_id) REFERENCES deck(deck_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (card_id) REFERENCES card(card_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
                UNIQUE(deck_id, card_id)
            )
        """.format(table_name=mcs.table_name())

    # noinspection SqlInsertValues
    @classmethod
    def add(mcs) -> str:
        """ add a card to a deck """
        return """
            INSERT INTO {table_name} (deck_id, card_id, number)
            SELECT deck_id, %(card_id)s, %(number)s
            FROM deck
            WHERE user_id = %(user_id)s AND deck.name = %(deck_name)s
            ON DUPLICATE KEY UPDATE number=VALUES(number)
        """.format(table_name=mcs.table_name())

    @classmethod
    def get_cards(mcs) -> str:
        """ list all cards in the deck"""
        return """
            SELECT number, card_id
            FROM {table_name}
            INNER JOIN deck
            ON {table_name}.deck_id = deck.deck_id
            WHERE user_id = %(user_id)s AND deck.name = %(deck_name)s
        """.format(table_name=mcs.table_name())

    @classmethod
    def delete(mcs):
        """ delete the given entry """
        return """
            DELETE FROM {table_name}
            WHERE deck_id=(
                    SELECT deck_id FROM deck WHERE name = %(name)s AND user_id=%(user_id)s
                )
                AND card_id=%(card_id)s
        """.format(table_name=mcs.table_name())

    @classmethod
    def export(mcs):
        """ data information about the deck """
        return """
            SELECT card.name, edition, card.number AS ed_number, {table_name}.number
            FROM {table_name}
            INNER JOIN deck
                ON deck.deck_id = {table_name}.deck_id
            INNER JOIN card
                ON {table_name}.card_id = card.card_id
            WHERE deck.user_id = %(user_id)s AND deck.name = %(deck_name)s
        """.format(table_name=mcs.table_name())

    # noinspection SqlInsertValues
    @classmethod
    def insert(mcs):
        """ insert a card in the object """
        return """
            INSERT INTO {table_name} (deck_id, card_id, number)
            SELECT deck_id, card_id, %(number)s
            FROM
                (SELECT deck_id FROM deck
                    WHERE user_id = %(user_id)s AND name = %(deck_name)s) AS deck,
                (SELECT card_id FROM card
                    WHERE name = %(name)s AND edition=%(edition)s AND number=%(ed_number)s) AS card
        """.format(table_name=mcs.table_name())


class CardInDeck(CardInDeckEntity):
    """
    MySQL commands to handle adding and removing cards in a deck
    """
    @classmethod
    def table_name(mcs) -> str:
        """ the table name """
        return "card_in_deck"


class CardInSide(CardInDeckEntity):
    """
    MySQL commands to handle adding and removing cards in a side deck
    """
    @classmethod
    def table_name(mcs) -> str:
        """ the table name """
        return "card_in_side"


class LegalInFormat:
    """
    MySQL commands to handle which formats which card is available in
    """
    @classmethod
    def create_table(cls) -> str:
        """ command to create the table """
        return """
            CREATE TABLE card_legal_in_format (
                card_name VARCHAR(150) NOT NULL,
                format VARCHAR(150) NOT NULL,
                type SET('Restricted', 'Legal', 'Banned') NOT NULL,

                FOREIGN KEY (card_name) REFERENCES metacard(name) ON DELETE RESTRICT ON UPDATE RESTRICT,
                FOREIGN KEY (format) REFERENCES format(name) ON DELETE RESTRICT ON UPDATE RESTRICT ,
                UNIQUE (card_name, format)
            )
        """

    @classmethod
    def insert(cls) -> str:
        """ command to make a card valid in a format """
        return """
            INSERT INTO card_legal_in_format (card_name, format, type)
            VALUES (%(card_name)s, %(format)s, %(type)s)
            ON DUPLICATE KEY UPDATE type=VALUES(type)
        """
