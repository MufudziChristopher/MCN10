from django.db import migrations


STORE_SLUGS = ('axis', 'exodus', 'genesis', 'collective')


def grant_existing_accounts_full_access(apps, schema_editor):
    Account = apps.get_model('account', 'Account')
    StoreAccess = apps.get_model('account', 'StoreAccess')
    for account in Account.objects.iterator():
        for store_slug in STORE_SLUGS:
            StoreAccess.objects.get_or_create(
                user_id=account.pk,
                store_slug=store_slug,
                defaults={'package': 'full'},
            )


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0014_account_first_name_account_last_name_storeaccess_and_more'),
    ]

    operations = [
        migrations.RunPython(grant_existing_accounts_full_access, migrations.RunPython.noop),
    ]
