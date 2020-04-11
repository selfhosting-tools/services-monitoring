# Authors: FL42 & alex2242

"""
Tools for TLSA records
"""


import hashlib
import logging

import dns.resolver
import OpenSSL.crypto

from src.tools.message import Message

log = logging.getLogger(__name__)


class TLSA:
    """
    Useful methods for TLSA records
    """

    def __init__(self, service_name):
        """
        Init
        """
        self.service_name = service_name
        self.messages = []

    def check_tlsa(self, host, port, cert):
        """
        Check if TLSA record is valid.

        Parameters:
            host: (str)
            port: (int)
            cert: (OpenSSL cert object)

        Return:
            List of Message objects
            If the list is empty, all tests succeeded
        """

        dns_records = self._get_records(host, port)
        if not dns_records:
            return self.messages

        one_match = False
        log.debug('dns_records: %s', str(dns_records))
        for record in dns_records:
            log.debug("[TLSA] checking '%s'", record)
            splitted_record = record.split(' ')

            if len(splitted_record) != 4:
                log.warning(
                    "[%s] TLSA record is malformed (not 4 fields): ignored",
                    self.service_name
                )
                continue

            tlsa_hash = splitted_record[3]
            try:
                (certificate_usage, selector, matching_type) = [
                    int(s) for s in splitted_record[:3]
                ]
            except ValueError:
                log.warning(
                    "[%s] TLSA record is malformed: ignored",
                    self.service_name
                )
                continue

            # Only comparaison of hash is supported (no CA trust)
            if certificate_usage not in (1, 3):
                log.warning(
                    "[%s] TLSA record is malformed: ignored",
                    self.service_name
                )
                continue

            if certificate_usage == 1:  # cert must be trusted by a CA
                # TODO: Check if cert is trusted
                # For https it's not an issue as requests checks cert validity
                log.debug(
                    "certificate usage is 1 but the validity of the "
                    "certificate will not be verified (not implemented)"
                )

            cert_hash = self._get_hash(cert, selector, matching_type)

            is_matching = tlsa_hash == cert_hash
            log.debug("TLSA record matches cert: %s", str(is_matching))

            one_match |= is_matching

        if not one_match:
            self.messages.append(Message(
                self.service_name,
                "No TLSA record matches the certificate",
                Message.ERROR
            ))

        return self.messages

    def _get_records(self, host, port, protocol='tcp'):
        """
        Parameters:
            host: (str) Host of service
            port: (int) Port of service
            protocol: (str) Protocol of service (default to 'tcp')

        Return:
        (list of str) e.g. ['1 0 1 2f9bc...']
        """

        try:
            dns_answer = dns.resolver.query(
                '_{}._{}.{}'.format(port, protocol.lower(), host),
                'TLSA'
            ).response.answer

        except dns.resolver.NXDOMAIN:
            self.messages.append(Message(
                self.service_name,
                "TLSA record does not exist",
                Message.ERROR
            ))
            return []

        except Exception as dns_resolver_exception:
            self.messages.append(Message(
                self.service_name,
                "Failed to fetch TLSA record: {}"
                .format(dns_resolver_exception),
                Message.ERROR
            ))
            return []

        return [record.to_text() for record in dns_answer[0].items]

    def _get_hash(self, cert, selector, matching_type):
        """
        Compute the hash of the certificate

        Parameters:
        cert: (OpenSSL cert) TLS certificate
        selector: (int) TLSA selector
        matching_type: (int) TLSA matching type

        Return:
        (str) hash or '' on error
        """

        if selector == 0:  # entire cert
            x509_dump = OpenSSL.crypto.dump_certificate(
                OpenSSL.crypto.FILETYPE_ASN1,
                cert
            )
            log.debug("Hashing entire cert")

        elif selector == 1:  # public key only
            x509_dump = OpenSSL.crypto.dump_publickey(
                OpenSSL.crypto.FILETYPE_ASN1,
                cert.get_pubkey()
            )
            log.debug("Hashing public key only")

        else:  # invalid selector
            self.messages.append(Message(
                self.service_name,
                "Invalid selector in TLSA record",
                Message.ERROR
            ))
            log.debug("Invalid selector: %d", selector)
            return ''

        if matching_type == 1:
            hash_algo = hashlib.sha256()
            log.debug("Hashing with sha256")
        elif matching_type == 2:
            hash_algo = hashlib.sha1()
            log.debug("Hashing with sha1")
        else:
            self.messages.append(Message(
                self.service_name,
                "Invalid matching type in TLSA record",
                Message.ERROR
            ))
            log.debug("Invalid matching type: %d", matching_type)
            return ''

        hash_algo.update(x509_dump)

        digest = hash_algo.hexdigest()
        log.debug("hexdigest: %s", digest)

        return digest
