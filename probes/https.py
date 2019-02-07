# Author: alex2242

"""
This probe checks if status code is 2XX or 3XX.

Parameters:
    url: (str) url to check (http or https protocols)
    verify_certificate: (bool) check validity of SSL certificate
    check_tlsa: (bool) check validity of TLSA record
    redirection: (bool) check if url redirects to another url (3XX codes)

Return:
    List of Message objects
    If the list is empty, all tests succeeded
"""

import logging
from datetime import datetime, timedelta

import requests
import urllib3

from tools import Message, tls

log = logging.getLogger(__name__)

# Disable warning for doing HTTPS requests with verify_certificate set to False
urllib3.disable_warnings()


def test(service):
    """
    See module docstring
    """

    url = service['url']
    verify_certificate = service.get('verify_certificate', True)
    # check_tlsa = service.get('check_tlsa', False)  # check 'tlsa' branch
    redirection = service.get('redirection', False)
    service_name = "[https] {}".format(url)

    results = []

    try:
        request = requests.get(
            url,
            verify=verify_certificate,
            headers={
                'user-agent': 'services-monitoring/v1'
            },
            timeout=5
        )

    # Handle timeout
    except requests.exceptions.Timeout:
        results.append(Message(
            service_name,
            "Time out",
            Message.ERROR
        ))
        return results

    except Exception as request_exception:
        results.append(Message(
            service_name,
            "Exception: {}".format(request_exception),
            Message.ERROR
        ))
        return results

    # Fail if error code is not 2XX/3XX or TLS error
    if not request.ok:
        results.append(Message(
            service_name,
            "Request failed (status code: {})"
            .format(request.status_code),
            Message.ERROR
        ))

    # Check if url redirects to another url (3XX codes)
    if redirection:
        first_response = request.history[0] if request.history else request
        if not first_response.is_redirect:
            results.append(Message(
                service_name,
                "Not a redirection",
                Message.ERROR
            ))

    # For https check certificate expiration date and TLSA (if requested)
    parsed_url = urllib3.util.parse_url(url)
    if parsed_url.scheme == 'https':

        # Get certificate
        port = parsed_url.port if parsed_url.port is not None else 443
        cert = tls.get_certificate(parsed_url.host, port)

        # Check if certificate has expired or will expire soon
        not_before = datetime.strptime(
            cert.get_notBefore().decode('ascii'),
            '%Y%m%d%H%M%SZ'
        )

        not_after = datetime.strptime(
            cert.get_notAfter().decode('ascii'),
            '%Y%m%d%H%M%SZ'
        )
        log.debug(
            "Certificate: not_before: %s, not_after: %s",
            str(not_before),
            str(not_after)
        )

        now = datetime.utcnow()

        if now < not_before or now > not_after:
            results.append(Message(
                service_name,
                "Certificate has expired",
                Message.ERROR
            ))
        elif now + timedelta(hours=48) > not_after:
            results.append(Message(
                service_name,
                "Certificate will expire in less than 48 hours",
                Message.ERROR
            ))
        elif now + timedelta(days=7) > not_after:
            results.append(Message(
                service_name,
                "Certificate will expire in less than 7 days",
                Message.WARNING
            ))

    return results
