# Generated by Django 2.1 on 2018-10-20 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0024_auto_20181020_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='seed',
            field=models.CharField(default=0, max_length=81),
            preserve_default=False,
        ),
    ]
