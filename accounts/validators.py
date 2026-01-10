import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UppercaseValidator:
    """
    Validate that the password contains at least one uppercase letter.
    """
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter.")


class LowercaseValidator:
    """
    Validate that the password contains at least one lowercase letter.
    """
    def validate(self, password, user=None):
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _("Your password must contain at least one lowercase letter.")


class NumberValidator:
    """
    Validate that the password contains at least one digit.
    """
    def validate(self, password, user=None):
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("This password must contain at least one number."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _("Your password must contain at least one number.")
