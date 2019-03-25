"""
Tests for the tlsa tool
"""

import unittest

from tools import TLSA, tls


class TestTLSA(unittest.TestCase):
    """
    See module docstring
    """

    def test_good_tlsa(self):
        """
        Good TLSA (cert matching)
        """
        hostname = "good.dane.huque.com"
        cert = tls.get_certificate(hostname)

        tlsa_checker = TLSA("test")
        results = tlsa_checker.check_tlsa(hostname, 443, cert)

        self.assertEqual(len(results), 0)

# TODO: Not yet supported
#    def test_good_ca_tlsa(self):
#        """
#        Good TLSA (CA matching)
#        """
#        hostname = "good-pkixta.dane.huque.com"
#        cert = tls.get_certificate(hostname)
#
#        tlsa_checker = TLSA("test")
#        results = tlsa_checker.check_tlsa(hostname, 443, cert)
#
#        self.assertEqual(len(results), 0)

    def test_bad_hash_tlsa(self):
        """
        Bad TLSA (bad hash)
        """
        hostname = "badhash.dane.huque.com"
        cert = tls.get_certificate(hostname)

        tlsa_checker = TLSA("test")
        results = tlsa_checker.check_tlsa(hostname, 443, cert)

        self.assertTrue(len(results) > 0)

    def test_bad_param_tlsa(self):
        """
        Bad TLSA (bad param)
        """
        hostname = "badparam.dane.huque.com"
        cert = tls.get_certificate(hostname)

        tlsa_checker = TLSA("test")
        results = tlsa_checker.check_tlsa(hostname, 443, cert)

        self.assertTrue(len(results) > 0)

    def test_bad_sig_tlsa(self):
        """
        Bad TLSA (bad sig)
        """
        hostname = "badsig.dane.huque.com"
        cert = tls.get_certificate(hostname)

        tlsa_checker = TLSA("test")
        results = tlsa_checker.check_tlsa(hostname, 443, cert)

        self.assertTrue(len(results) > 0)

    def test_expired_sig_tlsa(self):
        """
        Bad TLSA (expired sig)
        """
        hostname = "expiredsig.dane.huque.com"
        cert = tls.get_certificate(hostname)

        tlsa_checker = TLSA("test")
        results = tlsa_checker.check_tlsa(hostname, 443, cert)

        self.assertTrue(len(results) > 0)
