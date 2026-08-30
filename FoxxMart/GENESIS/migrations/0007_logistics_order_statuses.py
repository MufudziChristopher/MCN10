from django.db import migrations, models


ORDER_STATUSES = (
    ('Pending', 'Awaiting payment'), ('Payment confirmed', 'Payment confirmed'),
    ('Picking items', 'Picking items'), ('Packed', 'Packed and ready for dispatch'),
    ('Awaiting courier', 'Awaiting courier collection'), ('Collected by courier', 'Collected by courier'),
    ('In transit', 'In transit'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered'),
    ('Delivery exception', 'Delivery exception'), ('Cancelled', 'Cancelled'),
)


def migrate_processing_orders(apps, schema_editor):
    apps.get_model('GENESIS', 'GENESISOrder').objects.filter(status='Payment Confirmed, Processing Order').update(status='Payment confirmed')


class Migration(migrations.Migration):
    dependencies = [('GENESIS', '0006_rename_name1_genesisproduct_name')]
    operations = [
        migrations.RunPython(migrate_processing_orders, migrations.RunPython.noop),
        migrations.AlterField(model_name='genesisorder', name='status', field=models.CharField(choices=ORDER_STATUSES, max_length=200, null=True)),
    ]
