from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('account', '0020_invoice_vat_amounts')]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='delivery_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.CreateModel(
            name='ReturnRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=100)),
                ('details', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('approved', 'Approved'), ('declined', 'Declined'), ('received', 'Received'), ('refunded', 'Refunded')], default='requested', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='return_request', to='account.invoice')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='return_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-created_at',)},
        ),
    ]
