from django.test import TestCase
from django.urls import reverse
from account.models import Account
from Axis.models import AxisCustomer, Order, OrderItem, Product


class MallFrontTests(TestCase):
    def test_mall_front_does_not_show_a_personal_welcome(self):
        shopper = Account.objects.create_user(
            email='mall-shopper@example.com', username='Mall Shopper', password='SafePass123!'
        )
        shopper.first_name = 'Mall'
        shopper.save(update_fields=['first_name'])
        self.client.force_login(shopper)

        response = self.client.get(reverse('home:mall'))

        self.assertNotContains(response, 'Welcome, Mall!')

    def test_portfolio_navigation_exposes_mall_after_home(self):
        response = self.client.get(reverse('home:home'))

        self.assertContains(response, 'data-external-page href="/mall/"', html=False)
        content = response.content.decode()
        self.assertLess(content.index('href="#page-home"'), content.index('data-external-page href="/mall/"'))

    def test_mall_front_lists_each_current_store(self):
        response = self.client.get(reverse('home:mall'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3rd Axis')
        self.assertContains(response, 'The Collective')
        self.assertContains(response, 'Genesis')
        self.assertContains(response, 'Exodus')
        self.assertContains(response, 'Bomkazi Designs')
        self.assertContains(response, reverse('Axis:store'))
        self.assertContains(response, reverse('Collective:store'))
        self.assertContains(response, reverse('GENESIS:store'))
        self.assertContains(response, reverse('EXODUS:store'))
        self.assertContains(response, reverse('Projects:bomkazi'))

    def test_bomkazi_boutique_is_available_from_the_mall(self):
        response = self.client.get(reverse('Projects:bomkazi'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bomkazi Designs')

    def test_mall_only_shows_a_store_badge_when_that_store_has_cart_items(self):
        shopper = Account.objects.create_user(
            email='mall-cart@example.com', username='Mall Cart', password='SafePass123!'
        )
        customer = AxisCustomer.objects.create(user=shopper, email=shopper.email)
        product = Product.objects.create(name='Mall badge product', short_desc='Test', price='100.00', stock=2)
        order = Order.objects.create(customer=customer, status='Pending')
        OrderItem.objects.create(order=order, product=product, quantity=2)
        self.client.force_login(shopper)

        response = self.client.get(reverse('home:mall'))

        self.assertContains(response, 'mall-card__cart-count', count=2)
        self.assertContains(response, '>2</span>', html=False)
