"""Storefront metadata shared by registration, account pages and navigation."""

from Axis.models import AxisCustomer, OrderItem
from EXODUS.models import EXODUSCustomer, EXODUSOrderItem
from GENESIS.models import GENESISCustomer, GENESISOrderItem
from Collective.models import CollectiveCustomer, CollectiveOrderItem


STOREFRONTS = {
    'axis': {'slug': 'axis', 'name': '3rd Axis Storefront', 'menu_label': '3rd Axis', 'url_name': 'Axis:store', 'store_url_name': 'Axis:store', 'cart_url_name': 'Axis:cart', 'checkout_url_name': 'Axis:checkout', 'contact_url_name': 'Axis:contact', 'about_url_name': 'Axis:about', 'customer_model': AxisCustomer, 'order_item_model': OrderItem, 'orders_accessor': 'order_set', 'order_items_accessor': 'orderitem_set'},
    'exodus': {'slug': 'exodus', 'name': 'EXODUS Storefront', 'menu_label': 'EXODUS', 'url_name': 'EXODUS:store', 'store_url_name': 'EXODUS:store', 'cart_url_name': 'EXODUS:cart', 'checkout_url_name': 'EXODUS:checkout', 'contact_url_name': 'EXODUS:contact', 'about_url_name': 'EXODUS:about', 'customer_model': EXODUSCustomer, 'order_item_model': EXODUSOrderItem, 'orders_accessor': 'exodusorder_set', 'order_items_accessor': 'exodusorderitem_set'},
    'genesis': {'slug': 'genesis', 'name': 'GENESIS Storefront', 'menu_label': 'GENESIS', 'url_name': 'GENESIS:store', 'store_url_name': 'GENESIS:store', 'cart_url_name': 'GENESIS:cart', 'checkout_url_name': 'GENESIS:checkout', 'contact_url_name': 'GENESIS:contact', 'about_url_name': 'GENESIS:about', 'customer_model': GENESISCustomer, 'order_item_model': GENESISOrderItem, 'orders_accessor': 'genesisorder_set', 'order_items_accessor': 'genesisorderitem_set'},
    'collective': {'slug': 'collective', 'name': 'The Collective Storefront', 'menu_label': 'The Collective', 'url_name': 'Collective:store', 'store_url_name': 'Collective:store', 'cart_url_name': 'Collective:cart', 'checkout_url_name': 'Collective:checkout', 'contact_url_name': 'Collective:contact', 'about_url_name': 'Collective:about', 'customer_model': CollectiveCustomer, 'order_item_model': CollectiveOrderItem, 'orders_accessor': 'collectiveorder_set', 'order_items_accessor': 'collectiveorderitem_set'},
}


def get_profile_storefront(request):
    """Resolve the storefront carried in the account URL, defaulting to 3rd Axis."""
    return STOREFRONTS.get(request.GET.get('store'), STOREFRONTS['axis'])
