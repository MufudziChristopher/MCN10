from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from Axis.models import Product
import uuid



class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		user = self.model(
			email=self.normalize_email(email),
			username=username,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


class Account(AbstractBaseUser):
	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True)
	username 				= models.CharField(max_length=30, verbose_name="Full Name")
	first_name				= models.CharField(max_length=30, blank=True)
	last_name				= models.CharField(max_length=30, blank=True)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=False)
	is_axisStaff			= models.BooleanField(default=False)
	is_staff				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	objects = MyAccountManager()

	def __str__(self):
		return self.email

	# For checking permissions. to keep it simple all admin have ALL permissons
	def has_perm(self, perm, obj=None):
		return self.is_admin

	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
	def has_module_perms(self, app_label):
		return True


class StoreAccess(models.Model):
	class Package(models.TextChoices):
		SINGLE = 'single', 'Single store'
		MULTI = 'multi', 'Multi-store'
		FULL = 'full', 'Full mall access'

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store_accesses')
	store_slug = models.CharField(max_length=40)
	package = models.CharField(max_length=10, choices=Package.choices)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [models.UniqueConstraint(fields=('user', 'store_slug'), name='unique_user_store_access')]

	def __str__(self):
		return f'{self.user.email} — {self.store_slug}'


class GoogleOAuthIdentity(models.Model):
	"""The stable Google subject connected to a Foxx Mart account."""
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='google_identity')
	google_subject = models.CharField(max_length=255, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.email


class Notification(models.Model):
	"""A customer-facing event generated from an order or an active cart."""
	class Kind(models.TextChoices):
		ORDER_STATUS = 'order_status', 'Order status'
		LOW_STOCK = 'low_stock', 'Low stock'
		PRICE_ALERT = 'price_alert', 'Price alert'

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
	store_slug = models.CharField(max_length=40)
	kind = models.CharField(max_length=20, choices=Kind.choices)
	event_key = models.CharField(max_length=160)
	title = models.CharField(max_length=160)
	body = models.TextField()
	url = models.CharField(max_length=500, blank=True)
	read_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at',)
		constraints = [
			models.UniqueConstraint(fields=('user', 'store_slug', 'event_key'), name='unique_customer_notification_event'),
		]

	def __str__(self):
		return f'{self.user.email}: {self.title}'


class Invoice(models.Model):
	"""An immutable order invoice snapshot owned by a Foxx Mart account."""
	public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
	store_slug = models.CharField(max_length=40)
	store_name = models.CharField(max_length=100)
	order_reference = models.CharField(max_length=100)
	transaction_id = models.CharField(max_length=200, blank=True)
	status = models.CharField(max_length=200, blank=True)
	total = models.DecimalField(max_digits=12, decimal_places=2)
	subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	items = models.JSONField(default=list)
	issued_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('-issued_at',)
		constraints = [
			models.UniqueConstraint(
				fields=('user', 'store_slug', 'order_reference'),
				name='unique_user_store_order_invoice',
			),
		]

	def __str__(self):
		return f'INV-{self.store_slug.upper()}-{self.order_reference}'


class ReturnRequest(models.Model):
	class Status(models.TextChoices):
		REQUESTED = 'requested', 'Requested'
		APPROVED = 'approved', 'Approved'
		DECLINED = 'declined', 'Declined'
		RECEIVED = 'received', 'Received'
		REFUNDED = 'refunded', 'Refunded'
		CANCELLED = 'cancelled', 'Cancelled'

	invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='return_request')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='return_requests')
	reason = models.CharField(max_length=100)
	details = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return f'Return for {self.invoice} ({self.get_status_display()})'


class ReturnAttachment(models.Model):
	return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name='attachments')
	image = models.ImageField(upload_to='return_requests/%Y/%m/%d/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Attachment for return {self.return_request_id}'
