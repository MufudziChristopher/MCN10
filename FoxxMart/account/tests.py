from django.test import TestCase
from django.urls import reverse
from django.test.utils import override_settings
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from Axis.models import AxisCustomer, Order, OrderItem, Product
from Collective.models import CollectiveCustomer
from EXODUS.models import EXODUSCustomer, EXODUSOrder
from GENESIS.models import GENESISCustomer
from account.models import Account, StoreAccess
from account.models import Invoice
from account.invoices import create_invoice_for_order


class RegistrationViewTests(TestCase):
    def test_logout_returns_to_the_mall_front(self):
        response = self.client.get(reverse('account:logout'))

        self.assertRedirects(response, reverse('home:mall'))

    def test_registration_page_is_a_mall_wide_flow_without_cart_controls(self):
        response = self.client.get(f"{reverse('account:register')}?store=axis")

        self.assertContains(response, 'One account gives you access to every Foxx Mart storefront.')
        self.assertContains(response, 'Create your account')
        self.assertContains(response, 'Full name')
        self.assertNotContains(response, 'Quick Cart')
        self.assertNotContains(response, 'title="Cart"', html=False)
        self.assertNotContains(response, 'Phone Number')

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID='test-google-client-id',
        GOOGLE_OAUTH_CLIENT_SECRET='test-google-client-secret',
    )
    def test_registration_page_offers_google_sign_in(self):
        response = self.client.get(reverse('account:register'))

        self.assertContains(response, 'Continue with Google')
        self.assertContains(response, 'name="logo-google"', html=False)

    def test_successful_registration_returns_to_mall_and_creates_profiles(self):
        response = self.client.post(
            reverse('account:register'),
            {
                'email': 'registration-test@example.com',
                'full_name': 'Registration Test',
                'password1': 'SafeRegistrationPass123!',
                'password2': 'SafeRegistrationPass123!',
            },
        )

        self.assertRedirects(response, reverse('home:mall'))
        account = Account.objects.get(email='registration-test@example.com')
        self.assertTrue(AxisCustomer.objects.filter(user=account).exists())
        self.assertTrue(EXODUSCustomer.objects.filter(user=account).exists())
        self.assertTrue(GENESISCustomer.objects.filter(user=account).exists())
        self.assertTrue(CollectiveCustomer.objects.filter(user=account).exists())
        self.assertEqual(account.username, 'Registration Test')
        self.assertEqual(StoreAccess.objects.filter(user=account).count(), 4)

    def test_invalid_registration_shows_view_and_form_error_messages(self):
        response = self.client.post(
            reverse('account:register'),
            {
                'email': '',
                'full_name': '',
                'password1': '',
                'password2': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors below and try again.')
        self.assertContains(response, 'This field is required')

    def test_registration_rejects_an_email_already_used_by_google_regardless_of_case(self):
        Account.objects.create_user(
            email='google-user@example.com', username='Google User', password='SafePass123!'
        )

        response = self.client.post(
            reverse('account:register'),
            {
                'email': 'Google-User@Example.com',
                'full_name': 'Duplicate User',
                'password1': 'SafeRegistrationPass123!',
                'password2': 'SafeRegistrationPass123!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An account with this email address already exists.')
        self.assertEqual(Account.objects.filter(email__iexact='google-user@example.com').count(), 1)


class AccountProfileTests(TestCase):
    def test_storefronts_redirect_anonymous_shoppers_to_login(self):
        for url_name in ('Axis:store', 'EXODUS:store', 'GENESIS:store', 'Collective:store'):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertRedirects(
                    response,
                    f"{reverse('account:login')}?next={reverse(url_name)}",
                )

    def test_checkout_endpoints_reject_anonymous_shoppers(self):
        for url_name in (
            'Axis:checkout', 'Axis:complete_test_checkout', 'EXODUS:checkout',
            'EXODUS:process_order', 'GENESIS:checkout', 'GENESIS:process_order',
            'Collective:checkout', 'Collective:process_order',
        ):
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                response = self.client.post(url, data='{}', content_type='application/json')
                self.assertRedirects(response, f"{reverse('account:login')}?next={url}")

    def test_login_menu_omits_storefront_specific_links(self):
        response = self.client.get(reverse('account:login') + '?store=axis')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '>Shop<', html=False)
        self.assertNotContains(response, '>Contact<', html=False)
        self.assertNotContains(response, '>About<', html=False)
        self.assertNotContains(response, 'Quick Cart')
        self.assertNotContains(response, 'title="Cart"', html=False)
        self.assertContains(response, 'Sign in to Foxx Mart')
        self.assertContains(response, 'Forgot password?')

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID='test-google-client-id',
        GOOGLE_OAUTH_CLIENT_SECRET='test-google-client-secret',
    )
    def test_login_page_offers_google_sign_in_when_configured(self):
        response = self.client.get(reverse('account:login'))

        self.assertContains(response, 'Continue with Google')
        self.assertContains(response, reverse('google_login'))

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID='test-google-client-id',
        GOOGLE_OAUTH_CLIENT_SECRET='test-google-client-secret',
    )
    def test_google_login_starts_a_state_protected_authorization_request(self):
        response = self.client.get(reverse('google_login') + '?next=/mall/')

        self.assertRedirects(response, response.url, fetch_redirect_response=False)
        self.assertTrue(response.url.startswith('https://accounts.google.com/o/oauth2/v2/auth?'))
        self.assertIn('google_oauth_state', self.client.session)
        self.assertEqual(self.client.session['google_oauth_next'], '/mall/')

    def test_google_callback_rejects_a_missing_or_invalid_state(self):
        response = self.client.get(reverse('google_callback') + '?code=example&state=wrong')

        self.assertRedirects(response, reverse('account:login'))

    def test_change_password_page_uses_the_profile_shell(self):
        account = Account.objects.create_user(
            email='change-password@example.com', username='Change Password', password='SafePass123!'
        )
        self.client.force_login(account)

        response = self.client.get(reverse('password_change') + '?store=axis')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile security')
        self.assertContains(response, 'Quick Cart')
        self.assertContains(response, 'Update password')

    def test_password_reset_uses_the_account_menu_and_quick_cart(self):
        response = self.client.get(reverse('reset_password') + '?store=axis')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Forgot your password?')
        self.assertContains(response, 'Quick Cart')
        self.assertContains(response, 'Send reset link')

    def test_profile_creates_the_missing_axis_customer_for_a_legacy_account(self):
        account = Account.objects.create_user(
            email='legacy-account@example.com', username='Legacy Account', password='SafePass123!'
        )
        self.client.force_login(account)

        response = self.client.get(reverse('account:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(AxisCustomer.objects.filter(user=account).exists())
        self.assertContains(response, 'Profile')
        self.assertContains(response, 'Logout')
        self.assertContains(response, 'Logged in as: Legacy Account')
        self.assertNotContains(response, '>Register<', html=False)
        self.assertNotContains(response, '>Login<', html=False)

    def test_profile_menu_shows_the_pending_cart_count_for_its_store(self):
        account = Account.objects.create_user(
            email='profile-cart@example.com', username='Profile Cart', password='SafePass123!'
        )
        customer = AxisCustomer.objects.create(user=account, email=account.email)
        order = Order.objects.create(customer=customer, status='Pending')
        product = Product.objects.create(name='Profile cart product', price='10.00', stock=2)
        OrderItem.objects.create(order=order, product=product, quantity=2)
        self.client.force_login(account)

        response = self.client.get(reverse('account:profile') + '?store=axis')

        self.assertContains(response, 'name="cart-outline"', html=False)
        self.assertContains(response, '<b>2</b>', html=False)
        self.assertContains(response, 'Quick Cart')
        self.assertContains(response, 'Profile cart product')

    def test_edit_profile_saves_and_returns_to_the_same_storefront(self):
        account = Account.objects.create_user(
            email='edit-profile@example.com', username='Before Edit', password='SafePass123!'
        )
        self.client.force_login(account)

        response = self.client.post(
            reverse('account:edit') + '?store=axis',
            {'email': 'updated-profile@example.com', 'username': 'Updated Profile'},
        )

        self.assertRedirects(response, reverse('account:profile') + '?store=axis')
        account.refresh_from_db()
        self.assertEqual(account.email, 'updated-profile@example.com')
        self.assertEqual(account.username, 'Updated Profile')

    def test_quick_cart_remove_restores_stock_and_keeps_the_storefront(self):
        account = Account.objects.create_user(
            email='remove-profile-cart@example.com', username='Remove Cart', password='SafePass123!'
        )
        customer = AxisCustomer.objects.create(user=account, email=account.email)
        product = Product.objects.create(name='Removable profile item', price='12.00', stock=0)
        order = Order.objects.create(customer=customer, status='Pending')
        item = OrderItem.objects.create(order=order, product=product, quantity=2)
        self.client.force_login(account)

        response = self.client.post(
            reverse('account:remove_cart_item'), {'store': 'axis', 'item_id': item.id}
        )

        self.assertRedirects(response, reverse('account:profile') + '?store=axis')
        self.assertFalse(OrderItem.objects.filter(pk=item.id).exists())
        product.refresh_from_db()
        self.assertEqual(product.stock, 2)

    def test_profile_shows_only_orders_for_the_selected_storefront(self):
        account = Account.objects.create_user(
            email='store-profile@example.com', username='Store Profile', password='SafePass123!'
        )
        axis_customer = AxisCustomer.objects.create(user=account, email=account.email)
        EXODUSOrder.objects.create(customer=EXODUSCustomer.objects.create(user=account, email='exodus-store-profile@example.com'))
        axis_order = Order.objects.create(customer=axis_customer, transaction_id='AXIS-ONLY')
        self.client.force_login(account)

        response = self.client.get(reverse('account:profile') + '?store=exodus')

        self.assertContains(response, 'EXODUS Order History')
        self.assertNotContains(response, axis_order.transaction_id)

    def test_confirmed_order_invoice_appears_in_its_store_profile_and_downloads_as_pdf(self):
        account = Account.objects.create_user(
            email='invoice-profile@example.com', username='Invoice Profile', password='SafePass123!'
        )
        customer = AxisCustomer.objects.create(user=account, email=account.email)
        product = Product.objects.create(name='Invoice-ready product', price='125.00', stock=1)
        order = Order.objects.create(
            customer=customer,
            transaction_id='INVOICE-TEST-001',
            status='Payment Confirmed, Processing Order',
        )
        OrderItem.objects.create(order=order, product=product, quantity=2)
        invoice = create_invoice_for_order(user=account, store_slug='axis', order=order)
        self.client.force_login(account)

        response = self.client.get(reverse('account:profile') + '?store=axis')

        self.assertContains(response, 'View PDF')
        self.assertContains(response, reverse('account:invoice_download', args=[invoice.public_id]))
        pdf_response = self.client.get(reverse('account:invoice_view', args=[invoice.public_id]))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
        self.assertTrue(pdf_response.content.startswith(b'%PDF'))
        self.assertEqual(Invoice.objects.filter(user=account, store_slug='axis').count(), 1)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class CartLifecycleTests(TestCase):
    def setUp(self):
        self.account = Account.objects.create_user(email='cart@example.com', username='Cart User', password='SafePass123!')
        self.customer = AxisCustomer.objects.create(user=self.account, email=self.account.email)
        StoreAccess.objects.create(user=self.account, store_slug='axis', package=StoreAccess.Package.SINGLE)
        self.product = Product.objects.create(name='Cart test product', price='100.00', stock=2)

    def test_login_merges_guest_cart_and_clears_cookie(self):
        self.client.cookies['cart'] = '{"%s":{"quantity":2}}' % self.product.id
        response = self.client.post(reverse('account:login') + '?next=/3rdAxis/cart/', {'email': self.account.email, 'password': 'SafePass123!'})

        self.assertRedirects(response, reverse('home:mall'))
        item = OrderItem.objects.get(order__customer=self.customer, product=self.product)
        self.assertEqual(item.quantity, 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)
        self.assertEqual(response.cookies['cart'].value, '{}')

    def test_expiry_command_emails_and_clears_old_cart(self):
        order = Order.objects.create(customer=self.customer, status='Pending')
        OrderItem.objects.create(order=order, product=self.product, quantity=1)
        Product.objects.filter(pk=self.product.pk).update(stock=1)
        Order.objects.filter(pk=order.pk).update(date_ordered=timezone.now() - timedelta(hours=3))

        call_command('expire_abandoned_carts')

        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(OrderItem.objects.filter(order=order).exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)


class RegionalPricingTests(TestCase):
    @patch('account.views.reverse_geocode_country', return_value='ZA')
    def test_region_endpoint_sets_country_from_geolocation(self, reverse_geocode):
        response = self.client.post(
            reverse('account:set_region'),
            data='{"latitude": -26.2041, "longitude": 28.0473}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['country'], 'ZA')
        self.assertEqual(response.cookies['foxxmart_country'].value, 'ZA')
        reverse_geocode.assert_called_once_with(-26.2041, 28.0473)

    def test_region_endpoint_rejects_invalid_coordinates(self):
        response = self.client.post(
            reverse('account:set_region'),
            data='{"latitude": 91, "longitude": 28}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

# Create your tests here.
