from django.forms import ModelForm
from .models import *

class OrderForm(ModelForm):
	class Meta:
		model = GENESISOrder
		fields = '__all__'
		exclude = ['transaction_id']


class OrderItemsForm(ModelForm):
	class Meta:
		model = GENESISOrderItem
		fields = '__all__'


class ShippingDetailsForm(ModelForm):
	class Meta:
		model = GENESISShippingAddress
		fields = '__all__'


class ProductsForm(ModelForm):
	class Meta:
		model = GENESISProduct
		fields = '__all__'
