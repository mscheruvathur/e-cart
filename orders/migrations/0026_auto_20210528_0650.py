# Generated by Django 3.2 on 2021-05-28 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_coupondiscount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupondiscount',
            name='coupon_price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coupondiscount',
            name='valid_from',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='coupondiscount',
            name='valid_to',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
