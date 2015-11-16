# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

import lib.db
import lib.models
from mtgcollector import app, login_manager


class RegisterForm(Form):
    username = StringField("Username", [DataRequired()])
    email = EmailField("Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])


class LoginForm(Form):
    username = StringField("Username or Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])

    def __init__(self):
        super().__init__()
        self.user = None

    def validate(self, **extras):
        if not super().validate():
            return False

        user = lib.models.User.get_user_by_name_or_mail(self.username.data)

        if user is None:
            self.username.errors.append("Unkown username")
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append("Invalid Password")
            return False

        self.user = user
        return True


@login_manager.user_loader
def load_user(user_id):
    try:
        return lib.models.User.get_user_by_id(user_id)
    except AttributeError:
        return None
