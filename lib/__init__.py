# -*- coding: utf-8 -*-
import inspect


def get_subclasses(base_class: callable) -> list:
    """
    Gets all non abstract subclasses for a given base class

    :param base_class: the base class of which to find children
    :return: list of all programs
    """
    all_subclasses = []

    for subclass in base_class.__subclasses__():
        if not inspect.isabstract(subclass):
            all_subclasses.append(subclass)
        all_subclasses.extend(get_subclasses(subclass))

    return all_subclasses
