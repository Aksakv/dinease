
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    View,
    DetailView,
)

from .models import Reservation, Notification
from .forms import ReservationForm
from restaurants.models import Table


# -----------------------------
# Create Reservation
# -----------------------------
class ReservationCreateView(LoginRequiredMixin, CreateView):

    model = Reservation
    form_class = ReservationForm
    template_name = "reservations/reservation_form.html"

    def get_initial(self):
        initial = super().get_initial()

        restaurant_id = self.request.GET.get("restaurant")

        if restaurant_id:
            initial["restaurant"] = restaurant_id

        return initial

    def form_valid(self, form):

        # Assign logged-in user
        form.instance.user = self.request.user

        return super().form_valid(form)

    def get_success_url(self):

        return reverse_lazy(
            "reservations:reservation-confirmation",
            kwargs={
                "pk": self.object.pk
            }
        )

    def form_invalid(self, form):

        print("FORM ERRORS:", form.errors)
        print("NON FIELD ERRORS:", form.non_field_errors())

        return super().form_invalid(form)


# -----------------------------
# Reservation List
# -----------------------------
class ReservationListView(LoginRequiredMixin, ListView):

    model = Reservation
    template_name = "reservations/reservation_list.html"
    context_object_name = "reservations"

    def get_queryset(self):

        return Reservation.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


# -----------------------------
# Reservation Confirmation
# -----------------------------
class ReservationConfirmationView(
    LoginRequiredMixin,
    DetailView
):

    model = Reservation
    template_name = "reservations/reservation_confirmation.html"
    context_object_name = "reservation"

    def get_queryset(self):

        return Reservation.objects.filter(
            user=self.request.user
        )


# -----------------------------
# Cancel Reservation
# -----------------------------
class CancelReservationView(
    LoginRequiredMixin,
    View
):

    def post(self, request, pk):

        reservation = Reservation.objects.get(
            pk=pk,
            user=request.user
        )

        reservation.status = "cancelled"
        reservation.save()

        return redirect(
            "reservations:reservation-list"
        )


# -----------------------------
# Available Tables
# -----------------------------
class TableListView(
    LoginRequiredMixin,
    View
):

    def get(self, request):

        restaurant_id = request.GET.get(
            "restaurant_id"
        )

        tables = Table.objects.filter(
            restaurant_id=restaurant_id,
            is_available=True
        )

        data = []

        for table in tables:

            data.append({
                "id": table.id,
                "table_number": table.table_number,
                "capacity": table.capacity,
            })

        return JsonResponse(
            data,
            safe=False
        )


# -----------------------------
# Notification List
# -----------------------------
class NotificationListView(
    LoginRequiredMixin,
    ListView
):

    model = Notification
    template_name = "reservations/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):

        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

