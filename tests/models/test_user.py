#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Tests for the User model. These tests are critical as they are our only guarantee that user data and configuration is
safely kept in our application
"""

import mysql.connector.errors
import unittest
from typing import Iterable

from tests import TestCaseWithDB
from lib.models import User


class TestUser(TestCaseWithDB, unittest.TestCase):
    """
    Defines tests for our User model
    """
    @classmethod
    def table_creation_commands(cls) -> Iterable[str]:
        """ commands to execute to setup the database for our tests """
        return [User.table_creation_command(), *User.table_constraints()]

    @classmethod
    def tables_to_truncate(cls) -> Iterable[str]:
        """ tables to empty after each test """
        return ["user"]

    def setUp(self):
        """ Creates two base users to reason about in our tests"""
        super().setUp()
        self.name1 = "goatsy"
        self.email1 = "goatsy@tdd.com"
        self.password1 = "verysecure"
        self.user1 = User(self.name1, self.email1, self.password1).create()

        self.name2 = "Impersonator"
        self.email2 = "bob"
        self.password2 = "notVeryInventive"
        self.user2 = User(self.name2, self.email2, self.password2).create()

    def test_check_password(self):
        """ Attest that passwords are correctly checked """
        self.assertTrue(self.user1.check_password("verysecure"))
        self.assertFalse(self.user1.check_password("NotVerySecure"))

    def test_get_user_by_name_or_mail(self):
        """ Checks user retrieval from the database """
        user_one = self.user1.get_user_by_name_or_mail(self.name1)
        user_two = self.user1.get_user_by_name_or_mail(self.email1)
        self.assertEqual(user_one, user_two)
        self.assertEqual(user_one, self.user1)

    def test_get_user_by_id(self):
        """ Checks that getting a user by id indeed returns the same user (also tests our __eq__ function) """
        user_id = self.user1.get_id()
        new_user = User.get_user_by_id(user_id)
        self.assertEqual(self.user1, new_user)

    def test_get_users(self):
        """ Checks user retrieval with limits """
        self.assertEqual(len(User.get_users()), 2)
        self.assertEqual(len(User.get_users(limit=0)), 0)
        User("goat", "goat@goatsy.com", "1234").create()
        self.assertEqual(len(User.get_users()), 3)
        self.assertEqual(len(User.get_users(limit=1)), 1)

    def test_set_admin(self):
        """ Checks the user admin works """
        self.assertFalse(self.user1.is_admin)

        self.user1.set_admin()
        self.assertTrue(self.user1.is_admin)
        self.assertTrue(User.get_user_by_id(self.user1.get_id()).is_admin)
        self.assertFalse(User.get_user_by_id(self.user2.get_id()).is_admin)

        self.user1.set_admin(False)
        self.assertFalse(self.user1.is_admin)
        self.assertFalse(User.get_user_by_id(self.user1.get_id()).is_admin)
        self.assertFalse(User.get_user_by_id(self.user2.get_id()).is_admin)

    def test_no_same_username(self):
        """ Checks that two users with the same username cannot be created """
        with self.assertRaises(mysql.connector.errors.IntegrityError):
            User("goatsy", "impersonator@goatsy.com", "1234").create()

    def test_no_same_emails(self):
        """ Checks that two users with the same email cannot be created """
        with self.assertRaises(mysql.connector.errors.IntegrityError):
            User("goat", "goatsy@tdd.com", "no").create()

    def test_no_email_and_username_same_on_two_users(self):
        """
        Checks that a username cannot be the same as the email as another user. This is a requirement for our login
        """
        with self.assertRaises(mysql.connector.errors.IntegrityError):
            User("goatsy@tdd.com", "goat@tsy.com", "hello").create()

        User("goat@tsy.com", "tdd@goat.com", "hello").create()
        with self.assertRaises(mysql.connector.errors.IntegrityError):
            User("goat", "goat@tsy.com", "no").create()

    def test_user_can_have_same_name_and_email(self):
        """ Checks that a user can have the same email and username """
        User("goat@tsy.com", "goat@tsy.com", "hi").create()
