from django.urls import path

from .views import ActivatePlanView, CancelSubscriptionView, PlanListView, SubscriptionView

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="subscription-plans"),
    path("current/", SubscriptionView.as_view(), name="subscription-current"),
    path("activate/", ActivatePlanView.as_view(), name="subscription-activate"),
    path("cancel/", CancelSubscriptionView.as_view(), name="subscription-cancel"),
]
