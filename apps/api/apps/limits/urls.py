from django.urls import path

from .views import LimitHistoryView, LimitsSimulateView, LimitsView

urlpatterns = [
    path("", LimitsView.as_view(), name="limits"),
    path("simulate/", LimitsSimulateView.as_view(), name="limits-simulate"),
    path("pausal/history/", LimitHistoryView.as_view(), name="limits-pausal-history"),
]
