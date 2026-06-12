from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('overcode', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupcomment',
            name='source',
            field=models.CharField(
                choices=[('manual', 'Professor'), ('ai', 'IA')],
                default='manual',
                help_text='Origem do comentário: escrito pelo professor ou gerado com IA',
                max_length=10,
            ),
        ),
    ]
