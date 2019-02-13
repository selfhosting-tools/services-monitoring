# Author: FL42

"""
Parameter:
    host: host to ping

Return:
    True if host is reachable else False
"""

import logging
import subprocess

from tools import Message

log = logging.getLogger(__name__)


def test(host):
    """
    See module docstring
    """
    returncode = subprocess.call(["ping", "-c", "1", "-W", "1", host])
    if returncode == 1:
        return [
            Message(
                body="Host is not reachable",
                severity=Message.ERROR,
                service="[ping] {}".format(host)
            )
        ]
    if returncode == 2:
        return [
            Message(
                body="Invalid host",
                severity=Message.ERROR,
                service="[ping] {}".format(host)
            )
        ]
    return []
