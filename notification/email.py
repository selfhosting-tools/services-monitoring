# Author: FL42

"""
Parameters:
    subject: (str) subject of the email
    body: (str) body of the email
    config: (dict) config of the smtp server to use
                   keys: host, port, user, password,
                         recipient_address, sender_address

Return:
    (bool) message was sent
"""

import logging
from smtplib import SMTP
from email.utils import formatdate
from email.mime.text import MIMEText

log = logging.getLogger(__name__)


def send_email(subject, body, config):
    """
    See module docstring
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config['sender_address']
    msg['To'] = config['recipient_address']
    msg['Date'] = formatdate(localtime=True)

    try:
        smtp_fd = SMTP(host=config['host'],
                       port=config['port'],
                       local_hostname=config['sender_address'].split('@')[0],
                       timeout=2
                       )
        if config['user'] is not None and config['password'] is not None:
            smtp_fd.login(config['user'], config['password'])
        smtp_fd.send_message(msg)
        smtp_fd.quit()
    except Exception as smtp_exception:
        log.exception(smtp_exception)
        return False
    return True
