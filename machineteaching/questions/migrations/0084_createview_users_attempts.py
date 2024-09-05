from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0083_auto_20240408_1842'),
    ]

    operations = [
        migrations.RunSQL("""drop view users_attempts"""),
        migrations.RunSQL("""
create view users_attempts as
select 
	questions_userlog.user_id, chapter_id, count(*) as attempts
from 
	questions_userlog
join 
    questions_problem on problem_id = questions_problem.id 
join
    questions_exerciseset on questions_problem.id = questions_exerciseset.problem_id
join 
    questions_chapter ON questions_exerciseset.chapter_id = questions_chapter.id 
group by 
    user_id, 
    chapter_id
order by 
    user_id,
    chapter_id asc;""",
    "drop view users_attempts"),
    ]
