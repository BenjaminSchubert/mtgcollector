# -*- coding: utf-8 -*-
import typing

import lib.db.sql
import lib.models
import lib.db.sql.mysql


def add_editions(connection, editions: typing.Iterable) -> None:
    lib.models.Edition.bulk_insert(editions, connection)


def add_tournaments(connection, tournaments: typing.Set[str]) -> None:
    cursor = connection.cursor()
    cursor.executemany(lib.db.sql.add_tournament, [dict(name=tournament) for tournament in tournaments])
    connection.commit()


def add_metacards(connection, metacards: typing.Dict) -> None:
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
