# Author: alex2242

"""
Tools for TLS connection
"""

from socket import socket
from OpenSSL.SSL import TLSv1_2_METHOD, Context, Connection


def get_certificate(hostname, port=443):
    """
    Return TLS certificate (f.i. for https or smtps)
    """

    client = socket()
    client.connect((hostname, port))

    client_ssl = Connection(Context(TLSv1_2_METHOD), client)
    client_ssl.set_connect_state()
    client_ssl.set_tlsext_host_name(hostname.encode("ascii"))  # SNI
    client_ssl.do_handshake()

    cert = client_ssl.get_peer_certificate()

    client_ssl.close()

    return cert
