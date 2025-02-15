# Generated by Django 3.0.8 on 2021-09-06 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0077_auto_20210729_0406'),
    ]

    operations = [
        migrations.CreateModel(
            name='DropOutModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_file', models.URLField()),
                ('completed_chapter', models.ManyToManyField(to='questions.Chapter')),
            ],
            options={
                'verbose_name': 'Drop out model',
                'verbose_name_plural': 'Drop out models',
            },
        ),
    ]
