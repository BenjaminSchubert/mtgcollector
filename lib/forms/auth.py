#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
These forms handle the authentication of users
"""

from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

import lib.db
import lib.models

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


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

        user = lib.models.User.get_user_by_name_or_mail(self.username.data)

        if user is None:
            self.username.errors.append("Unknown username")
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append("Invalid Password")
            return False

        self.user = user
        return True
