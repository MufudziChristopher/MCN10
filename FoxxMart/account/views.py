import json
import secrets
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse, Http404
from django.core.exceptions import PermissionDenied
from django.utils.http import url_has_allowed_host_and_scheme
from django.db import transaction
from django.views.decorators.http import require_POST
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from account.models import Account, GoogleOAuthIdentity, StoreAccess, Invoice, ReturnRequest, ReturnAttachment
from account.invoices import invoice_pdf_response
from django.contrib import messages
from django.core.mail import send_mail
from .cart_lifecycle import clear_guest_cart, merge_guest_cart, storefront_from_request
from .customer_profiles import get_store_customer
from .storefronts import STOREFRONTS, get_profile_storefront


def provision_storefront_access(account):
	"""Give a newly-created account the standard mall-wide storefront setup."""
	for store_slug, details in STOREFRONTS.items():
		StoreAccess.objects.get_or_create(
			user=account, store_slug=store_slug, defaults={'package': StoreAccess.Package.FULL}
		)
		details['customer_model'].objects.get_or_create(user=account, defaults={'email': account.email})


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
	if request.user.is_authenticated:
		return redirect('home:mall')
	context = {'google_oauth_enabled': bool(
		settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET
	)}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)

			# One Foxx Mart account belongs to every storefront from day one.
			provision_storefront_access(account)

			login(request, account)
			merge_guest_cart(request, account, storefront_from_request(request))

			messages.success(request, ('Registration Successful'))
			return clear_guest_cart(redirect('home:mall'))
		else:
			messages.error(request, 'Please correct the errors below and try again.')
	else: #GET request
		form = RegistrationForm()
	context['form'] = form
	return render(request, 'account/register.html', context)


def logout_view(request):
	logout(request)
	messages.success(request, ("You have been logged out."))
	return redirect('home:mall')


def login_view(request):
    context = {'google_oauth_enabled': bool(
        settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET
    )}
    user = request.user
    if user.is_authenticated:
        return _cart_redirect(request)

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['email'], password=request.POST['password'])
            if user:
                login(request, user)
                merge_guest_cart(request, user, storefront_from_request(request))
                messages.success(request, 'Welcome back!')
                return clear_guest_cart(_cart_redirect(request))
        messages.error(request, "Ooops! We're sorry but that didn't work. Please try again!")
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'account/login.html', context)


def _safe_next_url(request, value):
	return value if value and url_has_allowed_host_and_scheme(value, {request.get_host()}) else None


def _cart_redirect(request, store_slug=None):
	"""Return every successful sign-in flow to the Foxx Mart Mall."""
	return redirect('home:mall')


def google_login(request):
	"""Begin Google's authorization-code sign-in flow."""
	if not (settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET):
		messages.error(request, 'Google sign-in is not configured yet.')
		return redirect('account:login')

	state = secrets.token_urlsafe(32)
	request.session['google_oauth_state'] = state
	request.session['google_oauth_next'] = _safe_next_url(request, request.GET.get('next'))
	request.session['google_oauth_store'] = storefront_from_request(request)
	parameters = {
		'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
		'redirect_uri': request.build_absolute_uri(reverse('google_callback')),
		'response_type': 'code',
		'scope': 'openid email profile',
		'state': state,
		'access_type': 'online',
		'prompt': 'select_account',
	}
	return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(parameters)}")


def google_callback(request):
	"""Exchange Google's callback code and log the verified account in."""
	expected_state = request.session.pop('google_oauth_state', None)
	request.session.pop('google_oauth_next', None)
	store_slug = request.session.pop('google_oauth_store', None)
	if not expected_state or not secrets.compare_digest(request.GET.get('state', ''), expected_state):
		messages.error(request, 'Google sign-in could not be verified. Please try again.')
		return redirect('account:login')
	if request.GET.get('error') or not request.GET.get('code'):
		messages.error(request, 'Google sign-in was cancelled or did not complete.')
		return redirect('account:login')

	redirect_uri = request.build_absolute_uri(reverse('google_callback'))
	try:
		token_response = requests.post(
			'https://oauth2.googleapis.com/token',
			data={
				'code': request.GET['code'],
				'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
				'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
				'redirect_uri': redirect_uri,
				'grant_type': 'authorization_code',
			},
			timeout=10,
		)
		token_response.raise_for_status()
		access_token = token_response.json()['access_token']
		profile_response = requests.get(
			'https://openidconnect.googleapis.com/v1/userinfo',
			headers={'Authorization': f'Bearer {access_token}'}, timeout=10,
		)
		profile_response.raise_for_status()
		profile = profile_response.json()
	except (KeyError, ValueError, requests.RequestException):
		messages.error(request, 'Google could not complete sign-in. Please try again.')
		return redirect('account:login')

	email = (profile.get('email') or '').strip().lower()
	google_subject = profile.get('sub')
	if not email or not google_subject or profile.get('email_verified') is not True:
		messages.error(request, 'A verified Google email address is required to sign in.')
		return redirect('account:login')

	with transaction.atomic():
		identity = GoogleOAuthIdentity.objects.select_related('user').filter(google_subject=google_subject).first()
		if identity:
			user = identity.user
		else:
			user = Account.objects.filter(email__iexact=email).first()
			if user is None:
				user = Account.objects.create(
					email=email,
					username=(profile.get('name') or email.split('@', 1)[0])[:30],
					first_name=(profile.get('given_name') or '')[:30],
					last_name=(profile.get('family_name') or '')[:30],
				)
			GoogleOAuthIdentity.objects.create(user=user, google_subject=google_subject)
		provision_storefront_access(user)

	login(request, user)
	merge_guest_cart(request, user, store_slug or storefront_from_request(request))
	messages.success(request, 'You are now signed in with Google.')
	return clear_guest_cart(_cart_redirect(request, store_slug))

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
	invoices = Invoice.objects.filter(user=request.user, store_slug=storefront['slug'])
	return_requests = ReturnRequest.objects.filter(user=request.user, invoice__store_slug=storefront['slug'])
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
		'invoices': invoices,
		'return_requests': return_requests,
	}
	context.update(get_account_cart_context(orders, storefront))
	return render(request, 'account/profile.html', context)


def _owned_invoice(request, public_id):
	if not request.user.is_authenticated:
		raise Http404
	invoice = get_object_or_404(Invoice, public_id=public_id)
	if invoice.user_id != request.user.id and not request.user.is_superuser:
		raise Http404
	return invoice


def invoice_view(request, public_id):
	return invoice_pdf_response(_owned_invoice(request, public_id))


def invoice_download(request, public_id):
	return invoice_pdf_response(_owned_invoice(request, public_id), download=True)


@require_POST
def request_return(request, public_id):
	invoice = _owned_invoice(request, public_id)
	reason = request.POST.get('reason', '').strip()
	details = request.POST.get('details', '').strip()
	allowed_reasons = {'Damaged item', 'Incorrect item', 'Does not fit', 'Changed my mind', 'Other'}
	if reason not in allowed_reasons:
		messages.error(request, 'Please select a valid reason for your return.')
	elif ReturnRequest.objects.filter(invoice=invoice).exists():
		messages.info(request, 'A return request already exists for this order.')
	else:
		return_request = ReturnRequest.objects.create(user=request.user, invoice=invoice, reason=reason, details=details)
		for image in request.FILES.getlist('images'):
			if not image.content_type.startswith('image/') or image.size > 5 * 1024 * 1024:
				messages.warning(request, 'Only image files up to 5 MB were attached.')
				continue
			ReturnAttachment.objects.create(return_request=return_request, image=image)
		send_mail(
			subject=f'Return request: {invoice.transaction_id or invoice.order_reference}',
			message=(f'Customer: {request.user.email}\nInvoice: {invoice}\nReason: {reason}\n'
				f'Details: {details or "None"}\nAttachments: {return_request.attachments.count()}'),
			from_email=settings.DEFAULT_FROM_EMAIL,
			recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
			fail_silently=True,
		)
		messages.success(request, 'Your return request has been submitted. We will contact you with the next steps.')
	return redirect(f"{reverse('account:profile')}?store={invoice.store_slug}")


def return_detail(request, public_id):
	invoice = _owned_invoice(request, public_id)
	return_request = get_object_or_404(ReturnRequest.objects.prefetch_related('attachments'), invoice=invoice)
	return render(request, 'account/return_detail.html', {'return_request': return_request, 'account_storefront': STOREFRONTS[invoice.store_slug]})


@require_POST
def cancel_return(request, public_id):
	invoice = _owned_invoice(request, public_id)
	return_request = get_object_or_404(ReturnRequest, invoice=invoice)
	if return_request.status != ReturnRequest.Status.REQUESTED:
		messages.error(request, 'Only pending return requests can be cancelled.')
	else:
		return_request.status = ReturnRequest.Status.CANCELLED
		return_request.save(update_fields=['status', 'updated_at'])
		messages.success(request, 'Your return request has been cancelled.')
	return redirect('account:return_detail', public_id=invoice.public_id)


def admin_dashboard(request):
	if not request.user.is_superuser:
		raise PermissionDenied
	orders = []
	for store_slug, storefront in STOREFRONTS.items():
		for order in storefront['order_model'].objects.select_related('customer').order_by('-date_ordered')[:50]:
			orders.append({
				'store_slug': store_slug, 'store_name': storefront['menu_label'], 'order': order,
				'customer_email': getattr(order.customer, 'email', 'Unknown customer'),
				'total': getattr(order, 'get_total_with_vat', order.get_cart_total),
				'statuses': storefront['order_model'].STATUS,
			})
	orders.sort(key=lambda item: item['order'].date_ordered, reverse=True)
	return_requests = ReturnRequest.objects.select_related('invoice', 'user').prefetch_related('attachments')[:100]
	return render(request, 'account/admin_dashboard.html', {
		'orders': orders[:100], 'return_requests': return_requests,
		'return_statuses': ReturnRequest.Status.choices,
	})


@require_POST
def admin_update_order(request, store_slug, order_id):
	if not request.user.is_superuser:
		raise PermissionDenied
	storefront = STOREFRONTS.get(store_slug)
	if not storefront:
		raise Http404
	order = get_object_or_404(storefront['order_model'], pk=order_id)
	allowed = dict(storefront['order_model'].STATUS)
	status = request.POST.get('status')
	if status in allowed:
		order.status = status
		order.save(update_fields=['status'])
		messages.success(request, 'Order status updated.')
	next_url = request.POST.get('next', '')
	if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
		return redirect(next_url)
	return redirect('account:admin_dashboard')


@require_POST
def admin_update_return(request, return_id):
	if not request.user.is_superuser:
		raise PermissionDenied
	return_request = get_object_or_404(ReturnRequest, pk=return_id)
	status = request.POST.get('status')
	if status in dict(ReturnRequest.Status.choices):
		return_request.status = status
		return_request.save(update_fields=['status', 'updated_at'])
		messages.success(request, 'Return status updated.')
	next_url = request.POST.get('next', '')
	if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
		return redirect(next_url)
	return redirect('account:admin_dashboard')


def admin_order_detail(request, store_slug, order_id):
	if not request.user.is_superuser:
		raise PermissionDenied
	storefront = STOREFRONTS.get(store_slug)
	if not storefront:
		raise Http404
	order = get_object_or_404(storefront['order_model'].objects.select_related('customer'), pk=order_id)
	items = getattr(order, storefront['order_items_accessor']).select_related('product').filter(product__isnull=False)
	shipping_address = getattr(order.customer, 'shippingAddress', None) if order.customer else None
	if shipping_address is None:
		shipping_relation = getattr(order, 'collectiveshippingaddress_set', None)
		shipping_address = shipping_relation.first() if shipping_relation else None
	invoice = Invoice.objects.filter(store_slug=store_slug, order_reference=str(order.pk)).first()
	return render(request, 'account/admin_order_detail.html', {
		'order': order, 'items': items, 'storefront': storefront,
		'shipping_address': shipping_address,
		'invoice': invoice,
		'statuses': storefront['order_model'].STATUS,
		'total': getattr(order, 'get_total_with_vat', order.get_cart_total),
	})


def admin_return_detail(request, return_id):
	if not request.user.is_superuser:
		raise PermissionDenied
	return_request = get_object_or_404(
		ReturnRequest.objects.select_related('invoice', 'user').prefetch_related('attachments'), pk=return_id
	)
	return render(request, 'account/admin_return_detail.html', {
		'return_request': return_request,
		'return_statuses': ReturnRequest.Status.choices,
	})
