# -*- coding: utf-8 -*-
from datetime import datetime
import json
import typing

from ..models import Edition, Metacard, Card

CardList = typing.Dict[str, typing.Dict[str, typing.Union[str, typing.List]]]


def load_file(file_path: str) -> CardList:
    with open(file_path, encoding="utf8") as f:
        cards = json.load(f)

    return cards


def get_editions(cards: CardList) -> typing.Set[Edition]:
    editions = set()
    for edition in cards.values():
        editions.add(Edition(
            code=edition.get("code"),
            name=edition.get("name"),
            type=edition.get("type"),
            releaseDate=datetime.strptime(edition.get("releaseDate"), "%Y-%m-%d"),
            block=edition.get("block", None)
        ))

    return editions


def get_metacards(cards: CardList) -> typing.Dict[str, Metacard]:
    metacards = {}
    rulings = []
    rulings_set = set()
    for edition in cards.values():
        for metacard in edition.get("cards"):
            for rule in metacard.get("rulings", []):
                x = (rule["text"], rule["date"])
                rulings.append(rule)
                rulings_set.add(x)
            if metacard.get("types") is None and "token" in metacard.get("name"):
                metacard["types"] = ["token"]

            if not metacards.get(metacard.get("name")):
                metacards[metacard.get("name")] = Metacard(
                    name=metacard.get("name"),
                    types=metacard.get("types"),
                    subtypes=metacard.get("subtypes"),
                    supertypes=metacard.get("supertypes"),
                    manaCost=metacard.get("manaCost"),
                    power=metacard.get("power"),
                    toughness=metacard.get("toughness"),
                    colors=metacard.get("colors"),
                    cmc=metacard.get("cmc", 0),
                    text=metacard.get("originalText"),
                    instances=[],
                    legalities=metacard.get("legalities", []),
                )

            version = ""
            counter = -1
            while metacard.get("imageName")[counter].isdigit():
                version = metacard.get("imageName")[counter] + version
                counter -= 1

            if counter == -1:
                version = 0

            metacards[metacard.get("name")].instances.append(Card(
                multiverseid=metacard.get("multiverseid"),
                rarity=metacard.get("rarity"),
                number=metacard.get("number", 0),
                version=version,
                edition=edition.get("code"),
                artist=metacard.get("artist"),
                flavor=metacard.get("flavor")
            ))

    return metacards


def get_tournaments(cards: CardList) -> typing.Set[str]:
    tournaments = set()

    for edition in cards.values():
        for metacard in edition.get("cards"):
            for legality in metacard.get("legalities", []):
                tournaments.add(legality["format"])

    return tournaments
