from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_grant_existing_accounts_full_access'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleOAuthIdentity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('google_subject', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='google_identity', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
