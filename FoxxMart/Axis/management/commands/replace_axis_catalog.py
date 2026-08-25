from django.core.management.base import BaseCommand
from django.db import transaction

from Axis.models import Product


CATALOG = (
    ('Axis Form One', 'Precision desktop resin printing in a compact amber enclosure.', 'A refined resin printer for detailed prototypes, presentation models and small-batch production.', '45999.00', 6, ('Resin', 'Precision')),
    ('Axis Forge One', 'A versatile compact FDM printer for everyday prototyping.', 'A dependable desktop FDM system with a rigid frame and a practical, maker-friendly workflow.', '18999.00', 12, ('FDM', 'Desktop')),
    ('Axis Forge XL', 'Large-format FDM production with an enclosed build chamber.', 'A spacious, controlled FDM system for functional parts, jigs and ambitious one-piece prototypes.', '54999.00', 4, ('FDM', 'Large Format')),
    ('Axis Resin Mini', 'Small-footprint resin precision for desks and studios.', 'A clean, compact resin platform for smooth, high-detail prototypes with minimal bench space.', '23999.00', 10, ('Resin', 'Compact')),
    ('Axis Resin Pro', 'Professional resin printing with a controlled enclosed workflow.', 'A premium production-ready resin printer built for designers who value detail, repeatability and finish.', '74999.00', 5, ('Resin', 'Professional')),
    ('Axis Resin Max', 'Large-format resin printing for ambitious detailed work.', 'A wide-format resin platform for presentation pieces, production parts and larger precision models.', '129999.00', 3, ('Resin', 'Large Format')),
    ('Axis Metal Studio', 'Office-ready metal additive manufacturing.', 'A compact metal printing system for engineering prototypes, tooling concepts and specialised low-volume parts.', '349999.00', 1, ('Metal', 'Professional')),
    ('Axis Carbon CF', 'Technical FDM printing for carbon-fibre composites.', 'A high-performance enclosed printer engineered for strong, lightweight composite functional parts.', '89999.00', 4, ('FDM', 'Composite')),
    ('Axis BioPrint S', 'A precise laboratory platform for controlled experimental fabrication.', 'A clean research-grade printing instrument designed for educational and laboratory fabrication workflows.', '159999.00', 2, ('Research', 'Professional')),
    ('Axis Dental DLP', 'Fine-detail resin output for specialised dental workflows.', 'A detailed DLP system that produces accurate smooth models for labs and specialist fabrication teams.', '99999.00', 5, ('Resin', 'Medical')),
    ('Axis Maker Lab', 'An approachable modular printer for education and making.', 'A durable open-frame system that helps classrooms and makerspaces turn ideas into physical prototypes.', '14999.00', 16, ('FDM', 'Education')),
    ('Axis SLS Compact', 'Professional nylon part production in a compact footprint.', 'A powder-based additive manufacturing system for robust functional components and efficient low-volume production.', '279999.00', 2, ('SLS', 'Production')),
    ('Axis Ceramic One', 'Ceramic extrusion for expressive functional objects.', 'A specialised fabrication platform for studios exploring ceramic forms, small runs and material-driven work.', '67999.00', 5, ('Ceramic', 'Studio')),
    ('Axis MicroFab', 'Microscale resin precision for research and intricate parts.', 'A compact high-resolution instrument for miniature prototypes, research models and intricate fabrication.', '119999.00', 3, ('Resin', 'Precision')),
    ('Axis Hybrid X', 'FDM printing and CNC milling in one flexible workstation.', 'A capable hybrid fabrication unit that lets workshops print, refine and prototype within a single system.', '139999.00', 3, ('Hybrid', 'Professional')),
)


class Command(BaseCommand):
    help = 'Replace the Axis catalogue with the generated 15-product collection.'

    @transaction.atomic
    def handle(self, *args, **options):
        Product.objects.all().delete()
        for index, (name, short_desc, description, price, stock, tags) in enumerate(CATALOG, start=1):
            slug = name.lower().replace(' ', '-').replace('axis-', 'axis-')
            images = {f'image{view}': f'Axis_generated/{slug}/view-{view}.png' for view in range(1, 6)}
            product = Product.objects.create(
                name=name,
                short_desc=short_desc,
                description1=description,
                price=price,
                stock=stock,
                **images,
            )
            product.tags.add(*tags)
        self.stdout.write(self.style.SUCCESS('Replaced Axis catalogue with 15 generated products.'))
