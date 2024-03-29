import json
from .models import *

def cookieCart(request):

    #Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES['cart'])
        print('CART:', cart)

    except:
        cart = {}
        print('CART:', cart)

    items = []
    order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            print("try successful")
            cartItems += cart[i]['quantity']

            product = EXODUSProduct.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'id':product.id,
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL1':product.imageURL1,
                    },
                'quantity':cart[i]['quantity'],
                'digital':product.digital,
                'get_total':total,
                }

            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'cartItems':cartItems ,'order':order, 'items':items}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.exoduscustomer
        order, created = EXODUSOrder.objects.get_or_create(customer=customer, status="Pending")
        items = order.exodusorderitem_set.all()
        cartItems = order.get_cart_items
    else:
        print("Sent to cookie Cart")
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']


    return {'cartItems':cartItems ,'order':order, 'items':items}


def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = EXODUSCustomer.objects.get_or_create(
            email=email,
            )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        status="Pending",
        )

    for item in items:
        product = EXODUSEXODUSProduct.objects.get(id=item['id'])
        orderItem = EXODUSEXODUSOrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )
    return customer, order
