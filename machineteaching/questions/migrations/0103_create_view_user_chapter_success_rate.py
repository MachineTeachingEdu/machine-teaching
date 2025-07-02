from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0102_create_view_user_chapter_success'), 
    ]

    operations = [
        migrations.RunSQL("""drop view user_chapter_success_rate """),
        migrations.RunSQL("""
CREATE OR REPLACE VIEW public.user_chapter_success_rate
AS WITH successes AS (
         SELECT questions_userlog.user_id,
            questions_exerciseset.chapter_id,
            count(DISTINCT questions_userlog.problem_id) AS success
           FROM questions_userlog
             JOIN questions_problem ON questions_userlog.problem_id = questions_problem.id
             JOIN questions_exerciseset ON questions_problem.id = questions_exerciseset.problem_id
             JOIN questions_chapter ON questions_exerciseset.chapter_id = questions_chapter.id
          WHERE questions_userlog.outcome::text = 'P'::text
          GROUP BY questions_userlog.user_id, questions_exerciseset.chapter_id
        ), totalexercises AS (
         SELECT questions_exerciseset.chapter_id,
            count(questions_exerciseset.problem_id) AS total_exercises
           FROM questions_exerciseset
          GROUP BY questions_exerciseset.chapter_id
        )
 SELECT successes.user_id,
    successes.chapter_id,
    successes.success,
    totalexercises.total_exercises,
    successes.success::double precision / totalexercises.total_exercises::double precision AS success_rate
   FROM successes
     JOIN totalexercises ON successes.chapter_id = totalexercises.chapter_id;""",
        "drop view user_chapter_success_rate "),
    ]
