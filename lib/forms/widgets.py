#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Widgets to control the display of forms
"""

from wtforms.widgets import html_params, HTMLString, Input, CheckboxInput

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class GroupWidget:
    """
    Widget to display a group of sub-fields as a whole
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<%s %s>' % ("div", html_params(**kwargs)), '<div class="row">']

        counter = 0
        for subfield in field:
            counter += subfield.size
            if counter > 12:
                counter = subfield.size
                html.extend(["</div>", '<div class="row">'])

            html.append('<span class="col-md-%s">%s %s</span>' % (subfield.size, subfield(), subfield.label))

        html.extend(['</div>', '</%s>' % "div"])
        return HTMLString(''.join(html))


class SliderWidget(Input):
    """
    Widget to display bootstrap sliders
    """
    input_type = "text"

    def __call__(self, field, **kwargs):
        kwargs["class_"] = "slider span2"
        kwargs["data-slider-min"] = field.min_value
        kwargs["data-slider-max"] = field.max_value
        kwargs["data-slider-step"] = field.interval
        # noinspection PyProtectedMember
        kwargs["data-slider-value"] = "[{}]".format(field._value())

        return super().__call__(field, **kwargs)


class StartSeparatorWidget(Input):
    """
    Widget to display the beginning of a subsection in a form.
    """
    def __call__(self, field, **kwargs):
        return HTMLString('<div %s>' % self.html_params(class_="panel panel-danger col-md-4 col-lg-4 col-sm-12"))


class StopSeparatorWidget(Input):
    """
    Widget to display the end of a subsection in a form
    """
    def __call__(self, field, **kwargs):
        return HTMLString('</div>')
