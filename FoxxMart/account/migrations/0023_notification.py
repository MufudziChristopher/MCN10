from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('account', '0022_return_attachments_and_cancellation')]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_slug', models.CharField(max_length=40)),
                ('kind', models.CharField(choices=[('order_status', 'Order status'), ('low_stock', 'Low stock'), ('price_alert', 'Price alert')], max_length=20)),
                ('event_key', models.CharField(max_length=160)),
                ('title', models.CharField(max_length=160)),
                ('body', models.TextField()),
                ('url', models.CharField(blank=True, max_length=500)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-created_at',)},
        ),
        migrations.AddConstraint(
            model_name='notification',
            constraint=models.UniqueConstraint(fields=('user', 'store_slug', 'event_key'), name='unique_customer_notification_event'),
        ),
    ]
