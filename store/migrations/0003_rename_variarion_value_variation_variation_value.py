# Generated by Django 3.2 on 2021-05-09 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='variation',
            old_name='variarion_value',
            new_name='variation_value',
        ),
    ]
