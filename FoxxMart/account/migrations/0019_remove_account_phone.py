from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('account', '0018_invoice')]

    operations = [
        migrations.RemoveField(model_name='account', name='phone'),
    ]
