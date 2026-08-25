"""Versioned HTTP API for the 3rd Axis storefront.

The storefront can consume this contract directly while Django models remain an
implementation detail behind the API boundary.
"""
import json
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from account.access import store_access_required

from .models import Order, OrderItem, Product


def _product_payload(request, product):
    return {
        'id': product.id,
        'name': product.name,
        'short_description': product.short_desc or '',
        'description': product.description1 or '',
        'price': f'{product.price:.2f}',
        'stock': product.stock,
        'image_url': request.build_absolute_uri(product.imageURL1) if product.imageURL1 else '',
        'tags': list(product.tags.values_list('name', flat=True)),
    }


def _cart_payload(request, order):
    items = order.orderitem_set.select_related('product').filter(product__isnull=False)
    return {
        'items': [
            {
                'product': _product_payload(request, item.product),
                'quantity': item.quantity,
                'line_total': f'{item.get_total:.2f}',
            }
            for item in items
        ],
        'item_count': order.get_cart_items,
        'total': f'{order.get_cart_total:.2f}',
        'currency': 'ZAR',
    }


@require_GET
def products(request):
    return JsonResponse({'products': [_product_payload(request, product) for product in Product.objects.all()]})


@require_GET
def product_detail(request, product_id):
    return JsonResponse({'product': _product_payload(request, get_object_or_404(Product, pk=product_id))})


@require_GET
@store_access_required('axis')
def cart(request):
    order, _ = Order.objects.get_or_create(customer=request.user.axiscustomer, status='Pending')
    return JsonResponse(_cart_payload(request, order))


@require_POST
@store_access_required('axis')
def cart_items(request):
    try:
        payload = json.loads(request.body or '{}')
        product_id = int(payload['productId'])
        action = payload['action']
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return JsonResponse({'error': 'productId and action are required.'}, status=400)

    if action not in {'add', 'remove', 'cancel', 'set'}:
        return JsonResponse({'error': 'Unsupported cart action.'}, status=400)

    with transaction.atomic():
        product = get_object_or_404(Product.objects.select_for_update(), pk=product_id)
        order, _ = Order.objects.get_or_create(customer=request.user.axiscustomer, status='Pending')
        order_item, _ = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            if product.stock < 1:
                return JsonResponse({'error': 'This item is out of stock.'}, status=409)
            product.stock -= 1
            order_item.quantity += 1
        elif action == 'remove':
            if order_item.quantity > 0:
                product.stock += 1
                order_item.quantity -= 1
        elif action == 'cancel':
            product.stock += order_item.quantity
            order_item.quantity = 0
        else:
            try:
                requested_quantity = max(0, int(payload.get('quantity', 0)))
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Quantity must be a whole number.'}, status=400)
            requested_quantity = min(requested_quantity, product.stock + order_item.quantity)
            product.stock += order_item.quantity - requested_quantity
            order_item.quantity = requested_quantity

        product.save(update_fields=['stock'])
        if order_item.quantity:
            order_item.save()
        else:
            order_item.delete()

    return JsonResponse({'cart': _cart_payload(request, order), 'quantity': order_item.quantity})
