import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_alter_account_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('store_slug', models.CharField(max_length=40)),
                ('store_name', models.CharField(max_length=100)),
                ('order_reference', models.CharField(max_length=100)),
                ('transaction_id', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(blank=True, max_length=200)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('items', models.JSONField(default=list)),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-issued_at',)},
        ),
        migrations.AddConstraint(
            model_name='invoice',
            constraint=models.UniqueConstraint(fields=('user', 'store_slug', 'order_reference'), name='unique_user_store_order_invoice'),
        ),
    ]
