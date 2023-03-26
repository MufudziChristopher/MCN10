import django_filters
from .models import *



class OrderFilter(django_filters.FilterSet):
	class Meta:
		model = GENESISOrder
		fields = '__all__'
		exclude = [ 'date_created']

class ProductFilter(django_filters.FilterSet):
	class Meta:
		model = GENESISProduct
		fields = ['name1']
