#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Custom form validators for our application
"""

import ipaddress

from wtforms import StringField, ValidationError, IntegerField

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


# noinspection PyBroadException
def validate_host(_, field: StringField) -> None:
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
            # noinspection PyUnresolvedReferences
            socket.gethostbyname(field.data)
        except:
            raise ValidationError("The ip address is not valid or the hostname cannot be resolved")


def validate_port(_, field: IntegerField) -> None:
    """
    Checks that the given field.data is a valid network port

    :param _: form, unused parameter
    :param field: the field for which to check the data
    :raise ValidationError: if the data is bigger than 65535 or smaller than 1
    """
    if field.data is not None and not 0 < field.data <= 65535:
        raise ValidationError("The port value should be between 0 and 65535")
