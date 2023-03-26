from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(GENESISCustomer)
admin.site.register(GENESISProduct)
admin.site.register(GENESISOrder)
admin.site.register(GENESISOrderItem)
admin.site.register(GENESISShippingAddress)
