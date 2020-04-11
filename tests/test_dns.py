# Author: FL42

"""
Tests for the dns probe
"""

import unittest
from src.probes import dns


class TestDNS(unittest.TestCase):
    """
    See module docstring
    """

    def test_valid_domain(self):
        """
        Should work
        """
        results = dns.test({
            'domain': 'google.fr',
            'ns_IPs': ['8.8.8.8']
        })
        self.assertEqual(len(results), 0)

    def test_valid_domain_with_ns_discovering(self):
        """
        Should work
        """
        results = dns.test({
            'domain': 'google.fr'
        })
        self.assertEqual(len(results), 0)

    def test_nx_domain(self):
        """
        Should not work (nx domain)
        """
        results = dns.test({
            'domain': 'ImD5elFzdR77QDl7.com',
            'ns_IPs': ['8.8.8.8']
        })
        self.assertTrue(len(results) > 0)

    def test_valid_dnssec_domain(self):
        """
        Should work
        """
        results = dns.test({
            'domain': 'internetsociety.org',
            'ns_IPs': ['8.8.8.8'],
            'dnssec': True
        })
        self.assertEqual(len(results), 0)

    def test_invalid_dnssec_domain(self):
        """
        Should not work (invalid dnssec)
        """
        results = dns.test({
            'domain': 'dnssec-failed.org',
            'ns_IPs': ['8.8.8.8'],
            'dnssec': True
        })
        self.assertTrue(len(results) > 0)

    def test_invalid_dnssec_domain_dnssec_disabled(self):
        """
        Should work (DNSSEC disabled)
        """
        results = dns.test({
            'domain': 'dnssec-failed.org',
            'ns_IPs': ['8.8.8.8'],
            'dnssec': False
        })
        self.assertTrue(len(results) > 0)
