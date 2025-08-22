from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Reservation, Table

# 🔐 User registration form (for internal staff only)
class StaffUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


# 📅 Reservation form with overlap validation
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['table', 'name', 'start_time', 'status']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get('table')
        start_time = cleaned_data.get('start_time')

        if not table or not start_time:
            return cleaned_data  # Let field-level validation handle this

        # Auto-calculate end_time based on fixed duration
        end_time = start_time + timedelta(hours=1)

        conflict = Reservation.objects.filter(
            table=table,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if self.instance.pk:
            conflict = conflict.exclude(pk=self.instance.pk)

        if conflict.exists():
            raise forms.ValidationError(
                "⚠️ This table is already reserved at that time."
            )

        return cleaned_data


# 🪑 Table creation form
class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number', 'capacity']

    def clean_table_number(self):
        table_number = self.cleaned_data.get('table_number')
        user = self.initial.get('user')

        # Check if this user already has this table number
        if Table.objects.filter(user=user, table_number=table_number).exists():
            raise ValidationError(f"Table number {table_number} is already in use.")

        return table_number