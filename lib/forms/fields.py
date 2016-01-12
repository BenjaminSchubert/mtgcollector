#!/usr/bin/python3
# -*- coding: utf-8 -*-
from wtforms import Field
from wtforms.widgets import Input

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"



class SliderField(Field):
    class SliderWidget(Input):
        input_type = "text"

        def __call__(self, field, **kwargs):
            kwargs["class_"] = "slider span2"
            kwargs["data-slider-min"] = field.min_value
            kwargs["data-slider-max"] = field.max_value
            kwargs["data-slider-step"] = field.interval
            kwargs["data-slider-value"] = "[{}]".format(field._value())

            return super().__call__(field, **kwargs)

    widget = SliderWidget()

    def __init__(self, label, min_value, max_value, interval=1, **kwargs):
        super().__init__(label=label, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.interval = interval

    def _value(self):
        return "{},{}".format(self.min_value, self.max_value)

    def set_max_value(self, value):
        self.max_value = value
