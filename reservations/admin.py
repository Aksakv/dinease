from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "restaurant",
        "table",
        "reservation_date",
        "reservation_time",
        "guests",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "restaurant",
        "reservation_date",
    )

    search_fields = (
        "user__username",
        "restaurant__name",
    )