from django.db import models


class YogaClass(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    name = models.CharField(max_length=120)
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=160)
    capacity = models.PositiveSmallIntegerField(default=12)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('weekday', 'start_time', 'name')

    def __str__(self):
        return f'{self.get_weekday_display()} — {self.name}'


class Booking(models.Model):
    yoga_class = models.ForeignKey(YogaClass, on_delete=models.PROTECT, related_name='bookings')
    booking_date = models.DateField()
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('booking_date', 'yoga_class__start_time', 'name')
        constraints = [
            models.UniqueConstraint(fields=('yoga_class', 'booking_date', 'email'), name='court_unique_booking'),
        ]

    def __str__(self):
        return f'{self.name} — {self.yoga_class} on {self.booking_date}'
