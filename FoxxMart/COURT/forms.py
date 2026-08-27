from django import forms
from django.utils import timezone

from .models import Booking, YogaClass


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('yoga_class', 'booking_date', 'name', 'email', 'phone', 'note')
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Anything Courtney should know?'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['yoga_class'].queryset = YogaClass.objects.filter(active=True)
        self.fields['booking_date'].widget.attrs['min'] = timezone.localdate().isoformat()
        for field in self.fields.values():
            field.widget.attrs['class'] = 'yoga-booking__input'

    def clean(self):
        cleaned_data = super().clean()
        yoga_class = cleaned_data.get('yoga_class')
        booking_date = cleaned_data.get('booking_date')

        if not yoga_class or not booking_date:
            return cleaned_data
        if booking_date < timezone.localdate():
            self.add_error('booking_date', 'Please choose a future class date.')
        elif booking_date.weekday() != yoga_class.weekday:
            self.add_error('booking_date', f'This class runs on {yoga_class.get_weekday_display()}s.')
        elif Booking.objects.filter(yoga_class=yoga_class, booking_date=booking_date).count() >= yoga_class.capacity:
            self.add_error('booking_date', 'This class is fully booked. Please choose another date.')
        return cleaned_data
