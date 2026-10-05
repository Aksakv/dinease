from django.db import models
from django.contrib.auth.models import User
from restaurants.models import Restaurant, Table
# Create your models here.


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
    Restaurant,
    on_delete=models.CASCADE)
    table = models.ForeignKey(
    Table,
    on_delete=models.CASCADE
)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    guests = models.PositiveIntegerField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Reservation by {self.user.username} at {self.restaurant.name} on {self.reservation_date} at {self.reservation_time}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username