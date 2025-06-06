# Generated by Django 3.2.20 on 2023-08-17 21:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questions', '0081_auto_20220526_1755'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalchapter',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Chapter'},
        ),
        migrations.AlterModelOptions(
            name='historicaldeadline',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Deadline'},
        ),
        migrations.AlterModelOptions(
            name='historicalexerciseset',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Exercise Set'},
        ),
        migrations.AlterModelOptions(
            name='historicalonlineclass',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical OnlineClass'},
        ),
        migrations.AlterModelOptions(
            name='historicalproblem',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Problem'},
        ),
        migrations.AlterModelOptions(
            name='historicalprofessor',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical professor'},
        ),
        migrations.AlterModelOptions(
            name='historicalsolution',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Solution'},
        ),
        migrations.AlterModelOptions(
            name='historicaltestcase',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Test Case'},
        ),
        migrations.AlterModelOptions(
            name='historicaluserprofile',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical User profile'},
        ),
        migrations.AlterField(
            model_name='historicalchapter',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicaldeadline',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalexerciseset',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalonlineclass',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalproblem',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalprofessor',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicalsolution',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicaltestcase',
            name='history_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='history_date',
            field=models.DateTimeField(),
        ),
    ]
