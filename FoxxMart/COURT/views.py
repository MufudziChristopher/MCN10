from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import BookingForm
from .models import YogaClass


def store(request):
	if request.method == 'POST':
		booking_form = BookingForm(request.POST)
		if booking_form.is_valid():
			booking = booking_form.save()
			messages.success(request, f'Your {booking.yoga_class.name} booking is confirmed.')
			return redirect('COURT:store')
	else:
		booking_form = BookingForm()

	return render(request, 'court_base.html', {
		'booking_form': booking_form,
		'classes': YogaClass.objects.filter(active=True),
	})
