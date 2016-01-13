#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Search form to easily find cards
"""
from flask_wtf import Form
from wtforms import StringField, TextAreaField, FormField, BooleanField

import lib.models
from lib.forms.fields import SliderField, MultiCheckboxField


class SubForm(Form):
    # TODO : check that this is not a big security risk (should be handled by the form calling anyway
    def validate_csrf_token(self, field):
        return True


class SearchInputForm(SubForm):
    card_name = StringField("Name")
    card_type = StringField("Type")
    card_text = TextAreaField("Card text")
    card_context = TextAreaField("Context")
    card_number = StringField("Card number")
    artist = StringField("Artist")


class ValuesForm(SubForm):
    power = SliderField("Power", min_value=-1, max_value=10)
    toughness = SliderField("Toughness", min_value=-1, max_value=10)
    cmc = SliderField("Mana Cost", min_value=0, max_value=10)
    colors = MultiCheckboxField("Colors", choices=[
            ("Red", "{R}"), ("Green", "{G}"), ("White", "{W}"), ("Blue", "{B}"), ("Black", "{B}"), ("Colorless", "{C}")
        ])
    only_selected_colors = BooleanField("Only selected")
    all_selected_colors = BooleanField("All Selected")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power.set_max_value(lib.models.Metacard.maximum("power"))
        self.toughness.set_max_value(lib.models.Metacard.maximum("toughness"))
        self.cmc.set_max_value(lib.models.Metacard.maximum("cmc"))


class MCQForm(SubForm):
    in_collection = BooleanField('Only cards in collection')

    def clean_authenticated_fields(self):
        del self.in_collection


class SearchForm(Form):
    """
    This is a form to search through the card collection
    """
    text_inputs = FormField(SearchInputForm)
    values_inputs = FormField(ValuesForm)
    mcq_inputs = FormField(MCQForm)

    def setup_authenticated(self, user_authenticated: bool):
        if not user_authenticated:
            self.mcq_inputs.clean_authenticated_fields()
