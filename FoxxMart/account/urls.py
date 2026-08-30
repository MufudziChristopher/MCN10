from django.urls import path

from . import views

app_name = "account"


urlpatterns = [
    #Leave as empty string for base url
	path('', views.account_view, name="profile"),
	path('edit/', views.account_edit, name="edit"),
	path('register/', views.registration_view, name="register"),
	path('logout/', views.logout_view, name="logout"),
	path('login/', views.login_view, name="login"),
	path('region/', views.set_region, name="set_region"),
	path('cart/remove/', views.remove_cart_item, name='remove_cart_item'),
	path('invoices/<uuid:public_id>/', views.invoice_view, name='invoice_view'),
	path('invoices/<uuid:public_id>/download/', views.invoice_download, name='invoice_download'),
	path('invoices/<uuid:public_id>/return/', views.request_return, name='request_return'),
	path('invoices/<uuid:public_id>/return/details/', views.return_detail, name='return_detail'),
	path('invoices/<uuid:public_id>/return/cancel/', views.cancel_return, name='cancel_return'),
	path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
	path('admin-dashboard/orders/<slug:store_slug>/<int:order_id>/', views.admin_update_order, name='admin_update_order'),
	path('admin-dashboard/returns/<int:return_id>/', views.admin_update_return, name='admin_update_return'),
	path('admin-dashboard/orders/<slug:store_slug>/<int:order_id>/details/', views.admin_order_detail, name='admin_order_detail'),
	path('admin-dashboard/returns/<int:return_id>/details/', views.admin_return_detail, name='admin_return_detail'),
    ]
