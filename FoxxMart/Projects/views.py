from django.shortcuts import render
from django.conf import settings

# Create your views here.

def IDACA(request):

    return render(request, 'Projects/idaca.html', {})

def gallery(request):

    return render(request, 'Projects/gallery.html', {})


    

def bc(request):

    return render(request, 'Projects/bc.html', {})




def africanus(request):

    return render(request, 'Projects/africanus.html', {})


def about(request):

    return render(request, 'Projects/about.html', {})

def services(request):

    return render(request, 'Projects/services.html', {})

def contact(request):

    return render(request, 'Projects/contact.html', {})


def transcendcopy(request):
    return render(request, 'Projects/transcendcopy.html', {})


def jay_cast(request):
    return render(request, 'Projects/jay_cast.html', {})


def bomkazi(request):
    """A focused portfolio boutique for the Bomkazi Designs collection."""
    designs = [
        {
            'name': 'Ighorakazi',
            'image': 'bomkazi/images/Ighorakazi1.jpg',
            'description': 'An expressive silhouette that balances structure and movement.',
        },
        {
            'name': 'Imbali',
            'image': 'bomkazi/images/Imbali.jpg',
            'description': 'A considered statement piece made for celebration and presence.',
        },
        {
            'name': 'Nobomi',
            'image': 'bomkazi/images/Nobomi .jpg',
            'description': 'Soft tailoring and confident detail for an elevated everyday look.',
        },
        {
            'name': 'Qhama Fit',
            'image': 'bomkazi/images/QhamaFit1.jpg',
            'description': 'A refined fit designed to feel effortless from day into evening.',
        },
        {
            'name': 'Ubhelukazi',
            'image': 'bomkazi/images/Ubhelukazi .jpg',
            'description': 'A bold, contemporary design rooted in personal expression.',
        },
    ]
    return render(request, 'Projects/bomkazi.html', {
        'designs': designs,
        'media_url': settings.MEDIA_URL,
    })
