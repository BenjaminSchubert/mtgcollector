import unittest
from typing import Iterable

from tests import TestCaseWithDB
from lib.models.user import User


class TestUser(TestCaseWithDB, unittest.TestCase):
    @classmethod
    def table_creation_commands(cls) -> Iterable[str]:
        return [User.table_creation_command()]

    @property
    def tables_to_truncate(self) -> Iterable[str]:
        return ["user"]

    def setUp(self):
        super().setUp()
        self.user = User.create_user("goatsy", "goatsy@tdd.com", "verysecure")

    def test_check_password(self):
        self.assertTrue(self.user.check_password("verysecure"))
        self.assertFalse(self.user.check_password("NotVerySecure"))

    def test_get_user_by_name_or_mail(self):
        User.create_user("Impersonator", "bob", "notVeryInventive")
        user_one = self.user.get_user_by_name_or_mail("goatsy")
        user_two = self.user.get_user_by_name_or_mail("goatsy@tdd.com")
        self.assertEqual(user_one, user_two)
        self.assertEqual(user_one, self.user)

    def test_get_user_by_id(self):
        user_id = self.user.get_id()
        new_user = User.get_user_by_id(user_id)
        self.assertEqual(self.user, new_user)

    def test_get_users(self):
        self.assertEqual(len(User.get_users()), 1)
        self.assertEqual(len(User.get_users(limit=0)), 0)
        User.create_user("goat", "goat@goatsy.com", "1234")
        self.assertEqual(len(User.get_users()), 2)
        self.assertEqual(len(User.get_users(limit=1)), 1)

    def test_set_admin(self):
        self.assertFalse(self.user.is_admin)

        self.user.set_admin()
        self.assertTrue(self.user.is_admin)
        self.assertTrue(User.get_user_by_id(self.user.get_id()).is_admin)

        self.user.set_admin(False)
        self.assertFalse(self.user.is_admin)
        self.assertFalse(User.get_user_by_id(self.user.get_id()).is_admin)
