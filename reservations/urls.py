from django.urls import path
from .views import CancelReservationView

from .views import (
    ReservationCreateView,
    ReservationListView,
    CancelReservationView,
    TableListView,ReservationConfirmationView,NotificationListView
)
app_name = "reservations"
urlpatterns = [
    path("", ReservationListView.as_view(), name="reservation-list"),
    path("create/", ReservationCreateView.as_view(), name="reservation-create"),
    path(
        "<int:pk>/cancel/",
        CancelReservationView.as_view(),
        name="reservation-cancel",
    ),
    path("tables/", TableListView.as_view(), name="table-list"),
    path(
    "<int:pk>/confirmation/",
    ReservationConfirmationView.as_view(),
    name="reservation-confirmation",
),
    path(
    "notifications/",
    NotificationListView.as_view(),
    name="notification-list"
),
]