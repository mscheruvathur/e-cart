# Generated by Django 3.2 on 2021-05-14 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_orderproduct_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='user_cancel',
            field=models.CharField(default=False, max_length=15),
        ),
    ]