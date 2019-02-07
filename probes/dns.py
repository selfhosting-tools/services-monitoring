# Author: FL42

"""
This probe tries to resolv the given domain using all domain's nameservers.

Parameters:
    service: (dict)
        domain: (str) domain to check
        ns_IPs: (list of str) IPs of nameservers to check
                If not given all NS servers will be checked.
        dnssec: (bool) Check DNSSEC resolution (default to False)
                Local resolver needs to handle DO bit (aka DNSSEC compatible)

Return:
    List of Message objects
    If the list is empty, all tests succeeded
"""

import logging
import dns.resolver
from tools import Message

log = logging.getLogger(__name__)


def get_ns_servers(domain):
    """
    Helper function used to get all NS servers of a domain.

    Parameter:
    domain: (str) domain to resolv

    Return:
    (list of str) : All IPs of nameservers of the given domain
    """
    log.debug("Autodiscovering NS servers...")
    ns_ips = []
    for ns_server in dns.resolver.query(domain, 'NS').rrset.items:
        ns_hostname = ns_server.to_text()
        for item in dns.resolver.query(ns_hostname, 'A').rrset.items:
            ns_ips.append(item.address)
            log.debug("NS server: %s (%s)", ns_hostname, item.address)
    return ns_ips


def test(service):
    """
    See module docstring
    """

    domain = service['domain']
    ns_ips = service.get('ns_IPs', None)
    dnssec = service.get('dnssec', False)
    service_name = "[dns] {}:".format(domain)

    # Auto-discover NS servers if not given
    if ns_ips is None:
        ns_ips = get_ns_servers(domain)

    results = []

    for ns_ip in ns_ips:

        # request object
        request = dns.message.make_query(domain, dns.rdatatype.A)
        if dnssec:
            request.flags |= dns.flags.AD

        # UDP mode
        try:
            response = dns.query.udp(request, ns_ip)
            if response.rcode() != 0:
                raise Exception('rcode is not 0')
        except Exception as resolver_exception:
            results.append(Message(service_name,
                                   "Failed to resolv domain (UDP mode): {}"
                                   .format(resolver_exception),
                                   Message.ERROR))

        # TCP mode
        try:
            response = dns.query.tcp(request, ns_ip)
            if response.rcode() != 0:
                raise Exception('rcode is not 0')
        except Exception as resolver_exception:
            results.append(Message(service_name,
                                   "Failed to resolv domain (TCP mode): {}"
                                   .format(resolver_exception),
                                   Message.ERROR))

        return results
