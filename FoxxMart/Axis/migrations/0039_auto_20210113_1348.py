# Generated by Django 3.1.5 on 2021-01-13 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Axis', '0038_auto_20210113_0346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categorylayer3',
            name='category',
        ),
        migrations.RemoveField(
            model_name='categorylayer4',
            name='category',
        ),
        migrations.RemoveField(
            model_name='categorylayer5',
            name='category',
        ),
        migrations.RemoveField(
            model_name='categorylayer6',
            name='category',
        ),
        migrations.RemoveField(
            model_name='category',
            name='has_subcategory',
        ),
        migrations.RemoveField(
            model_name='product',
            name='category2',
        ),
        migrations.RemoveField(
            model_name='product',
            name='category3',
        ),
        migrations.RemoveField(
            model_name='product',
            name='category4',
        ),
        migrations.RemoveField(
            model_name='product',
            name='category5',
        ),
        migrations.RemoveField(
            model_name='product',
            name='category6',
        ),
        migrations.DeleteModel(
            name='CategoryLayer2',
        ),
        migrations.DeleteModel(
            name='CategoryLayer3',
        ),
        migrations.DeleteModel(
            name='CategoryLayer4',
        ),
        migrations.DeleteModel(
            name='CategoryLayer5',
        ),
        migrations.DeleteModel(
            name='CategoryLayer6',
        ),
    ]
