from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(EXODUSCustomer)
admin.site.register(EXODUSProduct)
admin.site.register(EXODUSOrder)
admin.site.register(EXODUSOrderItem)
admin.site.register(EXODUSShippingAddress)
