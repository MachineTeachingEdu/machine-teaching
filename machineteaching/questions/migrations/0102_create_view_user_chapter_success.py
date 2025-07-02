from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0101_create_view_user_chapter_attempts'), 
    ]

    operations = [
        migrations.RunSQL("""drop view user_chapter_success"""),
        migrations.RunSQL("""
CREATE OR REPLACE VIEW public.user_chapter_success
AS SELECT questions_userlog.user_id,
    questions_exerciseset.chapter_id,
    count(DISTINCT questions_userlog.problem_id) AS success
   FROM questions_userlog
     JOIN questions_problem ON questions_userlog.problem_id = questions_problem.id
     JOIN questions_exerciseset ON questions_problem.id = questions_exerciseset.problem_id
     JOIN questions_chapter ON questions_exerciseset.chapter_id = questions_chapter.id
  WHERE questions_userlog.outcome::text = 'P'::text
  GROUP BY questions_userlog.user_id, questions_exerciseset.chapter_id
  ORDER BY questions_userlog.user_id, questions_exerciseset.chapter_id;""",
        "drop view user_chapter_success"),
    ]
