# Generated by Django 2.2.6 on 2020-11-06 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0019_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',), 'verbose_name_plural': 'Комментарии'},
        ),
    ]
