from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('account', '0019_remove_account_phone')]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='invoice',
            name='vat_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
