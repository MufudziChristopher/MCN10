import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from account.models import StoreAccess
from django.contrib import messages
from Axis.models import AxisCustomer
from EXODUS.models import EXODUSCustomer
from GENESIS.models import GENESISCustomer
from Collective.models import CollectiveCustomer
from .cart_lifecycle import clear_guest_cart, merge_guest_cart, storefront_from_request


STOREFRONTS = {
	'axis': {'slug': 'axis', 'name': '3rd Axis Storefront', 'url_name': 'Axis:store'},
	'exodus': {'slug': 'exodus', 'name': 'EXODUS Storefront', 'url_name': 'EXODUS:store'},
	'genesis': {'slug': 'genesis', 'name': 'GENESIS Storefront', 'url_name': 'GENESIS:store'},
	'collective': {'slug': 'collective', 'name': 'The Collective Storefront', 'url_name': 'Collective:store'},
}


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

			customer_models = {
				'axis': AxisCustomer,
				'genesis': GENESISCustomer,
				'exodus': EXODUSCustomer,
				'collective': CollectiveCustomer,
			}
			for store_slug in selected_stores:
				StoreAccess.objects.get_or_create(user=account, store_slug=store_slug, defaults={'package': package})
				customer_models[store_slug].objects.get_or_create(user=account, defaults={'email': email})

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

	context = {}

	form = AccountUpdateForm(request.POST, instance=request.user)
	if form.is_valid():
		form.save()
		print("Form Saved")
		return render(request, 'account/profile.html', context)


	context['account_form'] = form
	print(context)
	return render(request, 'account/edit_profile.html', context)

def account_view(request):

	if not request.user.is_authenticated:
		return redirect("account:login")

	context = {}
	orders = request.user.customer.order_set.all()
	print("ORDERS::: ", orders)
	form = AccountUpdateForm(
			initial= {
				"email": request.user.email,
				"username": request.user.username,
			}
		)
	context = {'orders': orders, 'account_form': form }
	return render(request, 'account/profile.html', context)
