# Generated by Django 3.0.8 on 2021-04-16 05:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questions', '0075_remove_onlineclass_chapter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendations',
            name='problem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='questions.Problem'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('userlog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.UserLog')),
            ],
            options={
                'verbose_name': 'Comments',
            },
        ),
    ]
