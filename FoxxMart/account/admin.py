from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import *


class AccountAdmin(UserAdmin):
	list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff')
	search_fields = ('email', 'username',)
	readonly_fields = ('date_joined', 'last_login')

	filter_horizontal = ()
	list_filter = ()
	fieldsets = ()

admin.site.register(Account, AccountAdmin)
class ReturnAttachmentInline(admin.TabularInline):
	model = ReturnAttachment
	extra = 0
	readonly_fields = ('uploaded_at',)


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
	list_display = ('invoice', 'user', 'reason', 'status', 'created_at')
	list_filter = ('status', 'reason', 'invoice__store_slug')
	search_fields = ('invoice__transaction_id', 'user__email', 'details')
	readonly_fields = ('created_at', 'updated_at')
	inlines = (ReturnAttachmentInline,)
