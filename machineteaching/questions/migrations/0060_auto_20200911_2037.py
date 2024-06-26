# Generated by Django 2.2.5 on 2020-09-11 23:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questions', '0059_auto_20200907_1833'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'verbose_name': 'Chapter', 'verbose_name_plural': 'Chapters'},
        ),
        migrations.AlterModelOptions(
            name='historicalchapter',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Chapter'},
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
            name='historicalsolution',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Solution'},
        ),
        migrations.AlterModelOptions(
            name='historicaltestcase',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Test Case'},
        ),
        migrations.AlterModelOptions(
            name='onlineclass',
            options={'verbose_name': 'OnlineClass', 'verbose_name_plural': 'OnlineClasses'},
        ),
        migrations.AlterModelOptions(
            name='problem',
            options={'verbose_name': 'Problem', 'verbose_name_plural': 'Problems'},
        ),
        migrations.AlterModelOptions(
            name='professor',
            options={'verbose_name_plural': 'Professors'},
        ),
        migrations.AlterModelOptions(
            name='solution',
            options={'verbose_name': 'Solution', 'verbose_name_plural': 'Solutions'},
        ),
        migrations.AlterModelOptions(
            name='testcase',
            options={'verbose_name': 'Test Case', 'verbose_name_plural': 'Test Cases'},
        ),
        migrations.AlterModelOptions(
            name='userlog',
            options={'verbose_name': 'User log', 'verbose_name_plural': 'User logs'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'User profile', 'verbose_name_plural': 'User profiles'},
        ),
        migrations.AddField(
            model_name='historicalonlineclass',
            name='start_date',
            field=models.DateField(blank=True, default='2019-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='onlineclass',
            name='start_date',
            field=models.DateField(blank=True, default='2019-01-01'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='HistoricalUserProfile',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('programming', models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], max_length=3)),
                ('accepted', models.BooleanField(default=False)),
                ('read', models.BooleanField(default=False)),
                ('strategy', models.CharField(choices=[('random', 'random'), ('eer', 'eer'), ('sequential', 'sequential')], max_length=10)),
                ('seed', models.CharField(max_length=81)),
                ('sequential', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('professor', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='questions.Professor')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user_class', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='questions.OnlineClass')),
            ],
            options={
                'verbose_name': 'historical User profile',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
