# Generated by Django 2.2.6 on 2020-10-16 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20201015_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpost',
            name='text',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
