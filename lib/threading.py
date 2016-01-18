#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Threading event able to send data alongside the event
"""

import threading


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class Event(threading.Event):
    """
    Event able to send data with the event
    """
    def __init__(self):
        super().__init__()
        self.value = None

    def set_value(self, value: str):
        """
        send the event, passing it a value

        :param value: value to send to other threads
        """
        self.value = value
        super().set()

    def wait_value(self, timeout: int=0) -> str:
        """
        waits for a new value

        :param timeout: maximum timeout to wait
        :return: value sent with the event
        """
        event = super().wait(timeout)
        if not event:
            raise TimeoutError("No value was given during the given timeout")
        return self.value
