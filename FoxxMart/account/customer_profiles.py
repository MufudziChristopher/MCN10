"""Helpers for linking existing accounts to their storefront customer records."""

from Axis.models import AxisCustomer


def get_store_customer(user, customer_model):
    """Return a storefront customer record for ``user``, creating one if needed.

    Some accounts predate the storefront profile created during registration.  Reuse
    an unassigned record with the same email before creating a new one so those
    accounts can still see their order history.
    """
    customer = customer_model.objects.filter(user=user).first()
    if customer:
        return customer

    customer = customer_model.objects.filter(email=user.email).first()
    if customer and customer.user_id is None:
        customer.user = user
        customer.save(update_fields=['user'])
        return customer

    return customer_model.objects.create(user=user, email=user.email)


def get_axis_customer(user):
    """Return the 3rd Axis customer record for ``user``."""
    return get_store_customer(user, AxisCustomer)
