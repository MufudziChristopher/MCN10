from django.core.management.base import BaseCommand
from django.db import transaction

from Axis.models import Product


# Shared tags are intentional: they form the useful, multi-product filter groups
# shown on the Axis storefront.
CATALOG = (
    ('Axis PLA Matte Black', 'A low-gloss, reliable PLA for refined prototypes and display pieces.', 'A 1 kg spool of matte black PLA with smooth layer definition and an understated finish. It is an easy-printing choice for prototypes, fixtures and presentation models.', '495.00', 48, 'Axis_components/filament/axis-pla-matte-black.png', ('Filament', 'PLA', 'Matte', 'Black')),
    ('Axis PLA Signal Red', 'A saturated red PLA for visible prototypes and crisp display work.', 'A 1 kg spool of signal-red PLA designed for dependable everyday printing. Its strong colour and predictable flow make it ideal for concept models, labels and workshop parts.', '495.00', 42, 'Axis_components/filament/axis-pla-signal-red.png', ('Filament', 'PLA', 'Red')),
    ('Axis PLA Sapphire Blue', 'A vivid blue PLA that balances bold colour with easy processing.', 'A 1 kg spool of sapphire-blue PLA with stable extrusion and clean surface detail. Use it for visual mock-ups, educational builds and colourful functional prints.', '495.00', 40, 'Axis_components/filament/axis-pla-sapphire-blue.png', ('Filament', 'PLA', 'Blue')),
    ('Axis PETG Smoke Clear', 'Tough, translucent PETG with a restrained smoke tint.', 'A 1 kg spool of smoke-clear PETG for components that need more durability than standard PLA. The translucent finish suits enclosures, guards and practical display parts.', '575.00', 36, 'Axis_components/filament/axis-petg-smoke-clear.png', ('Filament', 'PETG', 'Transparent')),
    ('Axis Nylon CF Graphite', 'Carbon-fibre nylon for rigid, lightweight engineering parts.', 'A 1 kg spool of graphite nylon reinforced with carbon fibre. It delivers high stiffness and a technical matte finish for brackets, tooling and performance-driven components.', '1295.00', 18, 'Axis_components/filament/axis-nylon-cf-graphite.png', ('Filament', 'Nylon', 'Carbon Fibre', 'Engineering')),
    ('Axis ASA Arctic White', 'UV-stable ASA for clean outdoor and architectural prints.', 'A 1 kg spool of arctic-white ASA with weather resistance for parts used in sunlight. It is suited to outdoor housings, mounts, signage and durable functional prototypes.', '690.00', 32, 'Axis_components/filament/axis-asa-arctic-white.png', ('Filament', 'ASA', 'UV Resistant', 'White')),
    ('Axis TPU Flex Lime', 'Bright flexible TPU for impact-resistant, soft-touch components.', 'A 1 kg spool of lime-green TPU formulated for controlled flexible printing. Create grips, gaskets, bumpers and protective parts with resilient, elastic performance.', '790.00', 25, 'Axis_components/filament/axis-tpu-flex-lime.png', ('Filament', 'TPU', 'Flexible', 'Green')),
    ('Axis PETG Safety Orange', 'High-visibility PETG for robust workshop and safety components.', 'A 1 kg spool of safety-orange PETG combining strong colour with PETG durability. It is an excellent fit for guards, tools, brackets and visible operational prototypes.', '575.00', 30, 'Axis_components/filament/axis-petg-safety-orange.png', ('Filament', 'PETG', 'Orange')),
    ('Axis PLA Marble', 'A flecked marble PLA with a natural, premium surface effect.', 'A 1 kg spool of white PLA with subtle charcoal flecks. It produces distinctive presentation pieces, decor, props and prototypes without requiring complex finishing.', '650.00', 24, 'Axis_components/filament/axis-pla-marble.png', ('Filament', 'PLA', 'Specialty')),
    ('Axis ABS Cobalt', 'A robust cobalt ABS for workshop-ready functional parts.', 'A 1 kg spool of cobalt-blue ABS engineered for parts that benefit from heat resistance and toughness. Best for enclosures, jigs and durable mechanical prototypes.', '620.00', 28, 'Axis_components/filament/axis-abs-cobalt.png', ('Filament', 'ABS', 'Blue')),
    ('Axis MicroBoard Core 32', 'A compact 32-bit motion-control board for focused printer builds.', 'A compact controller board with responsive 32-bit motion control, practical expansion headers and a clean layout for reliable single-extruder printer projects.', '1699.00', 20, 'Axis_components/microboards/axis-microboard-core-32.png', ('Microboard', 'Electronics', '32-bit', 'Core')),
    ('Axis MicroBoard WiFi Motion', 'Network-ready controller hardware for connected printer control.', 'A Wi-Fi enabled 32-bit printer controller board for remote monitoring and modern connected workflows. Its compact form suits upgrades and custom desktop machines.', '2199.00', 15, 'Axis_components/microboards/axis-microboard-wifi-motion.png', ('Microboard', 'Electronics', 'WiFi', '32-bit')),
    ('Axis MicroBoard Duo Drive', 'A dual-extruder controller designed for more ambitious material setups.', 'A feature-rich 32-bit control board with extra motor and heater connections for dual-extruder systems. It supports controlled multi-material and support-material workflows.', '2799.00', 10, 'Axis_components/microboards/axis-microboard-duo-drive.png', ('Microboard', 'Electronics', 'Dual Extruder', '32-bit')),
    ('Axis MicroBoard Silent Motion', 'A quiet controller platform with integrated silent-driver cooling.', 'A motion-control board built around quiet stepper-driver operation and tidy thermal management. A strong choice for studio printers and low-noise desktop upgrades.', '2499.00', 12, 'Axis_components/microboards/axis-microboard-silent-motion.png', ('Microboard', 'Electronics', 'Silent Drivers', '32-bit')),
    ('Axis MicroBoard CAN Pro', 'A rugged CAN-bus control board for industrial printer wiring.', 'An industrial-focused controller board with robust connectors and CAN-bus capability for distributed machine electronics. Designed for durable, serviceable fabrication systems.', '3299.00', 8, 'Axis_components/microboards/axis-microboard-can-pro.png', ('Microboard', 'Electronics', 'CAN Bus', 'Industrial')),
    ('Axis Standard Brass Hotend', 'A precise 0.4 mm brass hotend for everyday materials.', 'A compact brass 0.4 mm hotend that delivers clean, predictable extrusion with common PLA, PETG and ABS filaments. A dependable replacement or upgrade component.', '899.00', 35, 'Axis_components/extruders/axis-standard-brass-hotend.png', ('Extruder', 'Hotend', 'Brass', '0.4mm')),
    ('Axis Hardened Steel Hotend', 'A wear-resistant hotend for abrasive and filled filaments.', 'A hardened-steel hotend assembly made for carbon-fibre, glow and other abrasive materials. It provides durable nozzle performance while retaining controlled detail.', '1199.00', 26, 'Axis_components/extruders/axis-hardened-steel-hotend.png', ('Extruder', 'Hotend', 'Hardened Steel', 'Abrasive Filament')),
    ('Axis High Flow Volcano Head', 'A long-melt-zone hotend for fast, high-volume extrusion.', 'A high-flow 0.6 mm volcano-style hotend that increases melt capacity for larger nozzles and faster builds. Ideal for production parts, strong perimeters and tall layers.', '1499.00', 20, 'Axis_components/extruders/axis-high-flow-volcano-head.png', ('Extruder', 'Hotend', 'High Flow', '0.6mm')),
    ('Axis Dual Drive Extruder', 'A dual-gear extruder for confident, even filament feeding.', 'A direct dual-drive extruder with two drive gears for balanced filament grip. It improves consistency with flexible materials and is well suited to precision desktop machines.', '1799.00', 16, 'Axis_components/extruders/axis-dual-drive-extruder.png', ('Extruder', 'Dual Drive', 'Hotend', 'Precision')),
    ('Axis Pellet Feed Extruder', 'An industrial pellet-feed extruder for high-throughput systems.', 'A rugged pellet-feed extruder assembly designed for large-format and industrial material handling. Its robust mechanism supports efficient high-volume extrusion workflows.', '3999.00', 6, 'Axis_components/extruders/axis-pellet-feed-extruder.png', ('Extruder', 'Pellet', 'Industrial', 'Hotend')),
)


class Command(BaseCommand):
    help = 'Add or refresh the Axis filament, microboard and extruder catalogue.'

    @transaction.atomic
    def handle(self, *args, **options):
        for name, short_desc, description, price, stock, image, tags in CATALOG:
            product, _ = Product.objects.update_or_create(
                name=name,
                defaults={
                    'short_desc': short_desc,
                    'description1': description,
                    'price': price,
                    'stock': stock,
                    'image1': image,
                },
            )
            product.tags.set(tags)
        self.stdout.write(self.style.SUCCESS('Seeded 20 Axis components with shared filter tags.'))
