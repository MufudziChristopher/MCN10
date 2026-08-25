import json

from django.db import transaction


STORE_CARTS = {
    'axis': ('Axis.models', 'Product', 'AxisCustomer', 'Order', 'OrderItem', ''),
    'collective': ('Collective.models', 'CollectiveProduct', 'CollectiveCustomer', 'CollectiveOrder', 'CollectiveOrderItem', 'size'),
    'genesis': ('GENESIS.models', 'GENESISProduct', 'GENESISCustomer', 'GENESISOrder', 'GENESISOrderItem', ''),
    'exodus': ('EXODUS.models', 'EXODUSProduct', 'EXODUSCustomer', 'EXODUSOrder', 'EXODUSOrderItem', ''),
}


def storefront_from_request(request):
    store = request.POST.get('store') or request.GET.get('store')
    if store in STORE_CARTS:
        return store
    next_url = request.POST.get('next') or request.GET.get('next') or ''
    for slug, prefix in {'axis': '/3rdAxis/', 'collective': '/TheCollective/', 'genesis': '/GENESIS/', 'exodus': '/EXODUS/'}.items():
        if next_url.startswith(prefix):
            return slug
    return None


def merge_guest_cart(request, user, store_slug):
    if store_slug not in STORE_CARTS:
        return False
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except (TypeError, json.JSONDecodeError):
        return False
    if not cart:
        return False

    module_name, product_name, customer_name, order_name, item_name, variant_field = STORE_CARTS[store_slug]
    module = __import__(module_name, fromlist=[product_name, customer_name, order_name, item_name])
    Product, Customer, Order, OrderItem = (getattr(module, name) for name in (product_name, customer_name, order_name, item_name))
    merged = False
    with transaction.atomic():
        customer, _ = Customer.objects.get_or_create(user=user, defaults={'email': user.email})
        order, _ = Order.objects.get_or_create(customer=customer, status='Pending')
        for product_id, entry in cart.items():
            try:
                requested = max(0, int(entry.get('quantity', 0)))
                product = Product.objects.select_for_update().get(pk=product_id)
            except (TypeError, ValueError, Product.DoesNotExist):
                continue
            if not requested:
                continue
            filters = {'order': order, 'product': product}
            if variant_field:
                filters[variant_field] = (entry.get(variant_field) or '').upper()
            item, _ = OrderItem.objects.get_or_create(**filters)
            quantity = min(requested, product.stock)
            if quantity:
                item.quantity += quantity
                item.save()
                product.stock -= quantity
                product.save(update_fields=['stock'])
                merged = True
        if merged:
            order.save()
    return merged


def clear_guest_cart(response):
    response.set_cookie('cart', '{}', path='/')
    return response
