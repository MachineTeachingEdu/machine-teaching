from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0104_auto_20260514_1746'),
    ]

    operations = [
        migrations.RunSQL("""drop view questions_userlogview"""),
        migrations.RunSQL("""
CREATE OR REPLACE VIEW public.questions_userlogview
AS SELECT grouped_query.user_id,
    grouped_query.problem_id,
    grouped_query.outcome,
    grouped_query.final_outcome,
    grouped_query."timestamp",
    questions_userlog.seconds_in_page,
    questions_userlog.seconds_in_code,
    grouped_query.user_class_id,
    questions_userlog.solution
   FROM ( SELECT questions_outcome_summary.user_id,
            questions_outcome_summary.problem_id,
            questions_outcome_summary.outcome,
            questions_outcome_summary.final_outcome,
            min(questions_userlog_1."timestamp") AS "timestamp",
            questions_outcome_summary.user_class_id
           FROM questions_outcome_summary,
            questions_userlog questions_userlog_1,
            questions_onlineclass
          WHERE questions_userlog_1.user_id = questions_outcome_summary.user_id AND questions_userlog_1.problem_id = questions_outcome_summary.problem_id AND questions_userlog_1.outcome::text = questions_outcome_summary.final_outcome AND questions_outcome_summary.user_class_id = questions_onlineclass.id AND questions_outcome_summary.user_class_id = questions_userlog_1.user_class_id AND questions_userlog_1."timestamp" >= questions_onlineclass.start_date
          GROUP BY questions_outcome_summary.user_id, questions_outcome_summary.problem_id, questions_outcome_summary.outcome, questions_outcome_summary.final_outcome, questions_outcome_summary.user_class_id) grouped_query,
    questions_userlog
  WHERE grouped_query.user_id = questions_userlog.user_id AND grouped_query."timestamp" = questions_userlog."timestamp";""",
        "drop view questions_userlogview"),
    ]
