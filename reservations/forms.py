from django import forms
from .models import Reservation
from restaurants.models import Table
from datetime import datetime
from django.utils import timezone


class ReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["table"].queryset = Table.objects.none()
        

        if "restaurant" in self.data:
            try:
                restaurant_id = int(self.data.get("restaurant"))
                self.fields["table"].queryset = Table.objects.filter(
                    restaurant_id=restaurant_id,
                    is_available=True
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk:
            self.fields["table"].queryset = Table.objects.filter(
                restaurant=self.instance.restaurant
            )

    class Meta:
        model = Reservation
        fields = [
            "restaurant",
            "table",
            "reservation_date",
            "reservation_time",
            "guests",
        ]
   
    def clean(self):
        cleaned_data = super().clean()

        restaurant = cleaned_data.get("restaurant")
        table = cleaned_data.get("table")
        guests = cleaned_data.get("guests")
        reservation_date = cleaned_data.get("reservation_date")
        reservation_time = cleaned_data.get("reservation_time")

        # Check whether the selected table belongs to the selected restaurant
        if restaurant and table:
            if table.restaurant != restaurant:
                raise forms.ValidationError(
                    "Please select a table from the selected restaurant."
                )

        # Check table availability
        if table and not table.is_available:
            raise forms.ValidationError(
                "This table is currently unavailable."
            )

        # Check table capacity
        if table and guests:
            if guests > table.capacity:
                raise forms.ValidationError(
                    f"This table can accommodate only {table.capacity} guests."
                )

        # Check restaurant opening hours
        if restaurant and reservation_time:

            opening_time = restaurant.opening_time
            closing_time = restaurant.closing_time

        # Normal hours, for example 09:00 AM - 10:00 PM
        if opening_time <= closing_time:

            if not (
                opening_time
                <= reservation_time
                <= closing_time
            ):
                raise forms.ValidationError(
                    f"Restaurant is open from "
                    f"{opening_time} to "
                    f"{closing_time}."
                )

        # Overnight hours, for example 11:00 AM - 02:00 AM
        else:

            if not (
                reservation_time >= opening_time
                or reservation_time <= closing_time
            ):
                raise forms.ValidationError(
                    f"Restaurant is open from "
                    f"{opening_time} to "
                    f"{closing_time}."
                )