import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from account.models import StoreAccess
from django.contrib import messages
from .cart_lifecycle import clear_guest_cart, merge_guest_cart, storefront_from_request
from .customer_profiles import get_store_customer
from .storefronts import STOREFRONTS, get_profile_storefront


def reverse_geocode_country(latitude, longitude):
	"""Resolve a consented browser position to an ISO country code server-side."""
	query = urlencode({
		'format': 'jsonv2',
		'lat': f'{latitude:.6f}',
		'lon': f'{longitude:.6f}',
		'zoom': '3',
		'addressdetails': '1',
	})
	request = Request(
		f'https://nominatim.openstreetmap.org/reverse?{query}',
		headers={'User-Agent': 'FoxxMart regional-currency lookup'},
	)
	with urlopen(request, timeout=2) as response:
		payload = json.load(response)
	country = payload.get('address', {}).get('country_code', '').upper()
	return country if len(country) == 2 and country.isalpha() else None


@require_POST
def set_region(request):
	"""Store a location-derived country preference used only for price display."""
	try:
		payload = json.loads(request.body or '{}')
		latitude = float(payload['latitude'])
		longitude = float(payload['longitude'])
	except (KeyError, TypeError, ValueError, json.JSONDecodeError):
		return JsonResponse({'detail': 'Valid coordinates are required.'}, status=400)

	if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
		return JsonResponse({'detail': 'Coordinates are outside the valid range.'}, status=400)

	try:
		country = reverse_geocode_country(latitude, longitude)
	except (OSError, ValueError, json.JSONDecodeError):
		country = None
	if not country:
		return JsonResponse({'detail': 'Location could not be resolved.'}, status=503)

	response = JsonResponse({'country': country})
	response.set_cookie(
		'foxxmart_country', country, max_age=60 * 60 * 24 * 365,
		secure=not settings.DEBUG, samesite='Lax',
	)
	return response


def get_storefront(request):
	store_slug = request.POST.get('store') or request.GET.get('store')
	return STOREFRONTS.get(store_slug)


def get_account_cart_context(orders, storefront):
	"""Build a small storefront-specific cart summary for account pages."""
	items = []
	for order in orders.filter(status='Pending'):
		items.extend(
			getattr(order, storefront['order_items_accessor']).select_related('product').filter(product__isnull=False)
		)
	return {
		'account_cart_items': sum(item.quantity or 0 for item in items),
		'account_quick_cart_items': items,
		'account_cart_total': sum((item.get_total for item in items), 0),
		'account_show_quick_cart': True,
	}


@require_POST
def remove_cart_item(request):
	"""Remove one pending-cart line item owned by the signed-in shopper."""
	if not request.user.is_authenticated:
		return redirect('account:login')

	storefront = STOREFRONTS.get(request.POST.get('store'))
	if not storefront:
		return redirect('account:profile')
	customer = get_store_customer(request.user, storefront['customer_model'])
	item = get_object_or_404(
		storefront['order_item_model'].objects.select_related('order', 'product'),
		pk=request.POST.get('item_id'),
	)
	if item.order.customer_id != customer.id or item.order.status != 'Pending':
		messages.error(request, 'That cart item is no longer available.')
	else:
		if item.product_id:
			item.product.stock += item.quantity or 0
			item.product.save(update_fields=['stock'])
		item.delete()
		messages.success(request, 'Item removed from your cart.')
	return redirect(f"{reverse('account:profile')}?store={storefront['slug']}")


def registration_view(request):
	storefront = get_storefront(request)
	storefront_url = reverse(storefront['url_name']) if storefront else None

	if request.user.is_authenticated:
		return redirect('home:mall')
	storefront_choices = [(slug, details['name']) for slug, details in STOREFRONTS.items()]

	context = {
		'storefront': storefront,
		'storefront_slug': storefront['slug'] if storefront else '',
		'storefront_url': storefront_url,
	}
	if request.POST:
		form = RegistrationForm(request.POST, storefront_slug=storefront['slug'] if storefront else '', storefront_choices=storefront_choices)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			package = form.cleaned_data['access_package']
			if package == StoreAccess.Package.FULL:
				selected_stores = list(STOREFRONTS)
			elif package == StoreAccess.Package.MULTI:
				selected_stores = form.cleaned_data['stores']
			else:
				selected_stores = [storefront['slug']] if storefront else []

			for store_slug in selected_stores:
				StoreAccess.objects.get_or_create(user=account, store_slug=store_slug, defaults={'package': package})
				STOREFRONTS[store_slug]['customer_model'].objects.get_or_create(user=account, defaults={'email': email})

			login(request, account)
			merge_guest_cart(request, account, storefront['slug'] if storefront else storefront_from_request(request))

			messages.success(request, ('Registration Successful'))
			return clear_guest_cart(redirect('home:mall'))
		else:
			messages.error(request, 'Please correct the errors below and try again.')
	else: #GET request
		form = RegistrationForm(storefront_slug=storefront['slug'] if storefront else '', storefront_choices=storefront_choices)
	context['form'] = form
	return render(request, 'account/register.html', context)


def logout_view(request):
	logout(request)
	messages.success(request, ("You have been logged out."))
	return redirect('home:mall')


def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect(request.POST.get('next') or request.GET.get('next') or 'home:mall')

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['email'], password=request.POST['password'])
            if user:
                login(request, user)
                merge_guest_cart(request, user, storefront_from_request(request))
                messages.success(request, 'Welcome back!')
                return clear_guest_cart(redirect(request.POST.get('next') or request.GET.get('next') or 'home:mall'))
        messages.error(request, "Ooops! We're sorry but that didn't work. Please try again!")
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'account/login.html', context)

def account_edit(request):

	if not request.user.is_authenticated:
		return redirect("account:login")

	storefront = get_profile_storefront(request)
	if request.method == 'POST':
		form = AccountUpdateForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, 'Your profile has been updated.')
			return redirect(f"{reverse('account:profile')}?store={storefront['slug']}")
	else:
		form = AccountUpdateForm(instance=request.user)

	customer = get_store_customer(request.user, storefront['customer_model'])
	orders = getattr(customer, storefront['orders_accessor']).all()
	context = {
		'account_form': form,
		'account_storefront': storefront,
	}
	context.update(get_account_cart_context(orders, storefront))
	return render(request, 'account/edit_profile.html', context)

def account_view(request):

	if not request.user.is_authenticated:
		return redirect("account:login")

	storefront = get_profile_storefront(request)
	customer = get_store_customer(request.user, storefront['customer_model'])
	orders = getattr(customer, storefront['orders_accessor']).all()
	form = AccountUpdateForm(
			initial= {
				"email": request.user.email,
				"username": request.user.username,
			}
		)
	context = {
		'orders': orders,
		'account_form': form,
		'account_storefront': storefront,
	}
	context.update(get_account_cart_context(orders, storefront))
	return render(request, 'account/profile.html', context)
