# Author: FL42

"""
Define useful classes
"""


class Message:
    """
    Provide Message abstratction to communicate probe results
    """

    # Class attributes for severity
    ERROR = 40
    WARNING = 30
    INFO = 20

    def __init__(self, service, body, severity, header=None):
        self.service = service
        self.body = body
        self.severity = severity  # Expects values defined above
        self.header = header

    def __str__(self):
        return "{}{}: {}".format(
            "[{}] ".format(self.header) if self.header is not None else "",
            self.service,
            self.body
        )

    def __repr__(self):
        return "Message: service: {}, body: {}, " \
               "severity: {}, header: {}".format(
                   self.service,
                   self.body,
                   self.severity,
                   self.header
               )

    def __eq__(self, message):

        if self.service == message.service \
           and self.body == message.body \
           and self.severity == message.severity \
           and self.header == message.header:

            return True

        return False
