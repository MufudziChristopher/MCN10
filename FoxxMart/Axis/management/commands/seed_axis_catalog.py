from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from Axis.models import Product


CATALOG = (
    {
        "name": "Creality CR-M4 Large Format",
        "short_desc": "A dependable large-format FDM printer for full-size prototypes and production parts.",
        "description": "The CR-M4 gives studios and growing workshops the generous build volume needed for larger models, fixtures and multi-part jobs. Its rigid frame, remote monitoring features and straightforward material workflow make it a practical choice for reliable day-to-day printing.",
        "price": "37999.00",
        "stock": 6,
        "tags": ("FDM", "Large Format", "Professional"),
        "images": (
            "main_product/CR-M4LagerVolume3DPrinter_1.jpg",
            "main_product/CR-M4LagerVolume3DPrinter_BuildSize.jpg",
            "main_product/CR-M4LagerVolume3DPrinter_MoreDetail.jpg",
            "main_product/CR-M4LagerVolume3DPrinter_StablePrinting.jpg",
            "main_product/3d-printing-3d-printers-makerbot-printer.jpg",
        ),
    },
    {
        "name": "Creality CR-10 Mini",
        "short_desc": "A compact, approachable FDM printer for makers learning and refining their workflow.",
        "description": "The CR-10 Mini delivers the familiar, open-frame Creality experience in a footprint that fits comfortably on a desk. It is an excellent entry point for makers who need dependable PLA and PETG printing without giving up useful build volume.",
        "price": "8999.00",
        "stock": 14,
        "tags": ("FDM", "Beginner", "Compact"),
        "images": (
            "main_product/CREALITY_CR-10_MINI_3D_PRINTER.png",
            "main_product/CREALITY_CR-10_MINI_3D_PRINTER2.png",
            "main_product/CREALITY_CR-10_MINI_3D_PRINTER2_11BbO42.png",
            "main_product/CREALITY_CR-10_MINI_3D_PRINTER23.png",
            "main_product/CREALITY_CR-10_MINI_3D_PRINTER23_7hw9h8x.png",
        ),
    },
    {
        "name": "Creality CR-10 Max",
        "short_desc": "A large-volume FDM printer designed for ambitious prototypes and functional parts.",
        "description": "The CR-10 Max combines a spacious build area with automatic levelling and a stable triangular frame. It suits designers and small production teams that want to print one-piece enclosures, display models and batches of functional components.",
        "price": "24999.00",
        "stock": 8,
        "tags": ("FDM", "Large Format", "Professional"),
        "images": (
            "main_product/CREALITY_CR-10_MAX_3D_PRINTER.png",
            "main_product/CREALITY_CR-10_MAX_3D_PRINTER2.png",
            "main_product/CREALITY_CR-10_MAX_3D_PRINTER3.png",
            "main_product/CREALITY_CR-10_MAX_3D_PRINTER4.png",
            "main_product/CREALITY_CR-10_MAX_3D_PRINTER4_ZwMdL3e.png",
        ),
    },
    {
        "name": "Creality CR-10 S5",
        "short_desc": "An extra-large FDM platform built for sizeable engineering and display prints.",
        "description": "The CR-10 S5 is made for jobs that outgrow standard desktop printers. Its expansive build area makes it well suited to architectural models, workshop jigs, props and other substantial parts that benefit from being printed in one piece.",
        "price": "43999.00",
        "stock": 4,
        "tags": ("FDM", "Large Format", "Production"),
        "images": (
            "main_product/CREALITY_CR-10_S5_3D_PRINTER.png",
            "main_product/CREALITY_CR-10_S5_3D_PRINTER2.png",
            "main_product/CREALITY_CR-10_S5_3D_PRINTER3.png",
            "main_product/CREALITY_CR-10_S5_3D_PRINTER4.png",
            "main_product/CREALITY_CR-10_S5_3D_PRINTER_8j5JAfQ.png",
        ),
    },
    {
        "name": "MakerBot Method X",
        "short_desc": "An enclosed professional FDM printer for precise, engineering-grade desktop production.",
        "description": "The Method X brings a controlled, enclosed print environment to the desktop for teams creating accurate functional prototypes. Its refined material handling and dependable workflow make it a strong fit for product development, classroom labs and internal tooling.",
        "price": "12499.00",
        "stock": 7,
        "tags": ("FDM", "Professional", "Compact"),
        "images": (
            "main_product/3d-printing-3d-printers-makerbot-printer.jpg",
            "main_product/3d-printing-3d-printers-makerbot-printer_Ge5skUe.jpg",
            "main_product/3d-printing-3d-printers-makerbot-printer_ZIghV0Q.jpg",
            "main_product/3d-printing-3d-printers-makerbot-printer_ZIghV0Q_l9KjsK8.jpg",
            "main_product/3d-printing-3d-printers-makerbot-printer_py9Tk6K.jpg",
        ),
    },
    {
        "name": "Formlabs Form 3+",
        "short_desc": "A precision SLA printer for beautifully detailed prototypes and end-use parts.",
        "description": "The Form 3+ gives professionals an accessible route to smooth, detailed resin prints. Its low-force stereolithography process is ideal for product prototypes, presentation models, fixtures and small-batch components where surface finish matters.",
        "price": "49999.00",
        "stock": 5,
        "tags": ("Resin", "Professional", "Precision"),
        "images": (
            "Axis_product/form-32xpng__1354x0_q85_subsampling-2png.png",
            "Axis_product/f3.png",
            "Axis_product/f3 (1).png",
            "Axis_product/f3_WiCNiPy.png",
            "Axis_product/form3_grow_businesspng__1354x0_q85_subsa.png",
        ),
    },
    {
        "name": "Formlabs Form 3B+",
        "short_desc": "A validated dental and medical resin printer with consistently fine detail.",
        "description": "The Form 3B+ is designed for dental, medical and biocompatible resin workflows. It combines a compact footprint with exceptional surface quality, making it well suited to models, appliances, surgical planning and specialist fabrication.",
        "price": "69999.00",
        "stock": 3,
        "tags": ("Resin", "Medical", "Professional"),
        "images": (
            "Axis_product/Form_3B_No_Background.png",
            "Axis_product/next_generation_3b_jpg__1354x0_q85_subsa.jpg",
            "Axis_product/Website_image_3_No_background.png",
            "Axis_product/87ccc0_21af485d2277480e8fa5b167d6646351mv2.jpg",
            "Axis_product/87ccc0_53f21684856f43fcbbeea9caf7d29489mv2.png",
        ),
    },
    {
        "name": "Formlabs Form 3L",
        "short_desc": "A large-format resin printer for production-scale parts with a polished finish.",
        "description": "The Form 3L expands precision resin printing to larger, more ambitious applications. It is a great fit for production runs, life-size prototypes, design validation and high-detail parts that need the surface quality associated with SLA printing.",
        "price": "124999.00",
        "stock": 2,
        "tags": ("Resin", "Large Format", "Professional"),
        "images": (
            "Axis_product/form-3-l-hero-2-x2x_png__1354x0_q85_subs.png",
            "Axis_product/lpus_png__1184x0_q85_subsampling-2.png",
            "Axis_product/website_page_1_PNG.png",
            "Axis_product/87ccc0_63b0fb460374442eacaacd821f404914mv2_d_2918_1218_s_2.jpg",
            "Axis_product/87ccc0_c9d9cdc836bc4242b5b5168fa6792f2dmv2_d_2762_1666_s_2.png",
        ),
    },
    {
        "name": "Desktop Metal Studio System 2",
        "short_desc": "An office-friendly metal additive manufacturing system for functional metal parts.",
        "description": "The Studio System 2 makes metal 3D printing more accessible to engineering teams. Its streamlined workflow supports the development of complex metal prototypes, tooling and low-volume components without relying on a traditional machine shop for every iteration.",
        "price": "239999.00",
        "stock": 1,
        "tags": ("Metal", "Production", "Professional"),
        "images": (
            "Axis_product/Studio_System_2_-_Printer_Only.png",
            "Axis_product/Optimized_For_Web_PNG-05132020_medical_sell_366_16x9.png",
            "Axis_product/Capture.png",
            "Axis_product/Capture2.png",
            "Axis_product/87ccc0_bdcae49e382f46c99a0d9578ddc11c8cmv2.jpg",
        ),
    },
    {
        "name": "ZMorph All-in-One",
        "short_desc": "A versatile fabrication workstation for 3D printing, CNC milling and laser work.",
        "description": "The ZMorph All-in-One combines several digital fabrication workflows in one adaptable machine. It is a compelling choice for makerspaces, schools and prototyping teams that want the flexibility to print, mill and engrave in a single workstation.",
        "price": "89999.00",
        "stock": 4,
        "tags": ("FDM", "Multi Tool", "Professional"),
        "images": (
            "Axis_product/zmorph-all-in-one-3d-printers-UqCCSbAIaDU-unsplash.jpg",
            "Axis_product/UserFriendlyHardware_640x480.jpg",
            "Axis_product/noSpecialFacilitiesReq_640x480_2021-01-29-230622.jpg",
            "Axis_product/ST_F3S2_640x480.jpg",
            "Axis_product/87ccc0_bafa0d96fbde4c8f86cb17a1e257f8a8mv2.jpg",
        ),
    },
)


GALLERIES = {
    "fdm-desktop": (
        "Axis_product/emotion-tech-hfoIlAvHuPw-unsplash.jpg",
        "Axis_product/kadir-celep-NwOeoxUY_p0-unsplash.jpg",
        "Axis_product/maria-teneva-xk9htrFBeAw-unsplash.jpg",
        "Axis_product/minku-kang-aCniNTiIFd8-unsplash.jpg",
        "Axis_product/tom-claes-JfUKD6JVeQ0-unsplash.jpg",
    ),
    "fdm-industrial": (
        "Axis_product/87ccc0_ff734140285c4af8a507e103c34f2b57mv2.jpg",
        "Axis_product/emotion-tech-hfoIlAvHuPw-unsplash.jpg",
        "Axis_product/kadir-celep-NwOeoxUY_p0-unsplash.jpg",
        "Axis_product/maria-teneva-xk9htrFBeAw-unsplash.jpg",
        "Axis_product/minku-kang-aCniNTiIFd8-unsplash.jpg",
    ),
    "resin-desktop": (
        "Axis_product/form-32xpng__1354x0_q85_subsampling-2png.png",
        "Axis_product/f3.png",
        "Axis_product/f3 (1).png",
        "Axis_product/f3_WiCNiPy.png",
        "Axis_product/form3_grow_businesspng__1354x0_q85_subsa.png",
    ),
    "resin-medical": (
        "Axis_product/Form_3B_No_Background.png",
        "Axis_product/next_generation_3b_jpg__1354x0_q85_subsa.jpg",
        "Axis_product/Website_image_3_No_background.png",
        "Axis_product/87ccc0_21af485d2277480e8fa5b167d6646351mv2.jpg",
        "Axis_product/87ccc0_53f21684856f43fcbbeea9caf7d29489mv2.png",
    ),
    "resin-large": (
        "Axis_product/form-3-l-hero-2-x2x_png__1354x0_q85_subs.png",
        "Axis_product/lpus_png__1184x0_q85_subsampling-2.png",
        "Axis_product/website_page_1_PNG.png",
        "Axis_product/87ccc0_63b0fb460374442eacaacd821f404914mv2_d_2918_1218_s_2.jpg",
        "Axis_product/87ccc0_c9d9cdc836bc4242b5b5168fa6792f2dmv2_d_2762_1666_s_2.png",
    ),
    "metal-production": (
        "Axis_product/Studio_System_2_-_Printer_Only.png",
        "Axis_product/Optimized_For_Web_PNG-05132020_medical_sell_366_16x9.png",
        "Axis_product/Capture.png",
        "Axis_product/Capture2.png",
        "Axis_product/87ccc0_bdcae49e382f46c99a0d9578ddc11c8cmv2.jpg",
    ),
    "fabrication": (
        "Axis_product/zmorph-all-in-one-3d-printers-UqCCSbAIaDU-unsplash.jpg",
        "Axis_product/UserFriendlyHardware_640x480.jpg",
        "Axis_product/noSpecialFacilitiesReq_640x480_2021-01-29-230622.jpg",
        "Axis_product/ST_F3S2_640x480.jpg",
        "Axis_product/87ccc0_bafa0d96fbde4c8f86cb17a1e257f8a8mv2.jpg",
    ),
    "production": (
        "Axis_product/87ccc0_da1debf7057c40b7abd7615c59f8703bmv2_d_1416_1502_s_2.png",
        "Axis_product/87ccc0_ff734140285c4af8a507e103c34f2b57mv2.jpg",
        "Axis_product/87ccc0_a9c88bf5853b467d879cf669714de7b6f000.jpg",
        "Axis_product/87ccc0_fa9e2c8aeefe4844922dcdf706592e28mv2.png",
        "Axis_product/87ccc0_bafa0d96fbde4c8f86cb17a1e257f8a8mv2.jpg",
    ),
}


def catalog_item(name, short_desc, description, price, stock, tags, gallery):
    return {
        "name": name,
        "short_desc": short_desc,
        "description": description,
        "price": price,
        "stock": stock,
        "tags": tags,
        "images": GALLERIES[gallery],
    }


CATALOG += (
    catalog_item(
        "Creality Ender-3 V3 KE",
        "A fast, capable desktop FDM printer for everyday prototyping.",
        "The Ender-3 V3 KE gives makers an efficient, approachable route to fast FDM printing for prototypes, fixtures and practical parts.",
        "10999.00", 12, ("FDM", "Beginner", "Fast Print"), "fdm-desktop",
    ),
    catalog_item(
        "Creality K1 Max",
        "An enclosed, large-format FDM printer for ambitious production jobs.",
        "The K1 Max pairs an enclosed build chamber with generous capacity for larger prototypes and consistent small-batch manufacturing.",
        "31999.00", 5, ("FDM", "Large Format", "Enclosed", "Fast Print"), "fdm-industrial",
    ),
    catalog_item(
        "Creality K1C",
        "A compact enclosed FDM printer ready for technical materials.",
        "The K1C brings speed, a tidy enclosed design and dependable material handling to product-development teams and serious makers.",
        "16999.00", 9, ("FDM", "Enclosed", "Professional", "Fast Print"), "fdm-industrial",
    ),
    catalog_item(
        "Creality Ender-5 S1",
        "A stable cube-frame FDM printer for reliable functional prototypes.",
        "The Ender-5 S1 is a versatile FDM platform with a rigid frame that supports accurate desktop fabrication for workshops and design studios.",
        "13999.00", 7, ("FDM", "Professional", "Compact"), "fdm-desktop",
    ),
    catalog_item(
        "Bambu Lab X1 Carbon",
        "A high-speed enclosed FDM system for advanced engineering materials.",
        "The X1 Carbon gives ambitious creators a refined, rapid-printing workflow with the control required for demanding models and components.",
        "28999.00", 6, ("FDM", "Enclosed", "Professional", "Fast Print"), "fdm-industrial",
    ),
    catalog_item(
        "Bambu Lab P1S",
        "An enclosed FDM printer that balances speed, quality and value.",
        "The P1S is a streamlined production-minded desktop printer for practical parts, prototypes and repeatable everyday prints.",
        "19999.00", 10, ("FDM", "Enclosed", "Fast Print"), "fdm-desktop",
    ),
    catalog_item(
        "Bambu Lab A1 Combo",
        "A colour-capable desktop FDM printer for creative and functional builds.",
        "The A1 Combo makes it easy to bring multicolour FDM prototypes and presentation-ready parts into a compact workspace.",
        "15999.00", 11, ("FDM", "Beginner", "Compact", "Multi Material"), "fdm-desktop",
    ),
    catalog_item(
        "Original Prusa MK4",
        "A refined FDM workhorse for dependable, accurate desktop printing.",
        "The Original Prusa MK4 is a proven choice for makers and professionals who value a dependable workflow and consistently strong print quality.",
        "22999.00", 8, ("FDM", "Professional", "Precision"), "fdm-desktop",
    ),
    catalog_item(
        "Original Prusa MINI+",
        "A compact FDM printer for reliable entry-level and lab printing.",
        "The Prusa MINI+ makes dependable FDM printing accessible in a compact format that suits desks, classrooms and small studios.",
        "9999.00", 13, ("FDM", "Beginner", "Compact"), "fdm-desktop",
    ),
    catalog_item(
        "Original Prusa XL",
        "A large-format multi-toolhead FDM platform for advanced projects.",
        "The Prusa XL is built for larger, more complex work where multicolour or multi-material printing and generous build capacity matter.",
        "64999.00", 3, ("FDM", "Large Format", "Multi Material", "Professional"), "fdm-industrial",
    ),
    catalog_item(
        "Anycubic Kobra 3 Combo",
        "A fast multicolour FDM printer for expressive prototypes and products.",
        "The Kobra 3 Combo brings rapid, multicolour FDM production to creative teams and makers with an accessible desktop workflow.",
        "14999.00", 10, ("FDM", "Beginner", "Fast Print", "Multi Material"), "fdm-desktop",
    ),
    catalog_item(
        "Anycubic Photon Mono M5s",
        "A high-resolution resin printer for finely detailed components.",
        "The Photon Mono M5s is ideal for detailed models, miniatures and prototypes where sharp surfaces and fine features are essential.",
        "15999.00", 8, ("Resin", "Precision", "Compact"), "resin-desktop",
    ),
    catalog_item(
        "Anycubic Photon Mono X 6Ks",
        "A spacious resin printer for detailed parts and small production runs.",
        "The Photon Mono X 6Ks offers high-detail resin printing with a practical build area for studios making multiple parts at once.",
        "11999.00", 9, ("Resin", "Precision", "Professional"), "resin-desktop",
    ),
    catalog_item(
        "ELEGOO Neptune 4 Pro",
        "A quick, capable FDM printer for functional desktop fabrication.",
        "The Neptune 4 Pro is a capable choice for users who need fast, clean FDM prints for design iterations and everyday workshop tasks.",
        "8999.00", 15, ("FDM", "Beginner", "Fast Print"), "fdm-desktop",
    ),
    catalog_item(
        "ELEGOO Saturn 3 Ultra",
        "A high-detail resin printer with the capacity for larger creative prints.",
        "The Saturn 3 Ultra combines precision resin output with a roomy platform for high-detail props, models and production-ready prototypes.",
        "18999.00", 7, ("Resin", "Large Format", "Precision"), "resin-large",
    ),
    catalog_item(
        "Flashforge Adventurer 5M Pro",
        "An enclosed FDM printer made for dependable high-speed desktop work.",
        "The Adventurer 5M Pro offers a straightforward enclosed workflow for teams that need repeatable prints with minimal setup.",
        "17999.00", 8, ("FDM", "Enclosed", "Fast Print"), "fdm-industrial",
    ),
    catalog_item(
        "Flashforge Guider 3 Plus",
        "A large-format FDM printer for professional prototyping and tooling.",
        "The Guider 3 Plus has the size and reliability for larger engineering models, jigs and batch production within a professional workspace.",
        "74999.00", 3, ("FDM", "Large Format", "Professional", "Enclosed"), "fdm-industrial",
    ),
    catalog_item(
        "Raise3D Pro3 Plus",
        "An industrial large-format FDM printer for demanding production teams.",
        "The Pro3 Plus supports long, complex print jobs with the capacity and material flexibility needed by engineering and manufacturing teams.",
        "119999.00", 2, ("FDM", "Large Format", "Production", "Professional"), "production",
    ),
    catalog_item(
        "Raise3D E2",
        "A dual-extrusion FDM printer built for dependable professional output.",
        "The Raise3D E2 lets teams produce complex prototypes with dual materials or support structures in a compact professional system.",
        "69999.00", 4, ("FDM", "Dual Extrusion", "Professional", "Enclosed"), "fdm-industrial",
    ),
    catalog_item(
        "UltiMaker S7",
        "A reliable professional FDM printer with an open-material workflow.",
        "The UltiMaker S7 is designed for organisations that need dependable, precise FDM printing across design, engineering and education teams.",
        "99999.00", 3, ("FDM", "Professional", "Precision"), "production",
    ),
    catalog_item(
        "Formlabs Form 4",
        "A next-generation resin printer for exceptionally quick, precise parts.",
        "The Form 4 delivers rapid, detailed resin prints for professionals creating prototypes, presentation models and end-use components.",
        "79999.00", 4, ("Resin", "Professional", "Precision", "Fast Print"), "resin-desktop",
    ),
    catalog_item(
        "Formlabs Form 4B",
        "A professional resin printer tailored to medical and dental workflows.",
        "The Form 4B brings high-speed precision to specialist resin applications that require reliable, detailed and biocompatible parts.",
        "92999.00", 3, ("Resin", "Medical", "Professional", "Fast Print"), "resin-medical",
    ),
    catalog_item(
        "Formlabs Fuse 1+ 30W",
        "A compact SLS system for strong, production-ready nylon parts.",
        "The Fuse 1+ 30W helps teams move beyond prototypes with durable powder-bed parts for functional testing and low-volume production.",
        "399999.00", 1, ("SLS", "Production", "Professional"), "production",
    ),
    catalog_item(
        "Nexa3D XiP Pro",
        "A large-format resin production printer for high-throughput applications.",
        "The XiP Pro gives production teams a fast route to large, precise resin components with excellent surface finish and consistency.",
        "349999.00", 1, ("Resin", "Large Format", "Production", "Professional"), "resin-large",
    ),
    catalog_item(
        "Markforged Mark Two",
        "A composite FDM printer for strong reinforced functional parts.",
        "The Mark Two supports the creation of durable reinforced fixtures, tools and prototype components directly in the workshop.",
        "189999.00", 2, ("FDM", "Carbon Fibre", "Professional", "Production"), "production",
    ),
    catalog_item(
        "Markforged FX20",
        "A large-format composite printer for industrial-strength manufactured parts.",
        "The FX20 is built for demanding composite fabrication, delivering large, robust components for aerospace, automotive and industrial applications.",
        "899999.00", 1, ("FDM", "Carbon Fibre", "Large Format", "Production"), "production",
    ),
    catalog_item(
        "Desktop Metal Shop System",
        "A high-throughput metal binder-jet solution for production parts.",
        "The Shop System helps manufacturers bring metal additive production closer to their workflow for complex parts and efficient short runs.",
        "649999.00", 1, ("Metal", "Production", "Professional"), "metal-production",
    ),
    catalog_item(
        "BCN3D Epsilon W50",
        "A large-format enclosed FDM printer for engineering-grade applications.",
        "The Epsilon W50 provides a controlled environment and generous build capacity for durable prototypes, tools and end-use components.",
        "129999.00", 2, ("FDM", "Large Format", "Enclosed", "Professional"), "fdm-industrial",
    ),
    catalog_item(
        "Stratasys F370",
        "An industrial FDM platform for accurate, repeatable engineering prototypes.",
        "The F370 supports dependable in-house prototyping with the workflow control and material consistency required by professional design and engineering teams.",
        "269999.00", 1, ("FDM", "Production", "Professional", "Enclosed"), "production",
    ),
    catalog_item(
        "Snapmaker Artisan",
        "A premium three-in-one system for 3D printing, CNC and laser projects.",
        "The Snapmaker Artisan gives creative studios a versatile production platform that combines additive, subtractive and laser fabrication.",
        "54999.00", 4, ("FDM", "Multi Tool", "Professional", "Large Format"), "fabrication",
    ),
)


class Command(BaseCommand):
    help = "Sync the curated 3rd Axis 3D-printer catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete the existing 3rd Axis products before recreating the curated collection.",
        )

    def handle(self, *args, **options):
        missing_images = [
            image
            for product in CATALOG
            for image in product["images"]
            if not (Path(settings.MEDIA_ROOT) / image).is_file()
        ]
        if missing_images:
            raise CommandError(
                "The catalog was not changed because these images are missing: "
                + ", ".join(missing_images)
            )

        if options["replace"]:
            Product.objects.all().delete()

        created_count = 0
        for item in CATALOG:
            product, created = Product.objects.update_or_create(
                name=item["name"],
                defaults={
                    "short_desc": item["short_desc"],
                    "description1": item["description"],
                    "price": item["price"],
                    "stock": item["stock"],
                    **{
                        f"image{position}": image
                        for position, image in enumerate(item["images"], start=1)
                    },
                },
            )
            product.tags.set(item["tags"])
            created_count += created

        action = "Recreated" if options["replace"] else "Synced"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {len(CATALOG)} tagged 3D printers "
                f"({created_count} created, {len(CATALOG) - created_count} updated)."
            )
        )
