from django.urls import path

from .views import LimitsSimulateView, LimitsView

urlpatterns = [
    path("", LimitsView.as_view(), name="limits"),
    path("simulate/", LimitsSimulateView.as_view(), name="limits-simulate"),
]
