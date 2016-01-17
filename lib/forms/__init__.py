#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Forms used across the application
"""

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, IntegerField, PasswordField, TextAreaField, BooleanField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, NumberRange, InputRequired

from lib.forms.fields import StartSeparatorField, StopSeparatorField, SliderField, MultiCheckboxField
from lib.forms.validators import validate_port, validate_host
from lib.models import Metacard, Edition, Format, Card, User

__author__ = "Benjamin Schubert, <ben.c.schubert@gmail.com>"


class InstallationForm(Form):
    """
    Installation Form, used to setup the database
    """
    host = StringField("Host", [DataRequired(), validate_host])
    port = IntegerField("Port", [validate_port], default=3306)
    database = StringField("Name", [DataRequired()])
    username = StringField("Username", [DataRequired()])
    password = PasswordField("Password")


class RegisterForm(Form):
    """
    Form to allow a new user to register
    """
    username = StringField("Username", [DataRequired()])
    email = EmailField("Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])


class LoginForm(Form):
    """
    Form for user login
    """
    username = StringField("Username or Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])

    def __init__(self):
        super().__init__()
        self.user = None

    def validate(self, **extras) -> bool:
        """
        Validates that the user authenticated correctly

        :param extras: additional arguments
        :return: whether the login succeeded or not
        """
        if not super().validate():
            return False

        user = User.get_user_by_name_or_mail(self.username.data)

        if user is None:
            self.username.errors.append("Unknown username")
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append("Invalid Password")
            return False

        self.user = user
        return True


class SearchForm(Form):
    """
    This is a form to search through the card collection
    """
    separator1 = StartSeparatorField()

    name = StringField("Name")
    subtypes = StringField("Subtypes")
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
            ("Red", "{R}", 4), ("Green", "{G}", 4), ("White", "{W}", 4), ("Blue", "{U}", 4), ("Black", "{B}", 4),
            ("Colorless", "{C}", 4), ("all_selected", "All", 4), ("only_selected", "Only selected", 8)
        ])
    rarity = MultiCheckboxField("Rarity")

    separator4 = StopSeparatorField()
    separator5 = StartSeparatorField()

    edition = SelectField("Edition", choices=[("", "")], default="")
    block = SelectField("Bloc", choices=[("", "")], default="")
    format = SelectField("Format", choices=[("", "")], default="")
    supertypes = SelectField(
            "Supertypes", default="",
            choices=[(choice, choice) for choice in ["", "Legendary", "Snow", "World", "Basic", "Ongoing"]]
    )
    types = SelectField(
        "Types", default="",
        choices=[
            (choice, choice) for choice in
            ["", "Land", "Creature", "Sorcery", "Instant", "Artifact", "Planeswalker", "Enchantment", "Tribal", "Scheme",
             "Enchant", "Vanguard", "Plane", "Conspiracy", "Phenomenon", "Token"]
        ]
    )
    in_collection = BooleanField('Only cards in collection')

    separator6 = StopSeparatorField()

    def __init__(self, user_authenticated, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power.set_max_value(Metacard.maximum("power"))
        self.toughness.set_max_value(Metacard.maximum("toughness"))
        self.cmc.set_max_value(Metacard.maximum("cmc"))
        self.edition.choices.extend([(edition["code"], edition["name"]) for edition in Edition.list()])
        self.block.choices.extend([(block["block"], block["block"]) for block in Edition.blocks()])
        self.format.choices.extend([(form["name"], form["name"]) for form in Format.list()])
        self.rarity.choices = [(rarity, rarity, 6) for rarity in Card.rarities()]

        if not user_authenticated:
            del self.in_collection


class AddToCollectionForm(Form):
    """
    Form to add a card to the collection
    """
    n_normal = IntegerField(validators=[InputRequired(), NumberRange(min=0)])
    n_foil = IntegerField(validators=[InputRequired(), NumberRange(min=0)])


class RenameDeck(Form):
    """
    Form to rename a deck
    """
    name = StringField(validators=[DataRequired()])


class ChangeDeckIndex(Form):
    """
    Form to change a deck index
    """
    index = IntegerField(validators=[InputRequired(), NumberRange(min=0)])


class AddToDeckForm(Form):
    """
    Form to add a card to a deck
    """
    n_cards = IntegerField(validators=[InputRequired(), NumberRange(min=0)], default=False)
    side = BooleanField()


class ImportDeckForm(Form):
    """
    Form to import a deck to the application
    """
    deck_data = FileField(validators=[FileRequired(), FileAllowed(["json", "Json Format only !"])])

    def __init__(self, label=None):
        super().__init__()
        self.deck_data.label = label
