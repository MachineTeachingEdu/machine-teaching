from django.db import migrations, models


def backfill_ai_comment_content(apps, schema_editor):
    GroupComment = apps.get_model("overcode", "GroupComment")
    GroupComment.objects.filter(
        source="ai",
        llm_generated_content="",
    ).update(
        llm_generated_content=models.F("content"),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('overcode', '0004_auto_20260624_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupcomment',
            name='llm_generated_content',
            field=models.TextField(blank=True, default='', help_text='Comentário original gerado pelo LLM antes de edição pelo professor'),
        ),
        migrations.AddField(
            model_name='groupcomment',
            name='llm_teacher_content',
            field=models.TextField(blank=True, default='', help_text='Comentário final usado pelo professor quando ele editou o texto do LLM'),
        ),
        migrations.AddField(
            model_name='groupcomment',
            name='llm_modified_by_professor',
            field=models.BooleanField(default=False, help_text='Indica se o professor editou o comentário original gerado pelo LLM'),
        ),
        migrations.RunPython(
            backfill_ai_comment_content,
            migrations.RunPython.noop,
        ),
    ]
