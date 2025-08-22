from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class Table(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table_number = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'table_number') # deberia solucionar el temita de duplicados

    def __str__(self):
        return f"Table {self.table_number} (Capacity: {self.capacity})"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Table {self.table.table_number} - {self.name} - {self.start_time} to {self.end_time}"

    def auto_delete_if_expired(self):
        """Deletes the reservation if it's expired by more than 1 hour."""
        if timezone.now() > self.end_time + timedelta(hours=1):
            self.delete()
