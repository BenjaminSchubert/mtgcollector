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


def _validate_port(form, field):
    if field.data is not None and not 0 < field.data < 65535:
        raise ValidationError("The port value should be between 0 and 65535")


class InstallationForm(Form):
    host = StringField("Host", [DataRequired(), _validate_host])
    port = IntegerField("Port", [_validate_port], default=3306)
    database = StringField("Name", [DataRequired()])
    username = StringField("Username", [DataRequired()])
    password = PasswordField("Password")
