from django.core.management.base import BaseCommand
from django.db import transaction

from GENESIS.models import GENESISProduct


CATALOG = (
    ('Genesis Reach 6', 'Compact six-axis collaboration for precise assembly.', 'A flexible compact robot arm for bench automation, inspection and repeatable assembly.', '189999.00', 8),
    ('Genesis Reach 12', 'Mid-payload precision for production cells.', 'A robust six-axis arm that brings smooth, accurate automation to growing production teams.', '279999.00', 6),
    ('Genesis Reach 20', 'Heavy-payload industrial handling at scale.', 'A high-reach robotic arm engineered for demanding material handling and production tasks.', '449999.00', 3),
    ('Genesis Weld Arc', 'Automated arc welding with consistent repeatability.', 'A specialist welding arm that helps production teams create reliable, repeatable welds.', '599999.00', 2),
    ('Genesis Pick Pro', 'Fast pick-and-place automation for modern workflows.', 'A rapid handling arm with vacuum tooling for organised packing and light industrial picking.', '339999.00', 5),
    ('Genesis Inspect Vision', 'Machine-vision inspection in a flexible automation cell.', 'A camera-equipped robotic arm for repeatable inspection, measurement and quality workflows.', '319999.00', 4),
    ('Genesis Pallet 30', 'High-reach palletising for heavier production loads.', 'A powerful robotic arm designed for efficient palletising and dependable end-of-line automation.', '749999.00', 2),
    ('Genesis Lab Assist', 'Laboratory automation in a precise compact platform.', 'A careful, controlled automation arm for research, sample handling and laboratory workflows.', '389999.00', 3),
    ('Genesis CNC Load', 'Reliable CNC machine tending around the clock.', 'A rugged gripper-equipped arm that automates machine loading and repeatable part handling.', '429999.00', 3),
    ('Genesis Cleanroom 8', 'Sealed precision automation for controlled environments.', 'A smooth, cleanroom-oriented robot arm built for consistent controlled-environment operation.', '469999.00', 2),
    ('Genesis Forge 16', 'Machining assistance for automated fabrication cells.', 'A robust industrial arm with tooling designed to complement automated machining operations.', '579999.00', 2),
    ('Genesis Food Safe', 'Hygienic robotic handling for food operations.', 'A smooth, wash-down-friendly automation arm for hygienic handling and packaging workflows.', '529999.00', 3),
    ('Genesis Mobile Dock', 'Flexible automation that can move between workstations.', 'A compact mobile robot platform that brings programmable manipulation wherever it is needed.', '649999.00', 2),
    ('Genesis Micro 3', 'Microscale precision for electronics and detailed work.', 'A compact high-precision arm for delicate assembly, electronics and research applications.', '159999.00', 7),
    ('Genesis Duo Cell', 'Coordinated dual-arm automation for complex tasks.', 'A paired robotic workcell that enables synchronised handling, assembly and advanced automation.', '899999.00', 1),
)


class Command(BaseCommand):
    help = 'Replace the Genesis catalogue with 15 generated robotic-arm products.'

    @transaction.atomic
    def handle(self, *args, **options):
        GENESISProduct.objects.all().delete()
        for name, short_desc, description, price, stock in CATALOG:
            slug = name.lower().replace(' ', '-')
            images = {f'image{view}': f'GENESIS_generated/{slug}/view-{view}.png' for view in range(1, 6)}
            GENESISProduct.objects.create(name=name, short_desc=short_desc, description1=description, price=price, stock=stock, **images)
        self.stdout.write(self.style.SUCCESS('Replaced Genesis catalogue with 15 generated robotic arms.'))
