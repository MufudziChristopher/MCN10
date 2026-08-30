from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Axis', '0046_product_tags_alter_product_image1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
