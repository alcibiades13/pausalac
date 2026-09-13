from django.contrib.auth import authenticate, login, logout, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import AuditService

from .models import User
from .serializers import (
    EmailVerificationSerializer,
    LoginSerializer,
    MeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
)
from .services import TokenError, consume_email_verification_token, consume_password_reset_token
from .tasks import send_password_reset_email_task, send_verification_email_task


@method_decorator(ensure_csrf_cookie, name="get")
class CsrfView(APIView):
    """
    GET /api/v1/auth/csrf/ — primes the csrftoken cookie. Call this once on
    app boot; the SPA then echoes the cookie value back as X-CSRFToken on
    every mutating request (master prompt §49 session-based auth).
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"detail": "CSRF cookie set."})


class RegisterView(APIView):
    """
    Registration logs the user in immediately (session created) — an
    unverified email does not block trial value (§105); it just leaves
    `is_email_verified=False` until the link is clicked.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_verification_email_task.delay(user.id)
        login(request, user)

        AuditService.log(
            actor=user,
            entity_type="user",
            entity_id=user.id,
            action="registered",
            source="api",
        )
        return Response(MeSerializer(user).data, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = consume_email_verification_token(serializer.validated_data["token"])
        except TokenError as exc:
            raise exceptions.ValidationError({"token": str(exc)}) from exc

        if user.email_verified_at is None:
            user.email_verified_at = timezone.now()
            user.save(update_fields=["email_verified_at"])
            AuditService.log(
                actor=user, entity_type="user", entity_id=user.id, action="email_verified"
            )
        return Response({"detail": "Email adresa je potvrđena."})


class ResendVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.is_email_verified:
            return Response({"detail": "Email adresa je već potvrđena."})
        send_verification_email_task.delay(request.user.id)
        return Response({"detail": "Poslali smo novi link za potvrdu."})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            raise exceptions.AuthenticationFailed("Pogrešan email ili lozinka.")

        login(request, user)
        AuditService.log(actor=user, entity_type="user", entity_id=user.id, action="logged_in")
        return Response(MeSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        AuditService.log(
            actor=request.user, entity_type="user", entity_id=request.user.id, action="logged_out"
        )
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(MeSerializer(request.user).data)


class PasswordResetRequestView(APIView):
    """
    Always returns 200 regardless of whether the email is registered
    (prevents account enumeration) — only sends an email when it is.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(email__iexact=serializer.validated_data["email"]).first()
        if user is not None:
            send_password_reset_email_task.delay(user.id)
        return Response({"detail": "Ako nalog postoji, poslali smo link za resetovanje lozinke."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = consume_password_reset_token(data["uid"], data["token"])
        except TokenError as exc:
            raise exceptions.ValidationError({"token": str(exc)}) from exc

        try:
            password_validation.validate_password(data["new_password"], user=user)
        except DjangoValidationError as exc:
            raise exceptions.ValidationError({"new_password": exc.messages}) from exc

        user.set_password(data["new_password"])
        user.save(update_fields=["password"])

        AuditService.log(
            actor=user, entity_type="user", entity_id=user.id, action="password_reset"
        )
        return Response({"detail": "Lozinka je uspešno promenjena."})
