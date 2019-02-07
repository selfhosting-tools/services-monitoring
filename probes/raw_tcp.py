# Author: FL42

"""
Parameters:
    service: (dict)
        host: (str) host to check (hostname or ip address)
        port: (int) port to check
        timeout: (int) (optional) timeout in seconds (default to 1)

Return:
    List of Message objects
    If the list is empty, the test succeeded (i.e. port is open)
"""

import logging
import socket
from tools import Message

log = logging.getLogger(__name__)


def test(service):
    """
    See module docstring
    """
    host = service['host']
    port = service['port']
    timeout = service.get('timeout', 1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.close()
    except Exception as socket_exception:
        return [
            Message(
                body="{}".format(socket_exception),
                severity=Message.ERROR,
                service="[raw_tcp] {}:{}".format(host, port)
            )
        ]
    return []
