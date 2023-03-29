from django.forms import ModelForm
from .models import *

class OrderForm(ModelForm):
	class Meta:
		model = EXODUSOrder
		fields = '__all__'
		exclude = ['transaction_id']


class OrderItemsForm(ModelForm):
	class Meta:
		model = EXODUSOrderItem
		fields = '__all__'


class ShippingDetailsForm(ModelForm):
	class Meta:
		model = EXODUSShippingAddress
		fields = '__all__'


class ProductsForm(ModelForm):
	class Meta:
		model = EXODUSProduct
		fields = '__all__'
