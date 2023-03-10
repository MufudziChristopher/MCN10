# Generated by Django 3.1.5 on 2021-01-13 01:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Axis', '0037_auto_20210112_1556'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='sub_category2',
        ),
        migrations.RemoveField(
            model_name='product',
            name='sub_category3',
        ),
        migrations.RemoveField(
            model_name='product',
            name='sub_category4',
        ),
        migrations.RemoveField(
            model_name='product',
            name='sub_category5',
        ),
        migrations.RemoveField(
            model_name='product',
            name='sub_category6',
        ),
        migrations.AddField(
            model_name='product',
            name='category2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Axis.categorylayer2'),
        ),
        migrations.AddField(
            model_name='product',
            name='category3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Axis.categorylayer3'),
        ),
        migrations.AddField(
            model_name='product',
            name='category4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Axis.categorylayer4'),
        ),
        migrations.AddField(
            model_name='product',
            name='category5',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Axis.categorylayer5'),
        ),
        migrations.AddField(
            model_name='product',
            name='category6',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Axis.categorylayer6'),
        ),
    ]
