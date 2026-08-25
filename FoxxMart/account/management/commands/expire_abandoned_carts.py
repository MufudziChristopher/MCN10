from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from Axis.models import Order as AxisOrder
from Collective.models import CollectiveOrder as CollectiveOrder
from EXODUS.models import EXODUSOrder
from GENESIS.models import GENESISOrder


class Command(BaseCommand):
    help = 'Email and clear pending carts older than two hours.'

    stores = (
        ('3rd Axis', AxisOrder, 'orderitem_set'),
        ('The Collective', CollectiveOrder, 'collectiveorderitem_set'),
        ('Genesis', GENESISOrder, 'genesisorderitem_set'),
        ('Exodus', EXODUSOrder, 'exodusorderitem_set'),
    )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=2)
        expired = 0
        for store_name, Order, related_name in self.stores:
            for order in Order.objects.filter(status='Pending', date_ordered__lte=cutoff).select_related('customer__user'):
                items = list(getattr(order, related_name).select_related('product').filter(product__isnull=False))
                if not items:
                    continue
                customer = order.customer
                email = getattr(getattr(customer, 'user', None), 'email', '') or getattr(customer, 'email', '')
                if not email:
                    continue
                message = f"You still have {sum(item.quantity for item in items)} item(s) waiting in your {store_name} cart. It has now been cleared, but you can add them again whenever you are ready."
                if not send_mail('You forgot something at FoxxMart', message, None, [email], fail_silently=True):
                    self.stderr.write(f'Email was not accepted for {email}; cart retained.')
                    continue
                with transaction.atomic():
                    for item in items:
                        item.product.stock += item.quantity
                        item.product.save(update_fields=['stock'])
                    getattr(order, related_name).all().delete()
                expired += 1
        self.stdout.write(self.style.SUCCESS(f'Expired {expired} abandoned cart(s).'))
