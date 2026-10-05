from datetime import timedelta
from django.utils import timezone

from .models import Reservation, Notification


def create_reservation_reminders():

    tomorrow = timezone.localdate() + timedelta(days=1)

    reservations = Reservation.objects.filter(
        reservation_date=tomorrow,
        status__in=["pending", "confirmed"]
    )

    for reservation in reservations:

        phone = reservation.user.profile.phone

        message = (
            f"DineEase Reminder: Your reservation at "
            f"{reservation.restaurant.name} is tomorrow at "
            f"{reservation.reservation_time}. "
            f"Guests: {reservation.guests}."
        )

        print("Phone:", phone)
        print("Message:", message)

        Notification.objects.get_or_create(
            user=reservation.user,
            message=message
        )