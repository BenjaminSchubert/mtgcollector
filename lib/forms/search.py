#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Search form to easily find cards
"""

from flask_wtf import Form
from wtforms import StringField, TextAreaField, FormField, BooleanField


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


class MCQForm(SubForm):
    in_collection = BooleanField('Only cards in collection')

    def clean_authenticated_fields(self):
        del self.in_collection


class SearchForm(Form):
    """
    This is a form to search through the card collection
    """
    text_inputs = FormField(SearchInputForm)
    mcq_inputs = FormField(MCQForm)

    def setup_authenticated(self, user_authenticated: bool):
        if not user_authenticated:
            self.mcq_inputs.clean_authenticated_fields()
