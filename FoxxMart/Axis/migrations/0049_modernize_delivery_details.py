from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('Axis', '0048_widen_taggit_object_id')]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='delivery_instructions',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='address1',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='address2',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='suburb',
            field=models.CharField(default='', max_length=200),
        ),
    ]
