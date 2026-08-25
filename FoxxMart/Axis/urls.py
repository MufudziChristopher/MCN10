from django.urls import path

from . import views
from . import api

app_name = "Axis"


urlpatterns = [
    #Leave as empty string for base url

    #------------ (STORE - URLS) ------------

	path('', views.store, name="store"),
    path('product_details/<str:pk>/', views.product_details, name="product_details"),
    path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('about/', views.about, name="about"),
	path('update_item/', views.updateItem, name="update_item"),
    path('checkout/complete-test/', views.complete_test_checkout, name='complete_test_checkout'),
    path('invoice/<int:pk>/', views.invoice, name='invoice'),
	path('contact/', views.contact, name="contact"),

    # Version 1 storefront API
    path('api/v1/products/', api.products, name='api_products'),
    path('api/v1/products/<int:product_id>/', api.product_detail, name='api_product_detail'),
    path('api/v1/cart/', api.cart, name='api_cart'),
    path('api/v1/cart/items/', api.cart_items, name='api_cart_items'),


    #------------ (CRM - URLS) ------------
	path('dashboard', views.dashboard, name="dashboard"),
    path('customer/<str:pk>/', views.customer, name="customer"),
    path('shipping_details/<str:pk>/', views.shippingDetails, name="shipping_details"),

    #------------ (CRUD - Order - URLS) ------------
    path('create_order/', views.createOrder, name="create_order"),
    path('update_order/<str:pk>/', views.updateOrder, name="update_order"),
    path('order_details/<str:pk>/', views.viewOrder, name="view_order"),
    path('delete_order/<str:pk>/', views.deleteOrder, name="delete_order"),


    #------------ (CRUD - Products - URLS) ------------
    path('products/', views.products, name="products"),
    path('add_product/', views.addProduct, name="add_product"),
    path('delete_product/<str:pk>/', views.deleteProduct, name="delete_product"),
    path('update_product/<str:pk>/', views.updateProduct, name="update_product"),

    #------------ (CRUD - Category - URLS) ------------
    path('categories/', views.categories, name="categories"),
    path('add_category/', views.addCategory, name="add_category"),
    path('delete_category/<str:pk>/', views.deleteCategory, name="delete_category"),
    path('update_category/<str:pk>/', views.updateCategory, name="update_category"),

]
