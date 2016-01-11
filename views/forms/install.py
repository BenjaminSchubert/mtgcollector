#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Forms to handle the installation of the server
"""

import ipaddress
import socket

from flask_wtf import Form
from wtforms import PasswordField, StringField, ValidationError, IntegerField
from wtforms.validators import DataRequired


# noinspection PyBroadException
def _validate_host(_, field: StringField) -> None:
    """
    Checks that the address is a valid host

    :param _: form, unused parameter
    :param field: the field for which to check the data
    :raise ValidationError: if the data cannot be converted to a valid network host
    """
    try:
        ipaddress.ip_address(field.data)
    except:
        try:
            socket.gethostbyname(field.data)
        except:
            raise ValidationError("The ip address is not valid or the hostname cannot be resolved")


def _validate_port(_, field: IntegerField) -> None:
    """
    Checks that the given field.data is a valid network port

    :param _: form, unused parameter
    :param field: the field for which to check the data
    :raise ValidationError: if the data is bigger than 65535 or smaller than 1
    """
    if field.data is not None and not 0 < field.data <= 65535:
        raise ValidationError("The port value should be between 0 and 65535")


class InstallationForm(Form):
    """
    Installation Form, used to setup the database
    """
    host = StringField("Host", [DataRequired(), _validate_host])
    port = IntegerField("Port", [_validate_port], default=3306)
    database = StringField("Name", [DataRequired()])
    username = StringField("Username", [DataRequired()])
    password = PasswordField("Password")
