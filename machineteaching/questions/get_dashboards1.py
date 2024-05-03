import re
import colour
from operator import itemgetter
from django.db import connection
from django.utils.translation import gettext as _
import plotly.graph_objects as go
import plotly.offline as opy
from plotly.subplots import make_subplots

def get_time(user, onlineclass, cursor): 
    cursor.execute(f"""SELECT AVG("questions_userlogview"."seconds_in_page") FROM "questions_userlogview" WHERE ("questions_userlogview"."final_outcome" = 'P' AND "questions_userlogview"."problem_id" IN (SELECT V0."id" FROM "questions_problem" V0 INNER JOIN "questions_exerciseset" V1 ON (V0."id" = V1."problem_id") WHERE V1."chapter_id" IN (SELECT U0."chapter_id" FROM "questions_deadline" U0 INNER JOIN "questions_deadline_onlineclass" U1 ON (U0."id" = U1."deadline_id") WHERE U1."onlineclass_id" = {onlineclass})) AND "questions_userlogview"."user_id" IN ({user}) AND "questions_userlogview"."user_class_id" = {onlineclass})""")
    user_time = cursor.fetchone()[0]
    cursor.execute(f"""SELECT AVG("questions_userlogview"."seconds_in_page") FROM "questions_userlogview" WHERE ("questions_userlogview"."final_outcome" = 'P' AND "questions_userlogview"."problem_id" IN (SELECT V0."id" FROM "questions_problem" V0 INNER JOIN "questions_exerciseset" V1 ON (V0."id" = V1."problem_id") WHERE V1."chapter_id" IN (SELECT U0."chapter_id" FROM "questions_deadline" U0 INNER JOIN "questions_deadline_onlineclass" U1 ON (U0."id" = U1."deadline_id") WHERE U1."onlineclass_id" = {onlineclass})) AND "questions_userlogview"."user_class_id" = {onlineclass})""")
    class_time = cursor.fetchone()[0]
    return user_time, class_time

def get_time_diff_per_chapter_user(user, onlineclass, chapter_problems, cursor):
    cursor.execute(f'''SELECT "questions_userlogview"."timestamp" FROM "questions_userlogview" WHERE ("questions_userlogview"."problem_id" IN ({str(chapter_problems).replace('[','').replace(']', '')}) AND "questions_userlogview"."user_id" = {user} AND "questions_userlogview"."user_class_id" = {onlineclass}) ORDER BY "questions_userlogview"."timestamp" ASC''')
    fetch_all_first_user = cursor.fetchall()
    if(len(fetch_all_first_user) == 0):
        final = 0
        add = 0
    else:
        first_user = fetch_all_first_user[0][0]
    cursor.execute(f'''SELECT "questions_userlogview"."timestamp" FROM "questions_userlogview" WHERE ("questions_userlogview"."final_outcome" = 'P' AND "questions_userlogview"."problem_id" IN ({str(chapter_problems).replace('[','').replace(']', '')}) AND "questions_userlogview"."user_id" = {user} AND "questions_userlogview"."user_class_id" = {onlineclass}) ORDER BY "questions_userlogview"."timestamp" DESC''')
    fetch_all_last_user = cursor.fetchall()
    if(len(fetch_all_last_user) == 0 or len(fetch_all_last_user) != len(chapter_problems)):
        final = 0
        add = 0
    else: 
        last_user = fetch_all_last_user[0][0]
        final = (last_user - first_user).total_seconds()
        add = 1
    return (final, add)

def get_users_per_class(onlineclass, cursor):
    cursor.execute(f'''SELECT "questions_userprofile"."user_id" FROM "questions_userprofile" WHERE "questions_userprofile"."user_class_id" = {onlineclass}''')
    users = cursor.fetchall()
    users_id = []
    for user in users:
        users_id.append(user[0])
    return users_id

def get_time_per_chapter(user, onlineclass, cursor): # Alguns dados não tão batendo (eu faço da seguinte forma: para cada capítulo concluido, pego o primeiro log e o último P. Faço a diferença para o aluno. Para a turma, itero pra todos os alunos que também acabaram o capítulo, somando os tempos e dividindo pela quantidade.)
    chapters = get_total_chapters(user, onlineclass, cursor)
    users = get_users_per_class(onlineclass, cursor)
    time_per_chapter = []
    for chapter in chapters:
        chapter_problems = get_chapter_problems(chapter, cursor)
        user_time_diff = get_time_diff_per_chapter_user(user, onlineclass, chapter_problems, cursor)
        if user_time_diff[1] == 0:
            pass
        else:
            user_avg_time = user_time_diff[0]
            total_time = 0
            user_count = 0
            for try_user in users:
                res = get_time_diff_per_chapter_user(try_user, onlineclass, chapter_problems, cursor) ## Essa parte ficou mais lenta no SQL do que no loop
                total_time += res[0]
                user_count += res[1]           
            if user_count == 0:
                pass
            else:
                avg_time = total_time / user_count
                time_per_chapter.append([chapter, round(user_avg_time / (60 * 60 * 24)), round(avg_time / (60 * 60 * 24))])
    return time_per_chapter

        # para cacular a media, precisarei pegar, para cada aluno, a mesma conta acima. Dá pra usar uma função que já faça isso, mas vai adicionar tempo de processamento. Ou mudamos a lógica desse grafico ou usamos a view.
        ### IDEIA: criar view contendo user_id, chapter e (last_log - first_log), pra facilitar essas contas.

def get_chapters(onlineclass, cursor):
    cursor.execute(f'''SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {onlineclass} ORDER BY "questions_deadline"."deadline" ASC''')
    chapters = cursor.fetchall()
    chapters_id = []
    for item in chapters:
        chapters_id.append(item[0])
    return chapters_id

def get_total_chapters(user, onlineclass, cursor):
    chapters_id = str(get_chapters(onlineclass, cursor)).replace('[', '').replace(']', '')
    cursor.execute(f'''select aluno.chapter_id from ((select count(id) as aluno_count, chapter_id from ((SELECT "questions_userlogview"."problem_id" FROM "questions_userlogview" WHERE ("questions_userlogview"."final_outcome" = 'P' AND "questions_userlogview"."problem_id" IN (SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" IN ({chapters_id}) ) AND "questions_userlogview"."user_id" = {user} AND "questions_userlogview"."user_class_id" = {onlineclass})) as a left  outer join (SELECT "questions_problem"."id", "questions_exerciseset"."chapter_id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" IN ({chapters_id})) as b on a."problem_id" = b."id") group by chapter_id) as aluno inner join (SELECT count("questions_problem"."id") as total_count, "questions_exerciseset"."chapter_id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" IN ({chapters_id}) group by "questions_exerciseset"."chapter_id") as total on aluno.chapter_id = total.chapter_id) where aluno_count = total_count''')
    total_chapters = cursor.fetchall()
    total_chapters_id = []
    for item in total_chapters:
        total_chapters_id.append(item[0])
    return total_chapters_id

def get_chapter_problems(chapter, cursor):
    cursor.execute(f'''SELECT "questions_problem"."id", "questions_problem"."question_type", "questions_problem"."title", "questions_problem"."content", "questions_problem"."options", "questions_problem"."difficulty", "questions_problem"."link", "questions_problem"."retrieved_date", "questions_problem"."crawler", "questions_problem"."hint", "questions_problem"."test_case_generator" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" = {chapter}''')
    problems = cursor.fetchall()
    problems_id = []
    for item in problems:
        problems_id.append(item[0])
    return problems_id

def get_error_per_chapter(user, onlineclass, cursor): # Algumas informações não tão batendo (a forma com a qual eu calculo é: para cada capitulo finalizado pelo aluno, olha sua média de erros nos exericios desse capitulo. Depoois comparo com o erro de todos os alunos da turma para esses mesmos problemas.).
    chapters_id = get_total_chapters(user, onlineclass, cursor)
    chapters_problems = []
    for chapter in chapters_id:
        problems_id = get_chapter_problems(chapter, cursor)
        chapters_problems.append([chapter, problems_id])
    error_chapter_user = []
    error_chapter_class = []
    for item in chapters_problems:
        cursor.execute(f'''select avg(count) from questions_errorcount where user_class_id = {onlineclass} and user_id = {user} and problem_id in ({str(item[1]).replace('[','').replace(']', '')})''')
        avg = cursor.fetchone()
        info = avg[0]
        if avg[0] == None:
            info = 0
        error_chapter_user.append([item[0], round(info)])
        cursor.execute(f'''select avg(count) from questions_errorcount where user_class_id = {onlineclass} and problem_id in ({str(item[1]).replace('[','').replace(']', '')})''')
        avg = cursor.fetchone()
        info = avg[0]
        if avg[0] == None:
            info = 0
        error_chapter_class.append([item[0], round(info)])
    error_chapter_user = get_chapter_name(error_chapter_user, cursor)
    error_chapter_class = get_chapter_name(error_chapter_class, cursor)
    return [error_chapter_user, error_chapter_class]

def get_chapter_name(info, cursor):
    for i in info:
        cursor.execute(f'select label from questions_chapter where id = {i[0]}')
        label = cursor.fetchone()
        # position = re.search(r'[0-9]+', label).group()
        i.append(label[0])
        # i.append(position)
    return info

def get_pfs(user, onlineclass, cursor):
        total_problems = 0
        for chapter in get_chapters(onlineclass, cursor):
            total_problems += len(get_chapter_problems(chapter, cursor))
        response_user = []
        response_class = []
        for i in ["P", "F", "S"]:
            cursor.execute(f"""SELECT COUNT(*) FROM "dashboard" WHERE ("dashboard"."final_outcome" = '{i}' AND "dashboard"."problem_id" IN (SELECT V0."id" FROM "questions_problem" V0 INNER JOIN "questions_exerciseset" V1 ON (V0."id" = V1."problem_id") WHERE V1."chapter_id" IN (SELECT U0."chapter_id" FROM "questions_deadline" U0 INNER JOIN "questions_deadline_onlineclass" U1 ON (U0."id" = U1."deadline_id") WHERE U1."onlineclass_id" = {onlineclass})) AND "dashboard"."user_id" IN ({user}) AND "dashboard"."user_class_id" = {onlineclass})""")
            row = cursor.fetchone()
            response_user.append(row[0])
        response_user.append(total_problems - (response_user[0] + response_user[1] + response_user[2]))
        for j in ["P", "F", "S"]:
            cursor.execute(f"""SELECT COUNT(*) FROM "dashboard" WHERE ("dashboard"."final_outcome" = '{j}' AND "dashboard"."problem_id" IN (SELECT V0."id" FROM "questions_problem" V0 INNER JOIN "questions_exerciseset" V1 ON (V0."id" = V1."problem_id") WHERE V1."chapter_id" IN (SELECT U0."chapter_id" FROM "questions_deadline" U0 INNER JOIN "questions_deadline_onlineclass" U1 ON (U0."id" = U1."deadline_id") WHERE U1."onlineclass_id" = {onlineclass})) AND "dashboard"."user_class_id" = {onlineclass})""")
            row = cursor.fetchone()
            response_class.append(row[0])
        class_students = len(get_users_per_class(onlineclass, cursor))
        response_class.append(class_students * total_problems - (response_class[0] + response_class[1] + response_class[2]))
        return [[response_user[0], response_user[3], response_user[1], response_user[2]], [response_class[0], response_class[3], response_class[1], response_class[2]]]

def get_chapter_table(user, onlineclass, cursor):
    chapters = get_chapters(onlineclass, cursor)
    total_chapters = get_total_chapters(user, onlineclass, cursor)
    not_total = set(chapters).difference(set(total_chapters))
    cursor.execute(f'''select id, label, ((done::float/total) * 100)::int, '-' as time from ((select id, done, label from (select chapter_id, count(distinct a.problem_id) as done from questions_userlogview inner join (SELECT problem_id, chapter_id  FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in ({str(not_total).replace('{', '').replace('}', '')})) a on questions_userlogview.problem_id = a.problem_id where user_id = {user} and final_outcome = 'P' group by chapter_id) b inner join questions_chapter on b.chapter_id = questions_chapter.id) chapters left join  (select count(questions_problem.id) as total, chapter_id FROM "questions_problem" INNER JOIN "questions_exerciseset" ON "questions_problem"."id" = "questions_exerciseset"."problem_id" group by chapter_id) problems on chapters.id = problems.chapter_id)''')
    not_total_info = cursor.fetchall()
    time_per_chapter = get_time_per_chapter(user, onlineclass, cursor)
    to_get_label = []
    for i in time_per_chapter:
        to_get_label.append(i[0])
    cursor.execute(f'''select id, label, 100 as progress from questions_chapter where id in ({str(to_get_label).replace('[', '').replace(']', '')})''')
    total_labels = cursor.fetchall()
    chapters = []
    for i in total_labels:
        for j in time_per_chapter:
            if i[0] == j[0]:
                label = i[1]
                position = re.search(r'[0-9]+', label).group()
                chapters.append({
                    'label': i[1],
                    'id': i[0],
                    'progress': i[2],
                    'chapter_time': j[1],
                    'position': position
                        })
    for i in not_total_info:
        label = i[1]
        position = re.search(r'[0-9]+', label).group()
        chapters.append({
            'label': i[1],
            'id': i[0],
            'progress': i[2],
            'chapter_time': '-',
            'position': position
                })
    return tuple(sorted(chapters, key=itemgetter('position')))

def get_erros_before_P(user, cursor):
    cursor.execute(f'''select avg(count)::int from (select outcome, count(outcome), problem_id, user_id from questions_userlog where user_id = {user} and problem_id in (select problem_id from questions_userlogview where final_outcome = 'P' and user_id = {user}) and outcome = 'F' group by problem_id, user_id, outcome) a;''')
    return cursor.fetchone()[0]

def get_dashboards(user, professor=False):
    user_label = _("You")
    class_label = _("Your class")
    if professor:
        user_label = _("Student")
        class_label = _("Class")
    cursor = connection.cursor()
    cursor.execute(f'''SELECT "questions_userprofile"."user_class_id" FROM "questions_userprofile" WHERE "questions_userprofile"."user_id" = {user}''')
    onlineclass = cursor.fetchone()[0]

    pfs = get_pfs(user, onlineclass, cursor)
    time = get_time(user, onlineclass, cursor)
    time_per_chapter = get_time_per_chapter(user, onlineclass, cursor)
    error_per_chapter = get_error_per_chapter(user, onlineclass, cursor)

    text = [user_label, class_label]
    size = [40, 17]
    hole = [0.9, .85]
    column_widths = [0.7, 0.3]
    progress_plot = create_progress_plot(
        2, [pfs[0], pfs[1]], size, text, hole, column_widths)

    chapters = get_chapter_table(user, onlineclass, cursor)
    errors = get_erros_before_P(user, cursor)
    
    return {
        'pfs': pfs,
        'problems_time': {'student': round(float(time[0]) / 60) , 'class': round(float(time[1]) / 60) },
        'time_per_chapter': time_per_chapter,
        'error_per_chapter': error_per_chapter,
        'progress_plot': progress_plot,
        'chapters': chapters,
        'errors': errors
    }

def create_progress_plot(n_plots, values, size, text, hole, column_widths=[1]):
    labels = [_("Passed"), _("No attempt"), _("Failed"), _("Skipped")]
    colors = ['rgb(84, 210, 87)', 'rgb(222,226,230)', 'rgb(255, 65, 65)','#FEC809']
    fig = make_subplots(1, n_plots, specs=[[{'type': 'domain'}]*n_plots], column_widths=column_widths)
    for i in range(n_plots):
        fig.add_trace(go.Pie(labels=labels, values=values[i], title=dict(text=text[i], font=dict(family="Nunito", size=size[i], color='rgb(76,83,90)')), textinfo="none", hole=hole[i], marker=dict(colors=colors),  hoverinfo='percent'), 1, i+1)
    fig.update_layout(autosize=True, height=300,  margin=dict( l=10, r=30, b=0, t=0, pad=4), legend=dict(orientation="h", xanchor='center', x=0.5, font=dict(family="Nunito", size=16, color='rgb(76,83,90)')), hoverlabel=dict(bgcolor='white', font_size=15, font_family='Nunito'))
    plot = opy.plot(fig, auto_open=False, output_type='div')
    return plot

def get_infos_per_problem(cursor, userclass):
    cursor.execute(f'''
select concat(id, ' ', title), minutes, errors
	from questions_problem 
inner join 
	(select problem_id, (avg(seconds_in_code) / 60) as minutes 
			from questions_userlogview 
			where user_class_id = {userclass} 
			and problem_id in 
				(SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass}))
          	group by problem_id
            ) a
on id = a.problem_id
inner join     
      (select problem_id, avg(erros_tries) as errors from 
      		(select user_id, problem_id, count(outcome) as erros_tries 
      		from questions_userlog
      		where user_class_id = {userclass} 
      		and outcome = 'F' group by user_id, problem_id) a
      group by problem_id) b
on a.problem_id = b.problem_id''')
    chapters = cursor.fetchall()
    infos_per_problem = []
    for chapter in chapters:
        infos_per_problem.append([chapter[0], float(chapter[1]), float(chapter[2])])
    return infos_per_problem

class UsersInfos:
    def __init__(self, user, user_name, time, pfs, delays, chapter_time, percentage, tries):
        self.user = user # user_id
        self.user_name = user_name # name
        self.time = time # avg_minutes
        self.pfs = pfs # passed skips fails 
        self.delays = delays
        self.chapter_time = chapter_time
        self.percentage = percentage # completed
        self.tries = tries # avg_tries 

def get_infos_per_user(cursor, userclass):
    cursor.execute(f'''
select 
    b.user,
    concat(first_name, ' ', last_name) as name, 
    coalesce((tries/passed)::int, 0) as avg_tries, 
    coalesce(minutos_acerto, 0) as minutos_acerto,
    coalesce((done::decimal * 100/total)::int, 0) as completed,
    coalesce(passed, 0) as passed, 
    coalesce(skips, 0) as skips, 
    coalesce(fails, 0) as fails,
    total,
    chaptertimediff,
    coalesce(delays, 0) as delays,
    (seconds/passed * 60)::int as avg_minutes_counting_errors
from 
        auth_user
	full outer join
	(select a.user_id as user, passed, fails, skips, (SELECT count("questions_problem"."id") FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass})) as total from 
			(select user_id, count(problem_id) as passed from questions_userlogview where user_class_id  = {userclass} and final_outcome = 'P' and problem_id in  (SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass}))  group by user_id) a
				full outer join 
			(select user_id, count(problem_id) as fails from questions_userlogview where user_class_id  = {userclass} and final_outcome = 'F' and problem_id in  (SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass}))  group by user_id) b
				on a.user_id = b.user_id
				full outer join 
			(select user_id, count(problem_id) as skips from questions_userlogview where user_class_id  = {userclass} and final_outcome = 'S' and problem_id in  (SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass}))  group by user_id) c
	 			on a.user_id = c.user_id
			 where a.user_id is not null
 		) b
 	on auth_user.id = b.user
 	full outer join 
 		(select a.user_id, count(distinct a.problem_id) as done, sum(seconds + seconds_in_page) as seconds, sum(erros_tries + 1) as tries from 
			(select user_id, problem_id, count(outcome) as erros_tries, sum(seconds_in_code) as seconds from questions_userlog where user_class_id = {userclass} and outcome = 'F' group by user_id, problem_id) a
	            inner join 
	        (select distinct user_id, problem_id, outcome, first_value(seconds_in_page) over (partition by user_id, problem_id order by timestamp asc) as seconds_in_page from questions_userlog where user_class_id = {userclass} and outcome = 'P') b
	            on a.user_id = b.user_id and a.problem_id = b.problem_id
       		where a.problem_id in  (SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass}))
            group by a.user_id
        ) a 
 	on a.user_id = b.user
    inner join 
            (select user_id, avg(timediff)::int as chaptertimediff from 
                (select user_id, chapter_id, date_part('days', max(timestamp) - min(timestamp)) as timediff from 
                    (select user_id, chapter_id, timestamp, questions_userlogview.problem_id from questions_userlogview inner join questions_exerciseset on questions_userlogview.problem_id = questions_exerciseset.problem_id  where user_class_id = {userclass}) a
                group by user_id, chapter_id) a 
            group by user_id
            ) c
    on b.user = c.user_id
    left outer join 
            (select user_id, count(*) as delays from 
                (select user_id, max(timestamp) as last_log, chapter_id 
                    from questions_userlogview inner join questions_exerciseset on questions_userlogview.problem_id  = questions_exerciseset.problem_id  where user_class_id = {userclass}
                    group by user_id, chapter_id) a
                inner join 
                    (select deadline, chapter_id from questions_deadline inner join questions_deadline_onlineclass on questions_deadline.id = questions_deadline_onlineclass.deadline_id where onlineclass_id = {userclass}) b
                on b.chapter_id = a.chapter_id
                where last_log > deadline
            group by user_id
            ) d           
    on b.user = d.user_id
    left outer join 
            (select user_id, (avg(soma)/60)::int as minutos_acerto from 
                (select user_id, avg(seconds_in_code) as soma, chapter_id 
                from questions_userlogview inner join questions_exerciseset on questions_userlogview.problem_id  = questions_exerciseset.problem_id  where user_class_id = {userclass}
                group by user_id, chapter_id) a
            group by user_id
            ) e
    on b.user = e.user_id
    ''')
    users = cursor.fetchall()
    infos_per_user = []
    for user in users:
        passed = round(user[5] * 100 / user[8])
        skipped = round(user[6] * 100 / user[8])
        failed = round(user[7] * 100 / user[8])
        infos_per_user.append(UsersInfos(user=user[0], user_name=user[1], tries=user[2], time=user[3], percentage=user[4], pfs=[passed, skipped, failed], chapter_time=user[9], delays=user[10] ))
    infos_per_user.sort(key = lambda x:x.user_name)
    user_plot = []
    for item in infos_per_user:
        user_plot.append([item.user_name, item.tries, item.time, item.percentage])
    return infos_per_user, user_plot

def get_pfs_class(cursor, userclass):
    cursor.execute(f'''
select 'P', count(*) from questions_userlogview where user_class_id = {userclass}  and problem_id in  (SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass})) and final_outcome = 'P'
union 
select 'F', count(*) from questions_userlogview where user_class_id = {userclass}  and problem_id in  (SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass})) and final_outcome = 'F'
union 
select 'S', count(*) from questions_userlogview where user_class_id = {userclass}  and problem_id in  (SELECT "questions_problem"."id" FROM "questions_problem" INNER JOIN "questions_exerciseset" ON ("questions_problem"."id" = "questions_exerciseset"."problem_id") WHERE "questions_exerciseset"."chapter_id" in (SELECT "questions_deadline"."chapter_id" FROM "questions_deadline" INNER JOIN "questions_deadline_onlineclass" ON ("questions_deadline"."id" = "questions_deadline_onlineclass"."deadline_id") WHERE "questions_deadline_onlineclass"."onlineclass_id" = {userclass})) and final_outcome = 'S'
''')
    infos = cursor.fetchall()
    pfs = [0, 0, 0]
    for info in infos:
        if info[0] == 'P':
            pfs[0] = info[1]
        elif info[0] == "S":
            pfs[1] = info[1]
        else:
            pfs[2] = info[1]
    return pfs

def get_heatmap(cursor, onlineclass):
    cursor.execute(f'''select concat(first_name, ' ', last_name) as name, a.user_id, a.chapter_id, 
case 
	when total > coalesce(done, 0) then 0
	when total = coalesce(done, 0) and last_log > deadline then 1
	else 2
end 
as situation,
(coalesce(timediff, -1) * 100 / upper_bound)::int as slow_ratio
from
auth_user 
inner join
(select * from 
	(select a.chapter_id, count(problem_id) as total, max(deadline) as deadline from 
		(select chapter_id, problem_id from questions_exerciseset) a
		inner join
		(select chapter_id, deadline from questions_deadline_onlineclass inner join questions_deadline on questions_deadline.id = questions_deadline_onlineclass.deadline_id where onlineclass_id = {onlineclass}) b
		on a.chapter_id = b.chapter_id
		group by a.chapter_id
 	) a 
 	cross join 
 	(select distinct user_id 
 	from questions_userlog 
 	where user_class_id = {onlineclass}
 	) b
 ) a
 on auth_user.id = a.user_id
left outer join
(select user_id, count(es.problem_id) as done, es.chapter_id, max(timestamp) as last_log from 
	questions_userlogview ulv 
	inner join 
	questions_exerciseset es 
	on ulv.problem_id = es.problem_id 
	where user_class_id = {onlineclass} and final_outcome = 'P'
	group by user_id, chapter_id
) b
on a.chapter_id = b.chapter_id and a.user_id = b.user_id
left outer join 
(select user_id, chapter_id, date_part('days', max(timestamp) - min(timestamp)) as timediff from 
    (select user_id, chapter_id, timestamp, questions_userlogview.problem_id from 
    	questions_userlogview 
    	inner join 
    	questions_exerciseset 
    	on questions_userlogview.problem_id = questions_exerciseset.problem_id 
    	where user_class_id = {onlineclass}) a
	group by user_id, chapter_id
) c
on a.user_id = c.user_id and a.chapter_id = c.chapter_id
left outer join 
(select b.chapter_id, max(timediff) as upper_bound
	from
	(select * from 
		(select a.chapter_id, count(problem_id) as total, max(deadline) as deadline from 
			(select chapter_id, problem_id from questions_exerciseset) a
			inner join
			(select chapter_id, deadline from questions_deadline_onlineclass inner join questions_deadline on questions_deadline.id = questions_deadline_onlineclass.deadline_id where onlineclass_id = {onlineclass}) b
			on a.chapter_id = b.chapter_id
			group by a.chapter_id
	 	) a 
	 	cross join 
	 	(select distinct user_id 
	 	from questions_userlog 
	 	where user_class_id = {onlineclass}
	 	) b
	 ) a
	left outer join
	(select user_id, count(es.problem_id) as done, es.chapter_id, max(timestamp) as last_log from 
		questions_userlogview ulv 
		inner join 
		questions_exerciseset es 
		on ulv.problem_id = es.problem_id 
		where user_class_id = {onlineclass} and final_outcome = 'P'
		group by user_id, chapter_id
	) b
	on a.chapter_id = b.chapter_id and a.user_id = b.user_id
	left outer join 
	(select user_id, chapter_id, date_part('days', max(timestamp) - min(timestamp)) as timediff from 
	    (select user_id, chapter_id, timestamp, questions_userlogview.problem_id from 
	    	questions_userlogview 
	    	inner join 
	    	questions_exerciseset 
	    	on questions_userlogview.problem_id = questions_exerciseset.problem_id 
	    	where user_class_id = {onlineclass}) a
		group by user_id, chapter_id
	) c
	on a.user_id = c.user_id and a.chapter_id = c.chapter_id
	where total = coalesce(done, 0) and last_log < deadline
	group by b.chapter_id
) d
on a.chapter_id = d.chapter_id
order by name, chapter_id''')
    infos = cursor.fetchall()
    chapters_users = []
    user_id = None
    infos_per_user = []
    user_name = None
    for info in infos:
        if user_id == info[1]:
            infos_per_user.append(get_color(info[3], info[4]))
        else:
            if user_id != None:
                chapters_users.append([user_name, infos_per_user])
            infos_per_user = []
            user_id = info[1]
            user_name = info[0]
            infos_per_user.append(get_color(info[3], info[4])) 
            if len(user_name) > 20:
                chapters_users.append(
                    {
                        'name':user_name[:20] + '...', 
                        'colors': infos_per_user
                    }
                )
            else:
                chapters_users.append(
                    {
                        'name':user_name, 
                        'colors': infos_per_user
                    }
                )
    return chapters_users

def get_color(situation, percentage):
    list_of_colors = list(colour.Color('#d8ecfc').range_to(colour.Color('#2196f3'), 101))
    if situation == 0:
        color = '#ff4141'
    elif situation == 1:
        color = '#fec809'
    else:
        color = list_of_colors[percentage]
    return colour.Color(color).hex
    
def get_class_dashboards(onlineclass):
    cursor = connection.cursor()
    pfs = get_pfs_class(cursor, onlineclass.id)
    infos_per_user, user_plot = get_infos_per_user(cursor, onlineclass.id)
    infos_per_problem = get_infos_per_problem(cursor, onlineclass.id)
    number_of_problems = len(infos_per_user) * len(infos_per_problem)
    not_done = (number_of_problems - (pfs[0] + pfs[1] + pfs[2])) 
    pfs.append(not_done)
    text = [str(round(((number_of_problems - not_done) * 100 / number_of_problems))) + "%"]
    size = [50]
    hole = [0.9]
    progress_plot = create_progress_plot(1, [[pfs[0], pfs[3], pfs[2], pfs[1]]], size, text, hole)
    heatmap_colors = get_heatmap(cursor, onlineclass.id)
    return {
        "title": 'Dashboard - ' + onlineclass.name,
        'infos_per_user': infos_per_user,
        'infos_per_problem': infos_per_problem,
        'progress_plot': progress_plot,
        'user_plot': user_plot,
        'heatmap_colors': heatmap_colors
    }