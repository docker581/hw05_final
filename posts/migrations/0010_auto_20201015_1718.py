# Generated by Django 2.2.6 on 2020-10-15 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_newpost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpost',
            name='group',
            field=models.CharField(blank=True, choices=[('test', 'Test group'), ('second', 'Second group'), ('third', 'Third group')], max_length=100),
        ),
    ]
