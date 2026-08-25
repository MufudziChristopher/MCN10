from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.db import transaction
from django.db.models import Count
from taggit.models import Tag

import json
import uuid

from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST


from .models import *
from .forms import *
from .utils import cartData
from .models import *
from .filters import *
from account.access import store_access_required

# Create your views here.
def about(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'cartItems': cartItems, 'items': items, 'order': order,}
    return render(request, 'Axis/about.html', context)

def home(request):
    return render(request, 'home_base.html', {})


def store(request, category_slug=None):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    products = Product.objects.all()
    taglist = (
        Tag.objects.filter(product__isnull=False)
        .annotate(total_products=Count('product'))
        .order_by('name')
    )
    context = {'cartItems': cartItems, 'items': items, 'order': order, 'products':products, 'shipping': False, 'taglist': taglist}
    return render(request, 'Axis/store.html', context)



@store_access_required('axis')
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'Axis/cart.html', context)

def product_details(request, pk):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    category = None

    product = Product.objects.get(id=pk)
    category = None
    product_images = [
        product.imageURL1,
        product.imageURL2(),
        product.imageURL3(),
        product.imageURL4(),
        product.imageURL5(),
    ]
    view_descriptions = (
        ('Front three-quarter view', f'{product.name} shown as a complete system from the primary working angle.'),
        ('Side profile', f'A clear side view of the {product.name} chassis, working envelope and form factor.'),
        ('Rear three-quarter view', f'A rear perspective showing the {product.name} housing and service-side design.'),
        ('Detail view', f'A closer look at the precision components and material details of the {product.name}.'),
        ('Hero view', f'The {product.name} in a full product view for comparing its overall silhouette.'),
    )
    gallery_items = [
        {'url': image, 'title': view_descriptions[index][0], 'description': view_descriptions[index][1]}
        for index, image in enumerate(product_images) if image
    ]
    context = {
        'cartItems': cartItems,
        'items': items,
        'order': order,
        'product': product,
        'gallery_items': gallery_items,
        'category': category,
        'shipping': False,
    }
    return render(request, 'Axis/product.html', context)


@store_access_required('axis')
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'Axis/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.axiscustomer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, status="Pending")

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'set':
        try:
            quantity = max(0, int(data.get('quantity', 0)))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Quantity must be a whole number.'}, status=400)

        # Stock excludes the units already reserved in this pending order.
        available_quantity = product.stock + orderItem.quantity
        quantity = min(quantity, available_quantity)
        product.stock += orderItem.quantity - quantity
        orderItem.quantity = quantity

    elif action == 'add':
        if  product.stock >= 1:
            product.stock = (product.stock - 1)
            orderItem.quantity = (orderItem.quantity + 1)
            print("Stock: ",product.stock)

        else:
            messages.success(request, ("There is currently not enough stock available to fullfill your order"))

    elif action == 'remove':
        product.stock = (product.stock + 1)
        print("Stock: ",product.stock)
        orderItem.quantity = (orderItem.quantity - 1)

    elif action == 'cancel':
                product.stock = (product.stock + orderItem.quantity)
                print("Stock: ",product.stock)
                print("Quantity: ",orderItem.quantity)
                orderItem.quantity = (orderItem.quantity == 0)

    product.save()

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse({'quantity': orderItem.quantity}, safe=False)

def contact(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'cartItems': cartItems, 'items': items, 'order': order,}

    if request.method == 'POST':
        message = request.POST['message']

        if request.user.is_authenticated:
            name = request.user.username
            email = request.user.email
            message = name + "\n" + email + "\n"+ message
            send_mail('Contact Form', message, settings.EMAIL_HOST_USER, ['christopher@3rdaxis.co.za', 'mcn10.foxx@gmail.com'], fail_silently="false" )
            messages.success(request, ("Your message has been sent successfully..."))
        else:
            name = request.POST['name']
            email = request.POST['email']
            message = name + "\n" + email + "\n"+ message
            send_mail('Contact Form', message, settings.EMAIL_HOST_USER, ['christopher@3rdaxis.co.za', 'mcn10.foxx@gmail.com'], fail_silently="false" )
            messages.success(request, ("Your message has been sent successfully..."))
        return redirect('Axis:store')
    return render(request, 'Axis/contact.html', context)

@require_POST
@store_access_required('axis')
def complete_test_checkout(request):
    """Server-side test checkout; no totals or payment state are accepted from the browser."""
    customer = request.user.axiscustomer
    required_shipping = ('country', 'address1', 'suburb', 'city', 'province', 'postal_code')
    if any(not request.POST.get(field, '').strip() for field in required_shipping):
        messages.error(request, 'Please complete all required shipping fields.')
        return redirect('Axis:checkout')

    # Lock the pending order so two rapid submissions cannot complete it twice.
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(), customer=customer, status='Pending'
        )
        if not order.orderitem_set.filter(product__isnull=False).exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('Axis:cart')

        shipping_address = ShippingAddress.objects.create(
            country=request.POST['country'].strip(),
            address1=request.POST['address1'].strip(),
            address2=request.POST.get('address2', '').strip(),
            suburb=request.POST['suburb'].strip(),
            city=request.POST['city'].strip(),
            province=request.POST['province'].strip(),
            postal_code=request.POST['postal_code'].strip(),
        )
        customer.shippingAddress = shipping_address
        customer.save(update_fields=['shippingAddress'])
        order.transaction_id = f'TEST-{uuid.uuid4().hex[:12].upper()}'
        order.status = 'Payment Confirmed, Processing Order'
        order.save(update_fields=['transaction_id', 'status'])
    messages.success(request, 'Test payment recorded. Your invoice is ready.')
    return redirect('Axis:invoice', pk=order.pk)


@store_access_required('axis')
def invoice(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user.axiscustomer)
    return render(request, 'Axis/invoice.html', {'order': order, 'items': order.orderitem_set.select_related('product')})



#-------------------(DETAIL/LIST VIEWS) -------------------

def dashboard(request):
    orders = Order.objects.all().order_by('-status')[0:5]
    customers = AxisCustomer.objects.all()

    total_customers = customers.count()

    total_orders = Order.objects.all().count()
    delivered = Order.objects.filter(status='Delivered').count()
    pending = Order.objects.filter(status='Pending').count()



    context = {'customers':customers, 'orders':orders,
    'total_customers':total_customers,'total_orders':total_orders,
    'delivered':delivered, 'pending':pending}
    return render(request, 'Axis/AxisCRM/dashboard.html', context)


def customer(request, pk):
    customer = AxisCustomer.objects.get(id=pk)
    orders = customer.order_set.all()
    shippingDetails = ShippingAddress.objects.all()
    total_orders = orders.count()

    orderFilter = OrderFilter(request.GET, queryset=orders)
    orders = orderFilter.qs

    context = {'shippingDetails':shippingDetails, 'customer':customer, 'orders':orders, 'total_orders':total_orders,
    'filter':orderFilter}
    return render(request, 'Axis/AxisCRM/customer.html', context)


def shippingDetails(request):
    action = 'update'
    shippingDetails = ShippingAddress.objects.all()
    form = ShippingDetailsForm(instance=shippingDetails)

    context =  {'action':action, 'form':form}
    return render(request, 'Axis/AxisCRM/order_form.html', context)

#-------------------(CRUD ORDERS) -------------------

def createOrder(request):
    action = 'create'
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/3rdAxis/')

    context =  {'action':action, 'form':form}
    return render(request, 'Axis/AxisCRM/order_form.html', context)

def updateOrder(request, pk):
    action = 'update'
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/3rdAxis//order_details/' + str(order.id))

    context =  {'action':action, 'form':form}
    return render(request, 'Axis/AxisCRM/order_form.html', context)

def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        customer_id = order.AxisCustomer.id
        customer_url = '/3rdAxis//customer/' + str(customer_id)
        order.delete()
        return redirect(customer_url)

    return render(request, 'Axis/AxisCRM/delete_item.html', {'item':order})

def viewOrder(request, pk):
    order = Order.objects.get(id=pk)
    # shippingDetails = Order.shippingDetails
    items = order.orderitem_set.all()
    customer = request.user.customer
    cartItems = order.get_cart_items

    form = OrderItemsForm(instance=order)
    if request.method == 'POST':
        form = OrderItemsForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/3rdAxis/customer/' + str(order.AxisCustomer.id))

    shippingDetails = customer.shippingAddress
    print("Shipping Address: ", customer.shippingAddress)


    context =  { 'order':order,  'form':form, 'shippingDetails': shippingDetails, 'items':items, 'cartItems': cartItems}
    return render(request, 'Axis/AxisCRM/order_details.html', context)



#-------------------(CRUD - PRODUCTS) -------------------

def addProduct(request):
    action = 'create'
    name = "Product"
    form = ProductsForm()
    if request.method == 'POST':
        form = ProductsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/3rdAxis/products/')

    context =  {'action':action, 'form':form, 'name':name }
    return render(request, 'Axis/AxisCRM/order_form.html', context)

def products(request):
    products = Product.objects.all()
    productFilter = ProductFilter(request.GET, queryset=products)
    total_products = products.count()
    products = productFilter.qs

    context = {'total_products': total_products, 'products':products, 'filter': productFilter}

    return render(request, 'Axis/AxisCRM/products.html', context)

def updateProduct(request, pk):
    action = 'update'
    product = Product.objects.get(id=pk)
    name = product.name
    form = ProductsForm(instance=product)

    if request.method == 'POST':
        form = ProductsForm(request.POST, instance=product)
        if form.is_valid():
            newproduct = form.save(commit=False)
            newproduct.slug = slugify(newproduct.name)
            newproduct.save()
            # Without this next line the tags won't be saved.
            form.save()
            return redirect('/3rdAxis/products/')

    context =  {'action':action, 'form':form, 'name':name, 'product': product, }
    return render(request, 'Axis/AxisCRM/order_form.html', context)

def deleteProduct(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('/3rdAxis/products')

    return render(request, 'Axis/AxisCRM/delete_item.html', {'item':product})


#-------------------(CRUD - CATEGORIES) -------------------

def categories(request):
    categories = Category.objects.all()
    categoryFilter = CategoryFilter(request.GET, queryset=categories)
    total_categories = categories.count()
    categories = categoryFilter.qs

    context = {'total_categories': total_categories, 'categories':categories, 'filter': categoryFilter}

    return render(request, 'Axis/AxisCRM/category.html', context)

def addCategory(request):
    action = 'create'
    name = "Category"
    form = CategoriesForm()
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/3rdAxis/categories/')

    context =  {'action':action, 'form':form, 'name':name }
    return render(request, 'Axis/AxisCRM/order_form.html', context)

def updateCategory(request, pk):
    action = 'update'
    category = Category.objects.get(id=pk)
    name = category.category_name
    form = CategoriesForm(instance=category)

    if request.method == 'POST':
        form = CategoriesForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('/3rdAxis/categories/')

    context =  {'action':action, 'form':form, 'name':name }
    return render(request, 'Axis/AxisCRM/order_form.html', context)

def deleteCategory(request, pk):
    category = Category.objects.get(id=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('/3rdAxis/categories/')

    return render(request, 'Axis/AxisCRM/delete_item.html', {'item':category})
