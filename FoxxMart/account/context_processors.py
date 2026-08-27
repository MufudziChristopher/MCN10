from .customer_profiles import get_store_customer
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

    return {
        'account_storefront': storefront,
        # Authentication views also use menu_base. Supply the same quick cart
        # there, rather than limiting it to the custom profile views.
        'account_show_quick_cart': True,
        'account_quick_cart_items': items,
        'account_cart_items': sum(item.quantity or 0 for item in items),
        'account_cart_total': sum((item.get_total for item in items), 0),
    }
