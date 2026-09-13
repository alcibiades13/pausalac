"""
Email verification and password reset token handling. Uses Django's own
signed-token primitives (`django.core.signing`, `PasswordResetTokenGenerator`)
rather than a hand-rolled scheme (master prompt §49: "use established
Django security patterns").
"""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import User

_EMAIL_VERIFICATION_SALT = "accounts.email-verification"
_EMAIL_VERIFICATION_MAX_AGE = 60 * 60 * 24 * 3  # 3 dana


class TokenError(Exception):
    """Raised for any invalid/expired token — callers turn this into a 400."""


def make_email_verification_token(user: User) -> str:
    return signing.dumps({"user_id": user.pk}, salt=_EMAIL_VERIFICATION_SALT)


def consume_email_verification_token(token: str) -> User:
    try:
        data = signing.loads(
            token, salt=_EMAIL_VERIFICATION_SALT, max_age=_EMAIL_VERIFICATION_MAX_AGE
        )
    except signing.BadSignature as exc:
        raise TokenError("Link za potvrdu email adrese nije validan ili je istekao.") from exc

    try:
        return User.objects.get(pk=data["user_id"])
    except User.DoesNotExist as exc:
        raise TokenError("Korisnik ne postoji.") from exc


def email_verification_link(user: User) -> str:
    token = make_email_verification_token(user)
    return f"{settings.FRONTEND_URL}/verifikacija-emaila?token={token}"


def make_password_reset_tokens(user: User) -> tuple[str, str]:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uidb64, token


def password_reset_link(user: User) -> str:
    uidb64, token = make_password_reset_tokens(user)
    return f"{settings.FRONTEND_URL}/nova-lozinka?uid={uidb64}&token={token}"


def consume_password_reset_token(uidb64: str, token: str) -> User:
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
        raise TokenError("Link za resetovanje lozinke nije validan.") from exc

    if not default_token_generator.check_token(user, token):
        raise TokenError("Link za resetovanje lozinke nije validan ili je istekao.")

    return user
