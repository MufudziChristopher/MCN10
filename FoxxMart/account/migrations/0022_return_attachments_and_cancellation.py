from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('account', '0021_invoice_delivery_fee_return_request')]

    operations = [
        migrations.AlterField(
            model_name='returnrequest',
            name='status',
            field=models.CharField(choices=[('requested', 'Requested'), ('approved', 'Approved'), ('declined', 'Declined'), ('received', 'Received'), ('refunded', 'Refunded'), ('cancelled', 'Cancelled')], default='requested', max_length=20),
        ),
        migrations.CreateModel(
            name='ReturnAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='return_requests/%Y/%m/%d/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('return_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='account.returnrequest')),
            ],
        ),
    ]
