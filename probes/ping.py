# Author: alex2242

"""
Parameter:
    host: host to ping

Return:
    True if host is reachable else False
"""

import logging
import re
import socket
import subprocess
from tools import Message

log = logging.getLogger(__name__)


class Ping:
    """Provide tools for ping"""
    DOMAIN_RE = re.compile(r"^([a-z]+\.)*[a-z]+\.(fr|org|com)$")

    def __init__(self, host, count=4):
        is_ip4 = Ping._check_ip4(host)
        is_domain = Ping.DOMAIN_RE.match(host)

        if not is_ip4 and not is_domain:
            raise Exception("Unsupported host")

        if is_domain:
            try:
                resolved_host = socket.gethostbyname(host)
                self.host = resolved_host
                self.hostname = host
            except socket.gaierror:
                log.error("Name or service not known")
                exit(1)
        else:
            self.host = host
            self.hostname = host

        self.count = count

    def test(self):
        """ test if the host responds to ping """
        args = ["ping", "-c", str(self.count), self.host]
        res = subprocess.run(args, capture_output=True)

        stdout = res.stdout.decode("ascii").split("\n")

        stats = self._parse_ping_stats(stdout[-4:])

        if stats["received"] is self.count:
            log.info(
                "host %s is reachable with %s ms of latency",
                self.host, stats["avg"])
            msg = []

        elif stats["received"] > 0:
            log.warning(
                "host %s reachable, %s ms latency, %s percent of loss",
                self.hostname, stats["avg"], stats["loss"]
            )

            msg = []

        else:
            log.error("could not reach host %s", self.hostname)
            msg = [
                Message(
                    "Ping",
                    "Could not reach host {}".format(self.hostname),
                    Message.ERROR)
            ]

        return msg

    def _parse_ping_stats(self, stats):
        """
        Parse the last 4 lines of the
        ping command and extract stats of it
        """
        # parse header as:
        # --- 127.0.0.1 ping statistics ---
        header_match = stats[0] == "--- {} ping statistics ---"\
            .format(self.host)

        if not header_match or len(stats) != 4:
            print(stats[0])
            raise RuntimeError("Unrecognized ping stats")

        parsed_stats = {}

        # parse 2nd line as:
        # 1 packets transmitted, 1 received, 0% packet loss, time 0ms
        second_line = [s.strip() for s in stats[1].split(",")]
        parsed_stats["received"] = int(second_line[1].split(" ")[0])

        # in this case, there is nothing else to be parsed
        if parsed_stats["received"] == 0:
            return parsed_stats

        # parse 3th line as:
        # rtt min/avg/max/mdev = 0.054/0.054/0.054/0.000 ms
        third_line = stats[2].split(" ")[3].split("/")
        parsed_stats["min"] = third_line[0]
        parsed_stats["avg"] = third_line[1]
        parsed_stats["max"] = third_line[2]

        parsed_stats["loss"] = parsed_stats["received"] / self.count

        return parsed_stats

    @staticmethod
    def _check_ip4(ip4):
        ip_bytes = ip4.split(".")

        if not len(ip_bytes) == 4:
            return False

        for byte in [int(b) for b in ip_bytes]:
            if byte > 255 or byte < 0:
                return False

        return True
