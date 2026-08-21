from django.test import TestCase
from django.urls import reverse

from Axis.models import AxisCustomer
from Collective.models import CollectiveCustomer
from EXODUS.models import EXODUSCustomer
from GENESIS.models import GENESISCustomer
from account.models import Account


class RegistrationViewTests(TestCase):
    def test_registration_page_links_back_to_the_originating_storefront(self):
        response = self.client.get(f"{reverse('account:register')}?store=axis")

        self.assertContains(response, '3rd Axis Storefront')
        self.assertContains(response, reverse('Axis:store'))
        self.assertContains(response, 'name="store" value="axis"', html=False)

    def test_successful_registration_returns_to_storefront_and_creates_profiles(self):
        response = self.client.post(
            f"{reverse('account:register')}?store=exodus",
            {
                'email': 'registration-test@example.com',
                'username': 'Registration Test',
                'phone': '0123456789',
                'password1': 'SafeRegistrationPass123!',
                'password2': 'SafeRegistrationPass123!',
                'store': 'exodus',
            },
        )

        self.assertRedirects(response, reverse('EXODUS:store'))
        account = Account.objects.get(email='registration-test@example.com')
        self.assertTrue(AxisCustomer.objects.filter(user=account).exists())
        self.assertTrue(EXODUSCustomer.objects.filter(user=account).exists())
        self.assertTrue(GENESISCustomer.objects.filter(user=account).exists())
        self.assertTrue(CollectiveCustomer.objects.filter(user=account).exists())

    def test_invalid_registration_shows_view_and_form_error_messages(self):
        response = self.client.post(
            f"{reverse('account:register')}?store=axis",
            {
                'email': '',
                'username': '',
                'phone': '',
                'password1': '',
                'password2': '',
                'store': 'axis',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors below and try again.')
        self.assertContains(response, 'This field is required')

# Create your tests here.
