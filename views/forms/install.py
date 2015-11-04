# -*- coding: utf-8 -*-
import ipaddress
import socket

from flask_wtf import Form
from wtforms import PasswordField, StringField, ValidationError, IntegerField
from wtforms.validators import DataRequired


def _validate_host(form, field):
    try:
        ipaddress.ip_address(field.data)
    except:
        try:
            socket.gethostbyname(field.data)
        except:
            raise ValidationError("The ip address is not valid or the hostname cannot be resolved")


class InstallationForm(Form):
    host = StringField("Host", [DataRequired(), _validate_host])
    database = StringField("Name", [DataRequired()])
    username = StringField("Username", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    port = IntegerField("Port", default=3306)
