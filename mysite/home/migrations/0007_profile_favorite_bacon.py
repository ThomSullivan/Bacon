# Generated by Django 3.2.6 on 2021-09-20 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_remove_profile_favorite_bacon'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favorite_bacon',
            field=models.TextField(default='1', null=True),
        ),
    ]
