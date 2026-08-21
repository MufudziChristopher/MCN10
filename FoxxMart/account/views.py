from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.contrib import messages
from Axis.models import AxisCustomer
from EXODUS.models import EXODUSCustomer
from GENESIS.models import GENESISCustomer
from Collective.models import CollectiveCustomer


STOREFRONTS = {
	'axis': {'slug': 'axis', 'name': '3rd Axis Storefront', 'url_name': 'Axis:store'},
	'exodus': {'slug': 'exodus', 'name': 'EXODUS Storefront', 'url_name': 'EXODUS:store'},
	'genesis': {'slug': 'genesis', 'name': 'GENESIS Storefront', 'url_name': 'GENESIS:store'},
	'collective': {'slug': 'collective', 'name': 'The Collective Storefront', 'url_name': 'Collective:store'},
}


def get_storefront(request):
	store_slug = request.POST.get('store') or request.GET.get('store')
	return STOREFRONTS.get(store_slug)

def registration_view(request):
	storefront = get_storefront(request)
	storefront_url = reverse(storefront['url_name']) if storefront else None

	if request.user.is_authenticated:
		return redirect(storefront_url or "home:home")

	context = {
		'storefront': storefront,
		'storefront_slug': storefront['slug'] if storefront else '',
		'storefront_url': storefront_url,
	}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			for customer_model in (
				AxisCustomer,
				GENESISCustomer,
				EXODUSCustomer,
				CollectiveCustomer,
			):
				customer_model.objects.get_or_create(
					user=account,
					defaults={'email': email},
				)

			login(request, account)

			messages.success(request, ('Registration Successful'))
			return redirect(storefront_url or 'home:home')
		else:
			messages.error(request, 'Please correct the errors below and try again.')
	else: #GET request
		form = RegistrationForm()
	context['form'] = form
	return render(request, 'account/register.html', context)


def logout_view(request):
	logout(request)
	messages.success(request, ("You have been logged out."))
	return redirect('home:home')


def login_view(request):

	 context = {}

	 user = request.user
	 if user.is_authenticated:
	 	return redirect("home:home")

	 if request.POST:
	 	form = AccountAuthenticationForm(request.POST)
	 	if form.is_valid():
	 		email = request.POST['email']
	 		password = request.POST['password']
	 		user = authenticate(email=email, password=password)

	 		if user:
	 			login(request, user)
	 			messages.success(request, ("Welcome back!"))
	 			return redirect("home:home")
	 		else:
	 			messages.success(request, ("Ooops! We're sorry but that didn't work. Please try again!"))
	 			return redirect('account:login')

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
