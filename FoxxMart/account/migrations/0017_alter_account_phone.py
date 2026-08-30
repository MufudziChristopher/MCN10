from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_googleoauthidentity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='phone',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Phone Number'),
        ),
    ]
