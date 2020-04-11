# Author: FL42

"""
Tests for the smtp probe
"""

import unittest
from src.probes import smtp


class Testsmtp(unittest.TestCase):
    """
    See module docstring
    """

    def test_valid_smtp(self):
        """
        Should work
        """
        results = smtp.test({
            'host': 'smtp.gmail.com',
            'port': 587
        })

        self.assertEqual(len(results), 0)

    def test_invalid_smtp(self):
        """
        Should not work (invalid domain)
        """
        results = smtp.test({
            'host': 'mail.example.com',
            'port': 587
        })

        self.assertTrue(len(results) > 0)
