from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse

from .models import StoreAccess


def store_access_required(store_slug):
    """Require a signed-in shopper with access to the requested storefront."""
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), 'account:login')
            if request.user.is_superuser or StoreAccess.objects.filter(
                user=request.user, store_slug=store_slug
            ).exists():
                return view(request, *args, **kwargs)

            messages.info(request, 'Your current package does not include this store.')
            store_urls = {
                'axis': 'Axis:store',
                'exodus': 'EXODUS:store',
                'genesis': 'GENESIS:store',
                'collective': 'Collective:store',
            }
            return redirect(reverse(store_urls[store_slug]))
        return wrapped
    return decorator
