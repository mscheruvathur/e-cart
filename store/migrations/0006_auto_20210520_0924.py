# Generated by Django 3.2 on 2021-05-20 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_product_images_4'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='created_date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='modified_date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='variation',
            name='created_date',
            field=models.DateField(auto_now=True),
        ),
    ]
