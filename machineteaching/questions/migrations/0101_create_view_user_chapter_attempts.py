from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0094_auto_20240905_2321'),
    ]

    operations = [
        migrations.RunSQL("""drop view user_chapter_attempts"""),
        migrations.RunSQL("""
CREATE OR REPLACE VIEW public.user_chapter_attempts
AS SELECT questions_userlog.user_id,
    questions_exerciseset.chapter_id,
    count(*) AS attempts
   FROM questions_userlog
     JOIN questions_problem ON questions_userlog.problem_id = questions_problem.id
     JOIN questions_exerciseset ON questions_problem.id = questions_exerciseset.problem_id
     JOIN questions_chapter ON questions_exerciseset.chapter_id = questions_chapter.id
  GROUP BY questions_userlog.user_id, questions_exerciseset.chapter_id
  ORDER BY questions_userlog.user_id, questions_exerciseset.chapter_id;""",
        "drop view user_chapter_attempts"),
    ]
