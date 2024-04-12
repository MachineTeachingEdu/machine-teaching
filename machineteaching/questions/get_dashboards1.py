import re
from operator import itemgetter
from django.db import connection
from django.utils.translation import gettext as _

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

import plotly.graph_objects as go
import plotly.offline as opy
from plotly.subplots import make_subplots

def create_progress_plot(n_plots, values, size, text, hole, column_widths=[1]):
    labels = [_("Passed"), _("No attempt"), _("Failed"), _("Skipped")]
    # color settings
    colors = ['rgb(84, 210, 87)', 'rgb(222,226,230)', 'rgb(255, 65, 65)',
              '#FEC809']

    fig = make_subplots(1, n_plots, specs=[
                        [{'type': 'domain'}]*n_plots], column_widths=column_widths)
    for i in range(n_plots):
        fig.add_trace(go.Pie(labels=labels,
                             values=values[i],
                             title=dict(
                                 text=text[i],
                                 font=dict(family="Nunito", size=size[i], color='rgb(76,83,90)')),
                             textinfo="none",
                             hole=hole[i],
                             marker=dict(colors=colors),
                             hoverinfo='percent'), 1, i+1)

    fig.update_layout(autosize=True,
                      height=300,
                      margin=dict(
                          l=10,
                          r=30,
                          b=0,
                          t=0,
                          pad=4
                      ),
                      legend=dict(
                          orientation="h",
                          xanchor='center',
                          x=0.5,
                          font=dict(family="Nunito",
                                    size=16,
                                    color='rgb(76,83,90)')),
                      hoverlabel=dict(bgcolor='white',
                                      font_size=15,
                                      font_family='Nunito'))
    plot = opy.plot(fig, auto_open=False, output_type='div')
    return plot

