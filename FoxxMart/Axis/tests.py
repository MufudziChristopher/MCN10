import json

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from account.models import Account, StoreAccess
from .models import AxisCustomer, Order, Product


class AxisApiTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='API Test Arm',
            short_desc='A test product',
            price='1200.00',
            stock=3,
        )
        self.account = Account.objects.create_user(
            email='axis-api@example.com', username='Axis API', password='SafePassword123!'
        )
        AxisCustomer.objects.create(user=self.account, email=self.account.email)
        StoreAccess.objects.create(user=self.account, store_slug='axis', package=StoreAccess.Package.SINGLE)

    def test_catalog_is_public_and_serializes_products(self):
        response = self.client.get(reverse('Axis:api_products'))

        self.assertEqual(response.status_code, 200)
        product = response.json()['products'][0]
        self.assertEqual(product['id'], self.product.id)
        self.assertEqual(product['price'], '1200.00')
        self.assertEqual(product['stock'], 3)

    def test_authenticated_cart_mutations_use_api_and_preserve_stock(self):
        self.client.force_login(self.account)
        url = reverse('Axis:api_cart_items')

        add_response = self.client.post(url, data=json.dumps({'productId': self.product.id, 'action': 'add'}), content_type='application/json')
        self.assertEqual(add_response.status_code, 200)
        self.assertEqual(add_response.json()['quantity'], 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        set_response = self.client.post(url, data=json.dumps({'productId': self.product.id, 'action': 'set', 'quantity': 2}), content_type='application/json')
        self.assertEqual(set_response.status_code, 200)
        self.assertEqual(set_response.json()['cart']['item_count'], 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

        cancel_response = self.client.post(url, data=json.dumps({'productId': self.product.id, 'action': 'cancel'}), content_type='application/json')
        self.assertEqual(cancel_response.status_code, 200)
        self.assertEqual(cancel_response.json()['cart']['item_count'], 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertFalse(Order.objects.get(customer=self.account.axiscustomer, status='Pending').orderitem_set.exists())

    def test_test_payment_creates_order_history_and_invoice(self):
        self.client.force_login(self.account)
        order = Order.objects.create(customer=self.account.axiscustomer, status='Pending')
        from .models import OrderItem
        OrderItem.objects.create(order=order, product=self.product, quantity=1)
        response = self.client.post(reverse('Axis:complete_test_checkout'), {
            'country': 'ZA', 'address1': '1 Test Street', 'address2': '', 'suburb': 'Test', 'city': 'Cape Town', 'province': 'WC', 'postal_code': '8001',
        })

        self.assertRedirects(response, reverse('Axis:invoice', args=[order.id]))
        order.refresh_from_db()
        self.assertEqual(order.status, 'Payment Confirmed, Processing Order')
        self.assertTrue(order.transaction_id)
        self.assertContains(self.client.get(reverse('Axis:invoice', args=[order.id])), 'Test Invoice')

    def test_checkout_does_not_include_a_browser_payment_flow(self):
        self.client.force_login(self.account)
        response = self.client.get(reverse('Axis:checkout'))

        self.assertContains(response, reverse('Axis:complete_test_checkout'))
        self.assertNotContains(response, 'paypal.com')
        self.assertNotContains(response, 'paypal.Buttons')
        self.assertNotContains(response, 'fetch(url')


class AxisComponentSeedTests(TestCase):
    def test_component_seed_is_idempotent_and_creates_shared_filter_groups(self):
        call_command('seed_axis_components')
        call_command('seed_axis_components')

        self.assertEqual(Product.objects.filter(name__startswith='Axis ').count(), 20)
        self.assertEqual(Product.objects.filter(tags__name='Filament').count(), 10)
        self.assertEqual(Product.objects.filter(tags__name='Microboard').count(), 5)
        self.assertEqual(Product.objects.filter(tags__name='Extruder').count(), 5)
