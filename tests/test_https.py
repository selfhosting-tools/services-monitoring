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
        result = https.test({'url': 'http://google.fr'})
        self.assertEqual(len(result), 0)

    def test_https(self):
        """
        Should work
        """
        result = https.test({'url': 'https://google.fr'})
        self.assertEqual(len(result), 0)

    def test_https_badssl_expired_cert(self):
        """
        Expired cert
        """
        result = https.test({'url': 'https://expired.badssl.com'})
        self.assertTrue(len(result) > 0)

    def test_https_badssl_expired_cert_disabled_verification(self):
        """
        Expired cert but verification is disabled
        """
        result = https.test({
            'url': 'https://expired.badssl.com',
            'verify_certificate': False
        })
        self.assertEqual(len(result), 0)

    def test_https_badssl_wrong_host(self):
        """
        Wrong host
        """
        result = https.test({'url': 'https://wrong.host.badssl.com'})
        self.assertTrue(len(result) > 0)

    def test_https_badssl_self_signed_cert(self):
        """
        Self-signed cert
        """
        result = https.test({'url': 'https://self-signed.badssl.com'})

        self.assertTrue(len(result) > 0)

    def test_https_badssl_untrusted_root_cert(self):
        """
        Untrusted root
        """
        result = https.test({'url': 'https://untrusted-root.badssl.com'})
        self.assertTrue(len(result) > 0)

# FIXME: should fail
#    def test_https_badssl_revoked(self):
#        """
#        Revoked cert
#        """
#        result = https.test({'url': 'https://revoked.badssl.com'})
#        self.assertTrue(len(result) > 0)


# TODO: should be mocked
#    def test_https_tlsa(self):
#        """
#        Should work
#        """
#        result = https.test({
#            'url': 'https://good.dane.huque.com/',
#            'check_tlsa': True
#        })
#        self.assertEqual(len(result), 0)


    def test_https_invalid_tlsa(self):
        """
        Should not work
        """
        result = https.test({
            'url': 'https://badsig.dane.huque.com/',
            'check_tlsa': True
        })
        self.assertTrue(len(result) > 0)

    def test_https_invalid_tlsa_verification_disabled(self):
        """
        Should not work but check is disabled
        """
        result = https.test({
            'url': 'https://badsig.dane.huque.com/',
            'check_tlsa': False
        })
        self.assertEqual(len(result), 0)
