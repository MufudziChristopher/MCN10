from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('Axis', '0047_alter_product_id_bigautofield'),
    ]

    operations = [
        # django-taggit's generic relation defaults to a 32-bit IntegerField.
        # Foxx Mart has legacy product IDs outside that range, so PostgreSQL
        # needs an int8 column for their tag relationships as well.
        migrations.RunSQL(
            sql=(
                'ALTER TABLE taggit_taggeditem '
                'ALTER COLUMN object_id TYPE bigint USING object_id::bigint;'
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
