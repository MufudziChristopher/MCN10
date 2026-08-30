from django.shortcuts import render, redirect
from django.conf import settings
from Axis.models import Order as AxisOrder
from Collective.models import CollectiveOrder
from EXODUS.models import EXODUSOrder
from GENESIS.models import GENESISOrder

# Create your views here.
# Create your views here.
def home(request):

    context = {}
    return render(request, 'home/index.html', context)


def mall(request):
    """FoxxMart's mall front: a directory of the stores available today."""
    stores = [
        {
            'name': '3rd Axis',
            'tagline': 'Additive manufacturing',
            'url_name': 'Axis:store',
            'image': 'Axis_product/form-32xpng__1354x0_q85_subsampling-2png.png',
            'accent': '#ff6500',
            'customer_attr': 'axiscustomer',
            'order_model': AxisOrder,
        },
        {
            'name': 'The Collective',
            'tagline': 'Limited-edition apparel',
            'url_name': 'Collective:store',
            'image': 'collective_product/TWHoodie_WDN3gOu.jpg',
            'accent': '#cd0000',
            'customer_attr': 'collectivecustomer',
            'order_model': CollectiveOrder,
        },
        {
            'name': 'Genesis',
            'tagline': 'Robotic arm systems',
            'url_name': 'GENESIS:store',
            'image': 'GENESIS_product/85ca4b13fd05b8e959f0668ffdca96cf.jpg',
            'accent': '#63e6be',
            'customer_attr': 'genesiscustomer',
            'order_model': GENESISOrder,
        },
        {
            'name': 'Exodus',
            'tagline': 'Objects for the next chapter',
            'url_name': 'EXODUS:store',
            'image': 'EXODUS_product/form-3-l-hero-2-x2x_png__1354x0_q85_subs.png',
            'accent': '#a78bfa',
            'customer_attr': 'exoduscustomer',
            'order_model': EXODUSOrder,
        },
        {
            'name': 'Bomkazi Designs',
            'tagline': 'Contemporary African fashion',
            'url_name': 'Projects:bomkazi',
            'image': 'Bomkazi/cover.png',
            'accent': '#d65c82',
        },
    ]

    for store in stores:
        cart_count = 0
        if request.user.is_authenticated and store.get('customer_attr'):
            customer = getattr(request.user, store['customer_attr'], None)
            if customer:
                order = store['order_model'].objects.filter(customer=customer, status='Pending').order_by('-id').first()
                cart_count = order.get_cart_items if order else 0
        store['cart_count'] = cart_count

    return render(request, 'home/mall.html', {'stores': stores, 'media_url': settings.MEDIA_URL})

def contact(request):
    if request.method == 'POST':
        message = request.POST['message']
        if request.user.is_authenticated:
            name = request.user.first_name + request.user.last_name
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
        return redirect('home:home')

    return render(request, 'home/contact.html', {})

def profile(request):
    if request.user.is_authenticated:

        return render(request, 'home/profile.html', {})
    else:
        return redirect('home:home')



def edit_profile(request):
    if request.user.is_authenticated:
        return render(request, 'home/edit_profile.html', context)

    else:
        return redirect('account:login')
