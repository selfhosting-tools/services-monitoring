# Author: alex2242

"""
Tests for the https probe
"""

import unittest
from probes import https


class TestHTTPS(unittest.TestCase):
    """
    See module docstring
    """

    def test_http(self):
        """
        Should work
        """
        result = https.test({'url': 'http://google.fr/'})
        self.assertEqual(len(result), 0)

    def test_https(self):
        """
        Should work
        """
        result = https.test({'url': 'https://google.fr/'})
        self.assertEqual(len(result), 0)

    def test_https_and_cert(self):
        """
        Should work
        """
        result = https.test({
            'url': 'https://google.fr/',
            'verify_certificate': True
        })

        self.assertEqual(len(result), 0)
