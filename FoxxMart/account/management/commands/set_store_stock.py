from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from Axis.models import Product as AxisProduct
from Collective.models import CollectiveProduct, CollectiveProductVariant
from EXODUS.models import EXODUSProduct
from GENESIS.models import GENESISProduct


class Command(BaseCommand):
    help = 'Set every product stock level in the Foxx Mart storefronts to one quantity.'

    def add_arguments(self, parser):
        parser.add_argument('--quantity', type=int, default=100, help='Stock quantity to apply (default: 100).')

    def handle(self, *args, **options):
        quantity = options['quantity']
        if quantity < 0:
            raise CommandError('Stock quantity must be zero or greater.')

        models = (AxisProduct, CollectiveProduct, CollectiveProductVariant, EXODUSProduct, GENESISProduct)
        with transaction.atomic():
            updated = {model._meta.label: model.objects.update(stock=quantity) for model in models}

        summary = ', '.join(f'{label} ({count})' for label, count in updated.items())
        self.stdout.write(self.style.SUCCESS(f'Updated stock to {quantity}: {summary}'))
