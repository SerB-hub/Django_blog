# Generated by Django 3.2.6 on 2021-08-20 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20210820_0555'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryapi',
            name='name',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
    ]