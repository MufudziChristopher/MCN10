import json
from decimal import Decimal, ROUND_HALF_UP
from urllib.request import urlopen

from django.core.cache import cache
from django import template


register = template.Library()

COUNTRY_CURRENCIES = {
    'AU': 'AUD', 'CA': 'CAD', 'CH': 'CHF', 'CN': 'CNY', 'DE': 'EUR',
    'ES': 'EUR', 'FR': 'EUR', 'GB': 'GBP', 'IN': 'INR', 'JP': 'JPY',
    'KE': 'KES', 'MX': 'MXN', 'NG': 'NGN', 'NZ': 'NZD', 'US': 'USD',
    'ZA': 'ZAR',
}
SYMBOLS = {
    'AUD': 'A$', 'CAD': 'CA$', 'CHF': 'CHF', 'CNY': 'CN¥', 'EUR': '€',
    'GBP': '£', 'INR': '₹', 'JPY': '¥', 'KES': 'KSh', 'MXN': 'MX$',
    'NGN': '₦', 'NZD': 'NZ$', 'USD': 'US$', 'ZAR': 'R',
}


def _currency_for_request(request):
    # Currency is selected only from an explicitly consented, geolocated country.
    # A visitor who does not share location sees the storefront's ZAR base price.
    country = request.COOKIES.get('foxxmart_country', '').upper()
    return COUNTRY_CURRENCIES.get(country, 'ZAR')


def _rates():
    rates = cache.get('axis_zar_exchange_rates_v2')
    if rates:
        return rates
    try:
        with urlopen('https://open.er-api.com/v6/latest/ZAR', timeout=1.5) as response:
            payload = json.load(response)
        rates = payload.get('rates', {}) if payload.get('result') == 'success' else {}
    except (OSError, ValueError, json.JSONDecodeError):
        rates = {}
    rates['ZAR'] = 1
    # Do not cache a transient offline failure for as long as valid exchange data.
    cache.set('axis_zar_exchange_rates_v2', rates, 60 * 60 * 12 if len(rates) > 1 else 10 * 60)
    return rates


@register.simple_tag(takes_context=True)
def local_price(context, amount):
    """Display the server-held ZAR amount in the visitor's regional currency."""
    request = context['request']
    currency = _currency_for_request(request)
    rates = _rates()
    # Never label an unconverted ZAR price as another currency.
    if currency not in rates:
        currency = 'ZAR'
    rate = Decimal(str(rates[currency]))
    value = (Decimal(amount) * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"{SYMBOLS.get(currency, currency + ' ')}{value:,.2f}"
