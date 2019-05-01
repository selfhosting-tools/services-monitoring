# Author: FL42

"""
Send an email

Parameters:
    subject: (str) subject of the email
    body: (str) body of the email
    smtp_config (dict):
        host: (str) smtp host server
        port: (int) smtp port (default to 587)
        starttls: (bool) enable STARTTLS (default to True)
        user: (str or None) smtp user (or None)
        password: (str or None) smtp password (or None)
        recipient_address: (str) recipient address
        sender_address: (str) sender address

Return:
    (bool) message was sent
"""

import logging
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP, SMTPResponseException

log = logging.getLogger(__name__)


def send_email(subject, body, smtp_config):
    """
    See module docstring
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_config['sender_address']
    msg['To'] = smtp_config['recipient_address']
    msg['Date'] = formatdate(localtime=True)

    try:
        smtp_fd = SMTP(
            host=smtp_config['host'],
            port=smtp_config.get('port', 587)
        )
        log.debug("Connexion opened to %s", smtp_config['host'])

        if smtp_config.get('starttls', True):
            smtp_fd.starttls()
            log.debug("STARTTLS has succeeded")
        else:
            log.debug("SMTP is in PLAIN (no STARTTLS)")

        smtp_user = smtp_config.get('user', None)
        smtp_password = smtp_config.get('password', None)
        if smtp_user is not None and smtp_password is not None:
            smtp_fd.login(smtp_user, smtp_password)
            log.debug("SMTP login has succeeded")
        else:
            log.debug("No login given for SMTP")

        smtp_fd.send_message(msg)
        log.debug("Message sent")

        smtp_fd.quit()

    except (SMTPResponseException, OSError) as smtp_exception:
        log.exception(smtp_exception)
        return False
    return True
