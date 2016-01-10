#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class Event(threading.Event):
    def __init__(self):
        super().__init__()
        self.value = None

    def set_value(self, value):
        self.value = value
        super().set()

    def clear(self):
        super().clear()

    def wait_value(self, timeout=0):
        event = super().wait(timeout)
        if not event:
            raise TimeoutError("No value was given during the given timeout")
        return self.value
