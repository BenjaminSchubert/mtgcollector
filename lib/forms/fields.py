#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Custom fields expanding on WTForms
"""

from wtforms import Field, SelectMultipleField, widgets

from lib.forms.widgets import SliderWidget, GroupWidget, StartSeparatorWidget, StopSeparatorWidget

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class SliderField(Field):
    """
    Represent a slider, allowing to easily choose an interval

    :param label: name of the slider
    :param min_value: minimum value the slider can take
    :param max_value: maximum value the slider can take
    :param interval: interval between each values
    :param kwargs: arguments passed to Field
    """
    widget = SliderWidget()

    def __init__(self, label: str, min_value: int, max_value: int, interval: int=1, **kwargs):
        super().__init__(label=label, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.interval = interval

    def _value(self) -> str:
        """ represents the interval as a csv 'min,max' """
        return "{},{}".format(self.min_value, self.max_value)

    def set_max_value(self, value: int) -> None:
        """
        Allows for post-initialization setting of the maximum value

        :param value: new value to set
        """
        self.max_value = value


class MultiCheckboxField(SelectMultipleField):
    """
    Groups a set of checkboxes into the same display block
    """
    widget = GroupWidget()
    option_widget = widgets.CheckboxInput()


class StartSeparatorField(Field):
    """
    Field used to create a subsection in a form. Anything below it and before a StopSeparatorField will be
    contained in a group to allow better scaling of the form on displays
    """
    widget = StartSeparatorWidget()


class StopSeparatorField(Field):
    """
    Field used to create a subsection in a form. Determines the end of a subsection openned by a
    StartSeparatorField
    """
    widget = StopSeparatorWidget()
