# Generated by Django 2.2.6 on 2020-11-05 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20201017_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/', verbose_name='Изображение'),
        ),
    ]
