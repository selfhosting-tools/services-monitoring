# Author: FL42

"""
Parameters:
    service: (dict)
        host: (str) host to check
        port: (int) port to check (default to 25)
        check_tlsa: (bool) check validity of the SMTP TLSA record
                    (default to False)

Return:
    List of Message objects
    If the list is empty, all tests succeeded
"""

import logging
import smtplib
from datetime import datetime, timedelta
from re import match

import OpenSSL.crypto

from src.tools import TLSA, Message

log = logging.getLogger(__name__)


def test(service):
    """
    See module docstring
    """

    host = service['host']
    port = service.get('port', 25)
    check_tlsa = service.get('check_tlsa', False)
    service_name = "[smtp] {}:{}".format(host, port)

    # This list will store warnings or errors.
    results = []

    # Fetch certificate
    try:
        connection = smtplib.SMTP('{}:{}'.format(host, port), timeout=10)
        connection.starttls()
    except Exception as connection_exception:
        results.append(Message(
            service_name,
            "Failed to connect: {}"
            .format(connection_exception),
            Message.ERROR
        ))

        return results  # Future tests will necessarily fail

    # Parse peer certificate
    cert = OpenSSL.crypto.load_certificate(
        OpenSSL.crypto.FILETYPE_ASN1,
        connection.sock.getpeercert(
            binary_form=True
        )
    )

    connection.quit()

    # Check if hostname is correct
    common_name = dict(
        cert.get_subject().get_components()
    )[b'CN'].decode('ascii')

    if '*' in common_name:  # wildcard cert
        if match('.{}$'.format(common_name), host) is None:
            results.append(Message(
                service_name,
                "Common name {} does not match host {}"
                .format(common_name, host),
                Message.ERROR
            ))
    else:
        if common_name != host:
            results.append(Message(
                service_name,
                "Common name {} does not match host {}"
                .format(common_name, host),
                Message.ERROR
            ))

    # Check if certificate has expired or will expire soon
    not_before = datetime.strptime(
        cert.get_notBefore().decode('ascii'),
        '%Y%m%d%H%M%SZ'
    )

    not_after = datetime.strptime(
        cert.get_notAfter().decode('ascii'),
        '%Y%m%d%H%M%SZ'
    )

    now = datetime.utcnow()

    if now < not_before or now > not_after:
        results.append(Message(
            service_name,
            "Certificate has expired",
            Message.ERROR
        ))
    elif now + timedelta(hours=72) > not_after:
        results.append(Message(
            service_name,
            "Certificate will expire in less than 72 hours",
            Message.ERROR
        ))

    if check_tlsa:
        tlsa_checker = TLSA(service_name)
        results += tlsa_checker.check_tlsa(host, port, cert)

    return results
