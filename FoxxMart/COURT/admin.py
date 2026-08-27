from django.contrib import admin

from .models import Booking, YogaClass


@admin.register(YogaClass)
class YogaClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'weekday', 'start_time', 'end_time', 'location', 'capacity', 'active')
    list_filter = ('weekday', 'active')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'yoga_class', 'booking_date', 'email', 'created_at')
    list_filter = ('booking_date', 'yoga_class')
    search_fields = ('name', 'email', 'phone')
