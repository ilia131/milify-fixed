import logging
from smtplib import SMTPException
from urllib.parse import urlsplit

from django.conf import settings
from djoser.email import PasswordResetEmail


logger = logging.getLogger(__name__)


class MilifyPasswordResetEmail(PasswordResetEmail):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        frontend = urlsplit(settings.FRONTEND_URL)
        return {**context, "domain": frontend.netloc, "protocol": frontend.scheme}

    def send(self, to, **kwargs):
        try:
            return super().send(to, **kwargs)
        except (OSError, SMTPException):
            logger.error("Password reset email delivery failed")
