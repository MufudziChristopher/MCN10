# Generated by Django 4.1.7 on 2023-03-28 23:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GENESIS', '0005_genesisproduct_short_desc'),
    ]

    operations = [
        migrations.RenameField(
            model_name='genesisproduct',
            old_name='name1',
            new_name='name',
        ),
    ]
