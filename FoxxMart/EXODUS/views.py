from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm

from django.conf import settings

from .models import *
from .forms import *
from .utils import cookieCart, cartData, guestOrder
from .filters import *

# Create your views here.
def about(request):

    return render(request, 'EXODUS/about.html', {})


def store(request, category_slug=None):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    list_random1 = range(4)
    list_random2 = range(2,4)

    products = EXODUSProduct.objects.all()
    context = {'cartItems': cartItems, 'products':products , 'shipping': False, 'list_random1':list_random1, 'list_random2':list_random2}

    return render(request, 'EXODUS/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'cartItems': cartItems, 'items': items , 'order': order}

    return render(request, 'EXODUS/cart.html', context)

def product_details(request, pk):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    category = None

    product = EXODUSProduct.objects.get(id=pk)
    category = None
    context = {'cartItems': cartItems, 'product':product,'category' : category , 'shipping': False,}
    return render(request, 'EXODUS/product.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'cartItems': cartItems , 'items': items, 'order': order}
    return render(request, 'EXODUS/checkout.html', context)

def contact(request):
    if request.method == 'POST':
        message = request.POST['message']
        if request.user.is_authenticated:
            name = request.user.username
            email = request.user.email
            message = name + "\n" + email + "\n"+ message
            send_mail('Contact Form', message, settings.EMAIL_HOST_USER, ['django10.foxx@gmail.com', 'mcn10.foxx@gmail.com'], fail_silently="false" )
            messages.success(request, ("Your message has been sent successfully..."))
        else:
            name = request.POST['name']
            email = request.POST['email']
            message = name + "\n" + email + "\n"+ message
            send_mail('Contact Form', message, settings.EMAIL_HOST_USER, ['django10.foxx@gmail.com', 'mcn10.foxx@gmail.com'], fail_silently="false" )
            messages.success(request, ("Your message has been sent successfully..."))
        return redirect('EXODUS:store')

    return render(request, 'EXODUS/contact.html', {})


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.EXODUScustomer
    product = EXODUSProduct.objects.get(id=productId)
    order, created = EXODUSOrder.objects.get_or_create(customer=customer, status="Pending")

    orderItem, created = EXODUSOrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
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

    product.save()

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = EXODUSOrder.objects.get_or_create(customer=customer, status="Pending")
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        print("Order total is correct")
        order.status = "Payment Confirmed, Processing Order"
        order.save()

    else:
        print("Order total is incorrect")

    if order.shipping == True:
        EXODUSShippingAddress.objects.create(
        customer=customer,
        order=order,
        country=data['shipping']['country'],
        address1=data['shipping']['address1'],
        address2=data['shipping']['address2'],
        city=data['shipping']['city'],
        province=data['shipping']['province'],
        postal_code=data['shipping']['postal_code'],
        )

        # Add code to send email to Store Owner
    return JsonResponse('Payment Complete', safe=False)


#-------------------(DETAIL/LIST VIEWS) -------------------

def dashboard(request):
    orders = EXODUSOrder.objects.all().order_by('-status')[0:5]
    customers = EXODUSCustomer.objects.all()

    total_customers = customers.count()

    total_orders = EXODUSOrder.objects.all().count()
    delivered = EXODUSOrder.objects.filter(status='Delivered').count()
    pending = EXODUSOrder.objects.filter(status='Pending').count()



    context = {'customers':customers, 'orders':orders,
    'total_customers':total_customers,'total_orders':total_orders,
    'delivered':delivered, 'pending':pending}
    return render(request, 'EXODUS/EXODUSCRM/dashboard.html', context)


def customer(request, pk):
    customer = EXODUSCustomer.objects.get(id=pk)
    orders = customer.order_set.all()
    shippingDetails = EXODUSShippingAddress.objects.all()
    total_orders = orders.count()

    orderFilter = EXODUSOrderFilter(request.GET, queryset=orders)
    orders = orderFilter.qs

    context = {'shippingDetails':shippingDetails, 'customer':customer, 'orders':orders, 'total_orders':total_orders,
    'filter':orderFilter}
    return render(request, 'EXODUS/EXODUSCRM/customer.html', context)


def shippingDetails(request):
    action = 'update'
    shippingDetails = EXODUSShippingAddress.objects.all()
    form = EXODUSShippingDetailsForm(instance=shippingDetails)

    context =  {'action':action, 'form':form}
    return render(request, 'EXODUS/EXODUSCRM/order_form.html', context)

#-------------------(CRUD ORDERS) -------------------

def createOrder(request):
    action = 'create'
    form = EXODUSOrderForm()
    if request.method == 'POST':
        form = EXODUSOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/TheEXODUS')

    context =  {'action':action, 'form':form}
    return render(request, 'EXODUS/EXODUSCRM/order_form.html', context)

def updateOrder(request, pk):
    action = 'update'
    order = EXODUSOrder.objects.get(id=pk)
    form = EXODUSOrderForm(instance=order)

    if request.method == 'POST':
        form = EXODUSOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/TheEXODUS/order_details/' + str(order.id))

    context =  {'action':action, 'form':form}
    return render(request, 'EXODUS/EXODUSCRM/order_form.html', context)

def deleteOrder(request, pk):
    order = EXODUSOrder.objects.get(id=pk)
    if request.method == 'POST':
        customer_id = order.customer.id
        customer_url = '/TheEXODUS/customer/' + str(customer_id)
        order.delete()
        return redirect(customer_url)

    return render(request, 'EXODUS/EXODUSCRM/delete_item.html', {'item':order})

def viewOrder(request, pk):
    order = EXODUSOrder.objects.get(id=pk)
    # shippingDetails = Order.shippingDetails
    items = order.orderitem_set.all()

    cartItems = order.get_cart_items

    form = EXODUSOrderItemsForm(instance=order)
    if request.method == 'POST':
        form = EXODUSOrderItemsForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/TheEXODUS/customer/' + str(order.customer.id))

    context =  { 'order':order,  'form':form, 'shippingDetails': shippingDetails, 'items':items, 'cartItems': cartItems}
    return render(request, 'EXODUS/EXODUSCRM/order_details.html', context)


#-------------------(CRUD - PRODUCTS) -------------------

def addProduct(request):
    action = 'create'
    name = "Product"
    form = EXODUSProductsForm()
    if request.method == 'POST':
        form = EXODUSProductsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/TheEXODUS/products/')

    context =  {'action':action, 'form':form, 'name':name }
    return render(request, 'EXODUS/EXODUSCRM/order_form.html', context)

def products(request):
    products = EXODUSProduct.objects.all()
    productFilter = EXODUSProductFilter(request.GET, queryset=products)
    total_products = products.count()
    products = productFilter.qs

    context = {'total_products': total_products, 'products':products, 'filter': productFilter}

    return render(request, 'EXODUS/EXODUSCRM/products.html', context)

def updateProduct(request, pk):
    action = 'update'
    product = EXODUSProduct.objects.get(id=pk)
    name = product.name
    form = EXODUSProductsForm(instance=product)

    if request.method == 'POST':
        form = EXODUSProductsForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('/TheEXODUS/products/')

    context =  {'action':action, 'form':form, 'name':name }
    return render(request, 'EXODUS/EXODUSCRM/order_form.html', context)

def deleteProduct(request, pk):
    product = EXODUSProduct.objects.get(id=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('/TheEXODUS/products')

    return render(request, 'EXODUS/EXODUSCRM/delete_item.html', {'item':product})



#-------------------(CRUD - CATEGORIES) -------------------

def categories(request):
    categories = EXODUSCategory.objects.all()
    categoryFilter = EXODUSCategoryFilter(request.GET, queryset=categories)
    total_categories = categories.count()
    categories = categoryFilter.qs

    context = {'total_categories': total_categories, 'categories':categories, 'filter': categoryFilter}

    return render(request, 'EXODUS/EXODUSCRM/category.html', context)

def addCategory(request):
    action = 'create'
    name = "Category"
    form = EXODUSCategoriesForm()
    if request.method == 'POST':
        form = EXODUSCategoriesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/TheEXODUS/categories/')

    context =  {'action':action, 'form':form, 'name':name }
    return render(request, 'EXODUS/EXODUSCRM/order_form.html', context)

def updateCategory(request, pk):
    action = 'update'
    category = EXODUSCategory.objects.get(id=pk)
    name = category.category_name
    form = EXODUSCategoriesForm(instance=category)

    if request.method == 'POST':
        form = EXODUSCategoriesForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('/TheEXODUS/categories/')

    context =  {'action':action, 'form':form, 'name':name }
    return render(request, 'EXODUS/EXODUSCRM/order_form.html', context)

def deleteCategory(request, pk):
    category = EXODUSCategory.objects.get(id=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('/TheEXODUS/categories/')

    return render(request, 'EXODUS/EXODUSCRM/delete_item.html', {'item':category})
