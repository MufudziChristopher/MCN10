# Generated by Django 4.2.1 on 2023-05-15 20:49

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('Axis', '0045_remove_product_tags_product_description2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image1',
            field=models.ImageField(blank=True, upload_to='EXODUS_product/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image2',
            field=models.ImageField(blank=True, upload_to='EXODUS_product/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image3',
            field=models.ImageField(blank=True, upload_to='EXODUS_product/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image4',
            field=models.ImageField(blank=True, upload_to='EXODUS_product/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image5',
            field=models.ImageField(blank=True, upload_to='EXODUS_product/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image6',
            field=models.ImageField(blank=True, upload_to='EXODUS_product/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image7',
            field=models.ImageField(blank=True, upload_to='EXODUS_product/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image8',
            field=models.ImageField(blank=True, upload_to='EXODUS_product/'),
        ),
    ]