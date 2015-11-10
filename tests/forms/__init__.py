#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Tests the different forms to be sure that they correspond to what they need to do
"""

import abc

from tests import DBConnectionMixin


class BaseForm(metaclass=abc.ABCMeta):
    """
    Base class for testing forms. Defines the skeleton needed for this
    """
    @property
    @abc.abstractmethod
    def default_data(self):
        """ The default data that is to be entered in the form. """

    @property
    @abc.abstractmethod
    def submit_button(self) -> str:
        """ The submit button to confirm form """

    def fill_form(self, browser, **kwargs):
        """
        Completes the given form with the parameter in data

        :param browser: the browser to use to fill the form
        :param kwargs: these arguments allow overriding of the default data
        """
        for key, value in self.default_data.items():
            browser.find_element_by_id(key).clear()
            browser.find_element_by_id(key).send_keys(kwargs.get(key, value))

        browser.find_element_by_id(self.submit_button).click()

    def check_errors(self, test_instance, browser, element_with_error, error_regex):
        """
        Checks that the error message is displayed only once and in the correct place

        :param test_instance: the instance test to access asserts
        :param browser: the browser instance
        :param element_with_error: id value of the object on which the error should be applied
        :param error_regex: regex of the error message
        """
        errors = browser.find_elements_by_class_name("has-error")
        test_instance.assertEqual(len(errors), 1, "More than one object has errors")
        test_instance.assertEqual(
            errors[0].find_element_by_class_name("form-control").get_attribute("id"),
            element_with_error
        )

        help_blocks = errors[0].find_elements_by_class_name("help-block")
        test_instance.assertEqual(len(help_blocks), 1, "More than one help block has been defined")
        help_blocks = browser.find_elements_by_class_name("help-block")
        test_instance.assertEqual(len(help_blocks), 1, "More than one help block has been defined on the whole page")

        test_instance.assertRegex(help_blocks[0].find_elements_by_xpath("//p")[0].text, error_regex)

    @abc.abstractmethod
    def test(self, test_instance, browser):
        """
        Tests the form

        :param test_instance: the test instance used to run the tests to access asserts
        :param browser: the browser instance on which to test
        """


class InstallForm(BaseForm):
    """
    Form test for the first /install form
    """
    @property
    def default_data(self):
        """ Default data for the InstallForm, retrieved from the environment """
        return {
            "host": DBConnectionMixin.DATABASE_HOST,
            "database": DBConnectionMixin.DATABASE_NAME,
            "username": DBConnectionMixin.DATABASE_USER,
            "password": DBConnectionMixin.DATABASE_PASSWORD,
            "port": DBConnectionMixin.DATABASE_PORT
        }

    @property
    def submit_button(self):
        """ Name of the submit button """
        return "button_submit"

    def test(self, test_instance, browser):
        """
        Tests the install form

        :param test_instance: allows access to asserts
        :param browser: where to run the tests
        """
        self.fill_form(browser, host="HelloWorld")
        self.check_errors(test_instance, browser, "host", r".*ip.*or.*hostname")

        self.fill_form(browser, host="127.0.0.1")
        self.check_errors(test_instance, browser, "host", r"^Could not connect*")

        self.fill_form(browser, port="098098")
        self.check_errors(test_instance, browser, "port", ".*port value.*0.*65535.*")

        self.fill_form(browser, port="12.5")
        self.check_errors(test_instance, browser, "port", ".*valid integer.*")

        self.fill_form(browser, host="")
        self.check_errors(test_instance, browser, "host", "required")
        self.fill_form(browser, database="")
        self.check_errors(test_instance, browser, "database", "required")
        self.fill_form(browser, username="")
        self.check_errors(test_instance, browser, "username", "required")

        if self.default_data["password"] != "":
            self.fill_form(browser, password="")
            self.check_errors(test_instance, browser, "password", "credentials")

        self.fill_form(browser)


class AdminForm(BaseForm):
    """
    Form for the creation of an administrator during first setup
    """
    @property
    def default_data(self):
        """ Default data for the AdminForm, retrieved from the environment """
        return {
            "username": "tellendil",
            "password": "admin",
            "email": "tellendil@gmail.com"
        }

    @property
    def submit_button(self) -> str:
        """ The submit button name """
        return "button_submit"

    def test(self, test_instance, browser):
        """
        Test function for the Admin form

        :param test_instance: unittest instance for assert access
        :param browser: the browser on which to conduct the tests
        """
        self.fill_form(browser)


