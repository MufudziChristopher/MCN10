"""Small, store-aware notification helpers used by menus and operations."""

from django.urls import reverse

from .customer_profiles import get_store_customer
from .models import Notification
from .storefronts import STOREFRONTS

LOW_STOCK_THRESHOLD = 5


def _upsert_notification(*, user, store_slug, kind, event_key, title, body, url):
    """Create an event once; a changed status gets its own event key."""
    return Notification.objects.get_or_create(
        user=user,
        store_slug=store_slug,
        event_key=event_key,
        defaults={'kind': kind, 'title': title, 'body': body, 'url': url},
    )[0]


def notify_order_status(*, user, storefront, order):
    if not user or not order.status or order.status == 'Pending':
        return None
    label = getattr(order, 'get_status_display', lambda: order.status)()
    destination = f"{reverse('account:profile')}?store={storefront['slug']}"
    return _upsert_notification(
        user=user,
        store_slug=storefront['slug'],
        kind=Notification.Kind.ORDER_STATUS,
        event_key=f'order:{order.pk}:status:{order.status}',
        title='Order update',
        body=f'Your order is now {label.lower()}.',
        url=destination,
    )


def sync_customer_notifications(user, store_slug=None):
    """Surface order progress and at-risk cart items for the signed-in user."""
    if not user or not user.is_authenticated:
        return
    storefronts = [STOREFRONTS[store_slug]] if store_slug in STOREFRONTS else STOREFRONTS.values()
    for storefront in storefronts:
        customer = get_store_customer(user, storefront['customer_model'])
        destination = f"{reverse('account:profile')}?store={storefront['slug']}"
        orders = getattr(customer, storefront['orders_accessor']).all()
        for order in orders.exclude(status='Pending'):
            notify_order_status(user=user, storefront=storefront, order=order)
        for order in orders.filter(status='Pending'):
            items = getattr(order, storefront['order_items_accessor']).select_related('product').filter(product__isnull=False)
            for item in items:
                stock = item.product.stock
                if stock is not None and stock <= LOW_STOCK_THRESHOLD:
                    remaining = max(stock, 0)
                    _upsert_notification(
                        user=user,
                        store_slug=storefront['slug'],
                        kind=Notification.Kind.LOW_STOCK,
                        event_key=f'cart:{order.pk}:product:{item.product_id}:stock:{remaining}',
                        title='Low stock in your cart',
                        body=f'{item.product.name} has only {remaining} left in stock.',
                        url=storefront['cart_url_name'] and reverse(storefront['cart_url_name']),
                    )
