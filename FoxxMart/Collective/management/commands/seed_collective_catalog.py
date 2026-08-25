from django.core.management.base import BaseCommand
from django.db import transaction
from pathlib import Path

from Collective.models import CollectiveCategory, CollectiveOrderItem, CollectiveProduct, CollectiveProductVariant


def cutout_image(filename):
    """Return the transparent storefront cutout that accompanies an original asset."""
    return f'collective_product/cutouts/{Path(filename).stem}-cutout.png'


CATALOG = (
    {
        'name': 'Biggie & Tupac Adidas Tee',
        'category': 'T-Shirts',
        'description': '100% cotton. Premium-quality, all-day soft, built with real weight — you can feel the difference the second it lands on your shoulders. Biggie and Tupac front-and-centre, with a print made to stay sharp for years. “Stay far from timid.” — The Notorious B.I.G.',
        'price': '650.00',
        'images': ('TBBShirt.png', 'The-Tupac-and-Biggie-Murders-Adidas-Logo-Shirt-Hoodie.jpg'),
        'variants': (('Black', 'TBBShirt.png'),),
    },
    {
        'name': 'Tupac Adidas Tee',
        'category': 'T-Shirts',
        'description': '100% cotton and premium from collar to hem. This is the kind of tee that feels different: soft, solid and street-ready, with a Tupac graphic print built to ride for years. “Reality is wrong. Dreams are for real.” — Tupac Shakur.',
        'price': '650.00',
        'images': ('TWShirt.png', 'whiteshirt.jpg', 'greyshirt.jpg'),
        'variants': (('White', 'TWShirt.png'), ('Grey', 'greyshirt.jpg')),
    },
    {
        'name': 'Tupac & Biggie Murders Hoodie',
        'category': 'Hoodies',
        'description': 'Thick, warm and sturdy — a heavyweight hoodie for cold streets and long nights. The Tupac and Biggie graphic is printed to last for years, so the statement stays loud after the season changes. “Sky’s the limit.” — The Notorious B.I.G.',
        'price': '1100.00',
        'images': ('blackmurdershoodie.jpg', 'whitemurdershoodie.jpg', 'navymurdershoodie.jpg', 'Murders1.png'),
        'variants': (('Black', 'blackmurdershoodie.jpg'), ('White', 'whitemurdershoodie.jpg'), ('Navy', 'navymurdershoodie.jpg')),
    },
    {
        'name': 'Tupac Adidas Hoodie',
        'category': 'Hoodies',
        'description': 'A thick, warm, sturdy hoodie with a premium feel and a Tupac graphic that holds its ground. Built for the block, the studio and everywhere the temperature drops; the durable print is made to last for years. “Reality is wrong. Dreams are for real.” — Tupac Shakur.',
        'price': '1050.00',
        'images': ('blackhoodie.jpg', 'whitehoodie.jpg', 'navyhoodie.jpg', 'TWHoodie.png'),
        'variants': (('Black', 'blackhoodie.jpg'), ('White', 'whitehoodie.jpg'), ('Navy', 'navyhoodie.jpg')),
    },
    {
        'name': 'Tupac Adidas Sweater',
        'category': 'Sweaters',
        'description': 'Premium crewneck energy with a heavyweight feel, clean structure and bold Tupac artwork. Comfortable enough to live in, solid enough to keep its shape, with a long-lasting print that stays fresh for years. “Stay far from timid.” — The Notorious B.I.G.',
        'price': '900.00',
        'images': ('blacksweater.jpg', 'redsweater.png', 'navysweater.jpg', 'TWSweater.png'),
        'variants': (('Black', 'blacksweater.jpg'), ('Red', 'redsweater.png'), ('Navy', 'navysweater.jpg')),
    },
)


class Command(BaseCommand):
    help = 'Replace the Collective catalog with the Tupac and Biggie apparel collection.'

    @transaction.atomic
    def handle(self, *args, **options):
        # This command intentionally replaces only catalog rows; past orders remain intact.
        # Retired products must not remain in active carts after a catalog replacement.
        CollectiveOrderItem.objects.filter(product__isnull=False, order__status='Pending').delete()
        CollectiveProduct.objects.all().delete()
        for item in CATALOG:
            category, _ = CollectiveCategory.objects.get_or_create(category_name=item['category'])
            image_names = item['images']
            product = CollectiveProduct.objects.create(
                name=item['name'],
                description=item['description'],
                price=item['price'],
                stock=len(item['variants']) * 10,
                category=category,
                image1=cutout_image(image_names[0]),
                image2=cutout_image(image_names[1]) if len(image_names) > 1 else '',
                image3=cutout_image(image_names[2]) if len(image_names) > 2 else '',
                image4=cutout_image(image_names[3]) if len(image_names) > 3 else '',
            )
            CollectiveProductVariant.objects.bulk_create([
                CollectiveProductVariant(
                    product=product,
                    color=color,
                    image=cutout_image(image_name),
                    stock=10,
                )
                for color, image_name in item['variants']
            ])
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(CATALOG)} Collective products.'))
