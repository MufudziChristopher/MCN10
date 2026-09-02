from .customer_profiles import get_store_customer
from .models import Notification
from .notifications import sync_customer_notifications
from .storefronts import get_profile_storefront


def account_storefront(request):
    """Provide account templates with a consistent storefront-specific menu."""
    storefront = get_profile_storefront(request)
    items = []
    if request.user.is_authenticated:
        customer = get_store_customer(request.user, storefront['customer_model'])
        orders = getattr(customer, storefront['orders_accessor']).filter(status='Pending')
        for order in orders:
            items.extend(
                getattr(order, storefront['order_items_accessor'])
                .select_related('product')
                .filter(product__isnull=False)
            )
        # Keep menu alerts current without requiring a background worker during
        # local development. Production can run this same helper in a task.
        sync_customer_notifications(request.user)

    is_auth_page = (
        request.resolver_match
        and request.resolver_match.namespace == 'account'
        and request.resolver_match.url_name in {'login', 'register'}
    )
    return {
        'account_storefront': storefront,
        # Login and registration stay focused on authentication.
        'account_show_quick_cart': not is_auth_page,
        'account_is_auth_page': is_auth_page,
        'account_quick_cart_items': items,
        'account_cart_items': sum(item.quantity or 0 for item in items),
        'account_cart_total': sum((item.get_total for item in items), 0),
        'notification_count': Notification.objects.filter(user=request.user, read_at__isnull=True).count() if request.user.is_authenticated else 0,
    }
