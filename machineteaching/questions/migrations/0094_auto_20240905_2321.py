# Generated by Django 3.2.25 on 2024-09-06 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0093_auto_20240905_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcase',
            name='languages',
            field=models.ManyToManyField(to='questions.Language'),
        ),
        migrations.AlterField(
            model_name='historicalsolution',
            name='language',
            field=models.ForeignKey(blank=True, db_constraint=False, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='questions.language'),
        ),
        migrations.AlterField(
            model_name='solution',
            name='language',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='questions.language'),
        ),
        migrations.AlterField(
            model_name='userlog',
            name='language',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='questions.language'),
        ),
    ]