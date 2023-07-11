from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0045_auto_20190819_1950'),
    ]

    operations = [
        migrations.RunSQL("""
create view questions_userlogview as
select
	grouped_query.user_id, grouped_query.problem_id, grouped_query.outcome, grouped_query.final_outcome,
	(select
		timestamp
	from
		questions_userlog
	where questions_userlog.user_id = grouped_query.user_id and
		questions_userlog.problem_id = grouped_query.problem_id and
		questions_userlog.outcome = grouped_query.final_outcome
	order by timestamp asc limit 1) as timestamp
from
(
	select distinct_query.user_id, distinct_query.problem_id, sum(distinct_query.outcome) as outcome,
	case
		when sum(distinct_query.outcome) >= 4 then 'P'
		when sum(distinct_query.outcome) >=2 then 'F'
		when sum(distinct_query.outcome) = 1 then 'S'
	end as final_outcome
	from (
		select user_id, problem_id,
			case
				when outcome = 'P' then 4
				when outcome = 'F' then 2
				when outcome = 'S' then 1
			end as outcome
		from questions_userlog group by user_id, problem_id, outcome order by user_id, problem_id
		) as distinct_query
	group by distinct_query.user_id, distinct_query.problem_id
	order by distinct_query.user_id, distinct_query.problem_id) as grouped_query;""",
        "drop view questions_userlogview"),
    ]


