# -*- coding: utf-8 -*-
import typing

import lib.db.sql
import lib.models
import lib.db.sql.mysql


def setup_tables(connection) -> bool:
    cursor = connection.cursor()

    cursor.execute("SHOW TABLES LIKE 'edition'")
    if cursor.fetchone():
        return False

    # Editions
    cursor.execute(lib.db.sql.create_table_edition)

    # cards
    cursor.execute(lib.db.sql.create_table_metacard)
    cursor.execute(lib.db.sql.create_table_cards)

    # tournaments
    cursor.execute(lib.db.sql.create_table_tournament)
    cursor.execute(lib.db.sql.create_table_card_legal_in_tournament)

    # users
    cursor.execute(lib.db.sql.mysql.MySQL.create_table_user)

    # collections
    cursor.execute(lib.db.sql.create_table_card_in_collection)
    cursor.execute(lib.db.sql.create_table_deck)
    cursor.execute(lib.db.sql.create_table_card_in_deck)

    # constraints
    for constraint in lib.db.sql.metacard_constraints:
        cursor.execute(constraint)

    connection.commit()

    return True


def add_editions(connection, editions: typing.Iterable[lib.models.Edition]) -> None:
    cursor = connection.cursor()
    # noinspection PyArgumentList
    cursor.executemany(lib.db.sql.add_edition, [edition.info() for edition in editions])
    connection.commit()


def add_tournaments(connection, tournaments: typing.Set[str]) -> None:
    cursor = connection.cursor()
    cursor.executemany(lib.db.sql.add_tournament, [dict(name=tournament) for tournament in tournaments])
    connection.commit()


def add_metacards(connection, metacards: typing.Dict[str, lib.models.Metacard]) -> None:
    cursor = connection.cursor()
    # noinspection PyArgumentList
    cursor.executemany(
        lib.db.sql.add_metacard,
        [card.info(ignored=["instances", "special_instances", "legalities"]) for card in metacards.values()]
    )

    cursor.executemany(
        lib.db.sql.add_card,
        [card.info(name=metacard.name) for metacard in metacards.values() for card in metacard.instances]
    )

    cursor.executemany(
        lib.db.sql.allow_card_in_tournament,
        [
            dict(card_name=metacard.name, tournament_name=tournament["format"], type=tournament["legality"])
            for metacard in metacards.values() for tournament in metacard.legalities
            if tournament["legality"] != "Banned"
            ]
    )

    connection.commit()
