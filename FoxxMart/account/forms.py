from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import Account, StoreAccess


class RegistrationForm(UserCreationForm):
	email = forms.EmailField(max_length=60, help_text='Required. Add a valid email address')
	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	access_package = forms.ChoiceField(
		choices=StoreAccess.Package.choices,
		widget=forms.RadioSelect,
		initial='single',
	)
	stores = forms.MultipleChoiceField(required=False, choices=(), widget=forms.CheckboxSelectMultiple)

	def __init__(self, *args, storefront_slug='', storefront_choices=(), **kwargs):
		super().__init__(*args, **kwargs)
		self.storefront_slug = storefront_slug
		self.fields['stores'].choices = storefront_choices

	def clean(self):
		cleaned = super().clean()
		package = cleaned.get('access_package')
		stores = cleaned.get('stores') or []
		if package == 'single' and not self.storefront_slug:
			self.add_error('access_package', 'Start registration from a store to choose single-store access.')
		if package == 'multi' and not stores:
			self.add_error('stores', 'Choose at least one store for multi-store access.')
		return cleaned

	def save(self, commit=True):
		user = super().save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.username = f"{user.first_name} {user.last_name}".strip()
		if commit:
			user.save()
		return user

	class Meta:
		model = Account
		fields = ("first_name", "last_name", "email", 'phone', "password1", "password2")


class AccountAuthenticationForm(forms.ModelForm):

	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	class Meta:
		model = Account
		fields = ('email', 'password')

	def clean(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			password = self.cleaned_data['password']
			if not authenticate(email=email, password=password):
				raise forms.ValidationError("Invalid login")



class AccountUpdateForm(forms.ModelForm):

	class Meta:
		model = Account
		fields = ('email', 'username')

	def clean_email(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			try:
				account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
			except Account.DoesNotExist:
				return email
			raise forms.ValidationError('Email "%s" is already in use.' % email)

	def clean_username(self):
		if self.is_valid():
			username = self.cleaned_data['username']
			try:
				account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
			except Account.DoesNotExist:
				return username
			raise forms.ValidationError('Username "%s" is already in use.' % username)
