from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.companies.permissions import HasActiveCompany

from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService


class NotificationViewSet(ListModelMixin, GenericViewSet):
    """Always scoped to the requester's own in_app rows — email rows are
    an internal delivery record, never shown in this feed. No RBAC
    codename beyond company membership: results are already hard-scoped
    to `recipient=request.user`."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveCompany]

    def get_queryset(self):
        queryset = Notification.objects.for_company(self.request.company).filter(
            recipient=self.request.user, channel=Notification.Channel.IN_APP
        )
        is_read = self.request.query_params.get("is_read")
        if is_read == "false":
            queryset = queryset.filter(read_at__isnull=True)
        elif is_read == "true":
            queryset = queryset.filter(read_at__isnull=False)
        return queryset

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None, *args, **kwargs):
        notification = self.get_object()
        notification = NotificationService.mark_read(notification)
        return Response(self.get_serializer(notification).data)
