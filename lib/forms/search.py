#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Search form to easily find cards
"""
from flask_wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField

import lib.models
from lib.forms.fields import SliderField, MultiCheckboxField, StartSeparatorField, StopSeparatorField


class SearchForm(Form):
    """
    This is a form to search through the card collection
    """
    separator1 = StartSeparatorField()

    name = StringField("Name")
    types = StringField("Types")
    text = TextAreaField("Card text")
    context = TextAreaField("Context")
    number = StringField("Card number")
    artist = StringField("Artist")

    separator2 = StopSeparatorField()
    separator3 = StartSeparatorField()

    power = SliderField("Power", min_value=-1, max_value=10)
    toughness = SliderField("Toughness", min_value=-1, max_value=10)
    cmc = SliderField("Mana Cost", min_value=0, max_value=10)
    colors = MultiCheckboxField("Colors", choices=[
            ("Red", "{R}"), ("Green", "{G}"), ("White", "{W}"), ("Blue", "{U}"), ("Black", "{B}"), ("Colorless", "{C}")
        ])
    only_selected_colors = BooleanField("Only selected")
    all_selected_colors = BooleanField("All Selected")

    separator4 = StopSeparatorField()
    separator5 = StartSeparatorField()

    in_collection = BooleanField('Only cards in collection')
    edition = SelectField("Edition", choices=[("", "")], default="")
    block = SelectField("Bloc", choices=[("", "")], default="")
    format = SelectField("Format", choices=[("", "")], default="")
    rarity = MultiCheckboxField("Rarity")

    separator6 = StopSeparatorField()

    def __init__(self, user_authenticated, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power.set_max_value(lib.models.Metacard.maximum("power"))
        self.toughness.set_max_value(lib.models.Metacard.maximum("toughness"))
        self.cmc.set_max_value(lib.models.Metacard.maximum("cmc"))
        self.edition.choices.extend([(edition["code"], edition["name"]) for edition in lib.models.Edition.list()])
        self.block.choices.extend([(block["block"], block["block"]) for block in lib.models.Edition.blocks()])
        self.format.choices.extend([(form["name"], form["name"]) for form in lib.models.Format.list()])
        self.rarity.choices = [(rarity, rarity) for rarity in lib.models.Card.rarities()]

        if not user_authenticated:
            del self.in_collection
