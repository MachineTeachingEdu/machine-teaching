from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0103_create_view_user_chapter_success_rate'), 
    ]

    operations = [
        migrations.RunSQL("""drop view user_chapter_submissions """),
        migrations.RunSQL("""
CREATE OR REPLACE VIEW public.user_chapter_submissions
AS SELECT questions_userlog.user_id,
    questions_exerciseset.chapter_id,
    count(DISTINCT questions_userlog.problem_id) AS submissions
   FROM questions_userlog
     JOIN questions_problem ON questions_userlog.problem_id = questions_problem.id
     JOIN questions_exerciseset ON questions_problem.id = questions_exerciseset.problem_id
     JOIN questions_chapter ON questions_exerciseset.chapter_id = questions_chapter.id
     JOIN questions_deadline_onlineclass ON questions_userlog.user_class_id = questions_deadline_onlineclass.onlineclass_id
     JOIN questions_deadline ON questions_deadline_onlineclass.deadline_id = questions_deadline.id
  WHERE questions_userlog.outcome::text = 'P'::text AND questions_userlog.user_class_id = questions_deadline_onlineclass.onlineclass_id AND questions_userlog."timestamp" <= questions_deadline.deadline
  GROUP BY questions_userlog.user_id, questions_exerciseset.chapter_id
  ORDER BY questions_userlog.user_id, questions_exerciseset.chapter_id;""",
        "drop view user_chapter_submissions "),
    ]
