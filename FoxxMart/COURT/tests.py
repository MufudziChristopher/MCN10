from django.test import TestCase

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from .models import Booking, YogaClass


class BookingFlowTests(TestCase):
    def setUp(self):
        self.yoga_class = YogaClass.objects.get(name='Sunset Flow')

    def _next_session_date(self):
        today = timezone.localdate()
        return today + timedelta(days=(self.yoga_class.weekday - today.weekday()) % 7 or 7)

    def test_landing_page_lists_seeded_classes_and_booking_form(self):
        response = self.client.get(reverse('COURT:store'))

        self.assertContains(response, 'Reserve your place')
        self.assertContains(response, 'Sunset Flow')
        self.assertContains(response, 'Confirm booking')

    def test_valid_booking_is_saved(self):
        response = self.client.post(reverse('COURT:store'), {
            'yoga_class': self.yoga_class.pk,
            'booking_date': self._next_session_date().isoformat(),
            'name': 'Test Student',
            'email': 'student@example.com',
            'phone': '0123456789',
            'note': '',
        })

        self.assertRedirects(response, reverse('COURT:store'))
        self.assertTrue(Booking.objects.filter(email='student@example.com').exists())

# Create your tests here.
