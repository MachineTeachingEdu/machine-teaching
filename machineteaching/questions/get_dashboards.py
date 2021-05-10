import dash
import dash_html_components as html
import plotly.graph_objects as go
import plotly.offline as opy
from plotly.subplots import make_subplots

import numpy as np
import random

from statistics import mean

from questions.models import (Chapter, Problem, UserLog,
                             UserLogView, User, ExerciseSet, Deadline)
from django.utils.translation import gettext as _
import logging

LOGGER = logging.getLogger(__name__)


def student_dashboard(user, professor=False):
    user_label = _("You")
    class_label = _("Your class")
    if professor:
        user_label = _("Student")
        class_label = _("Class")

    onlineclass = user.userprofile.user_class
    students = User.objects.filter(userprofile__user_class=onlineclass)

    # TODO: get logs after class has started to avoid logs from students that came from a previous class
    chapters = Deadline.objects.filter(onlineclass=onlineclass).values_list('chapter', flat=True)
    problems = Problem.objects.filter(chapter__in=chapters)

    user_passed = UserLogView.objects.filter(user=user,
                                        problem__in=problems,
                                        final_outcome='P')
    user_failed = UserLogView.objects.filter(user=user,
                                        problem__in=problems,
                                        final_outcome='F')
    user_skipped = UserLogView.objects.filter(user=user,
                                        problem__in=problems,
                                        final_outcome='S')

    students = User.objects.filter(userprofile__user_class=onlineclass)
    class_passed = UserLogView.objects.filter(user__in=students,
                                        problem__in=problems,
                                        final_outcome='P')
    class_failed = UserLogView.objects.filter(user__in=students,
                                        problem__in=problems,
                                        final_outcome='F')
    class_skipped = UserLogView.objects.filter(user__in=students,
                                        problem__in=problems,
                                        final_outcome='S')

    #problems plot data
    labels = [_("Passed"), _("Failed"), _("Skipped"), _("No attempt")]
    student_values = [len(user_passed),
                      len(user_failed),
                      len(user_skipped),
                      len(problems)-len(user_passed)-len(user_failed)-len(user_skipped)]


    class_values = [len(class_passed),
                    len(class_failed),
                    len(class_skipped),
                    len(students)*len(problems)-len(class_passed)-len(class_failed)-len(class_skipped)]

    #color settings
    colors =['rgb(84, 210, 87)','rgb(255, 65, 65)','#FEC809','rgb(222,226,230)']

    #generating problems plot
    fig = make_subplots(1, 2, specs=[[{'type':'domain'}, {'type':'domain'}]], column_widths=[0.7, 0.3])

    fig.add_trace(go.Pie(labels=labels,
                         values=student_values, 
                         title=dict(
                            text=user_label,
                            font=dict(family="Nunito", size=40, color='rgb(76,83,90)')),
                         textinfo="none",
                         hole=.9,
                         marker=dict(colors=colors),
                         hoverinfo='percent'),1,1)

    fig.add_trace(go.Pie(labels=labels,
                         values=class_values, 
                         title=dict(
                            text=class_label,
                            font=dict(family="Nunito", size=17, color='rgb(76,83,90)')),
                         textinfo="none",
                         hole=.85,
                         marker=dict(colors=colors),
                         hoverinfo='percent'),1,2)

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

    # Average time view
    times = UserLog.objects.filter(user__in=students,
                                   problem__in=problems,
                                   outcome='P')
    student_times = times.filter(user=user).values_list('seconds_in_page')
    
    student_times_sum = 0 
    for time in student_times:
        student_times_sum += time[0]
    if len(student_times) != 0:
        student_time = round(student_times_sum/len(student_times))

    times_sum = 0
    for time in times.values_list('seconds_in_page'):
        times_sum += time[0]
    
    student_time = 0
    if len(student_times) != 0:
        student_time = round(student_times_sum/(len(student_times)*60))
    class_time = 0
    if times:
        class_time = round(times_sum/(len(times)*60))
    problems_time = {'student': student_time, 'class': class_time}

    #errors plot data
    # TODO: os codigos para alunos e turma são praticamente iguais
    # vale a pena criar uma funcao que calcule os erros so passando
    # como parametro o user (pode ser user__in=[user] ou user__id=[students])
    labels = []
    student_errors = []
    for chapter in chapters:
        chapter = Chapter.objects.get(id=chapter)
        problems = Problem.objects.filter(chapter=chapter)
        passed = UserLogView.objects.filter(user=user,
                                            problem__in=problems,
                                            final_outcome='P')
        if len(passed) > 0:
            problem_errors = []
            for problem in problems:
                timestamp = passed.filter(problem=problem).values_list('timestamp')
                errors = UserLog.objects.filter(user=user,
                                                problem=problem,
                                                outcome='F',
                                                timestamp__lte=timestamp)
                problem_errors.append(len(errors))
            chapter_errors = mean(problem_errors)
            student_errors.append(chapter_errors)
            labels.append(chapter.label)
    
    average_errors = 0
    if len(student_errors) != 0:
        average_errors = round(mean(student_errors))

    class_errors = []
    for chapter in chapters:
        problems = Problem.objects.filter(chapter=chapter)
        passed = UserLogView.objects.filter(user__in=students,
                                            problem__in=problems,
                                            final_outcome='P')
        if len(passed) > 0:
            problem_errors = []
            for problem in problems:
                passed_problem = passed.filter(problem=problem)
                errors = 0
                for log in passed_problem:
                    log_errors = UserLog.objects.filter(user__in=students,
                                                        problem=problem,
                                                        outcome='F',
                                                        timestamp__lte=log.timestamp)
                    errors += len(log_errors)
                problem_errors.append(errors)
            chapter_errors = mean(problem_errors)
            class_errors.append(chapter_errors)

    #color settings
    colors = []
    for i in range(len(student_errors)):
        if student_errors[i] == class_errors[i]:
            colors.append('#2196F3');
        elif student_errors[i] < class_errors[i]:
            colors.append('rgb(84, 210, 87)')
        else:
            colors.append('rgb(255, 65, 65)')

    #generating errors plot
    # TODO: esse e o proximo plot possuem uma estrutura muito parecida
    # Acho que vale a pena criar um funcao para criar esses plots tb
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(name=class_label,
                              x=labels,
                              y=class_errors,
                              line_shape='linear',
                              line = dict(color='rgb(200,200,200)', width=5),
                              marker = dict(size=15, color='rgb(200,200,200)'),
                              hoverinfo='none'))

    fig2.add_trace(go.Scatter(name=user_label,
                              x=labels,
                              y=student_errors,
                              line_shape='linear',
                              line = dict(color='#2196F3', width=5),
                              marker = dict(size=15, color=colors),
                              hoverinfo='none'))
    
    fig2.update_layout(autosize=True,
                       height=300,
                       margin=dict(
                          l=10,
                          r=10,
                          b=10,
                          t=0,
                          pad=4
                       ),
                       legend=dict(
                          bgcolor='rgba(0,0,0,0)',
                          traceorder='reversed',
                          yanchor="top",
                          y=0.99,
                          xanchor="right",
                          x=0.99,
                          orientation="h", 
                          font=dict(size=16)
                       ),
                       plot_bgcolor='white',
                       xaxis_title=_('Chapter'),
                       xaxis = dict(
                         fixedrange = True,
                         tickmode = 'linear',
                         dtick = 1),
                       yaxis_title=_('Errors'),
                       yaxis = dict(
                         fixedrange = True,
                         tickmode = 'linear',
                         tick0 = 0,
                         dtick = 1),
                       font=dict(family="Nunito",
                                 size=14,
                                 color='rgb(76,83,90)'),
                       hoverlabel=dict(bgcolor='white',
                                       font_size=15,
                                       font_family='Nunito'))

    # Get user chapters
    chapters = Deadline.objects.filter(onlineclass=onlineclass).values_list('chapter', flat=True)
    chapter_table = []
    for chapter in chapters:
        chapter = Chapter.objects.get(id=chapter)
        chapter_problems = Problem.objects.filter(chapter=chapter)
        userlog = UserLog.objects.filter(
              user=user,
              problem__in=chapter_problems).order_by('timestamp')
        passed = UserLogView.objects.filter(user=user,
                                            problem__in=chapter_problems,
                                            final_outcome='P').order_by('-timestamp')
        progress = 0
        if chapter_problems.count():
            progress = round(100 * len(passed)/len(chapter_problems))
        if progress == 100:
            time = (passed[0].timestamp - userlog[0].timestamp).days
        else:
            time = -1
        chapter_table.append({'chapter': chapter, 'progress': progress, 'time': time})

    # Chapter times plot
    labels = []
    student_times = []
    for chapter in chapter_table:
        if chapter['time'] >= 0:
            labels.append(chapter['chapter'].label)
            student_times.append(chapter['time'])
 
    class_times = []
    for item in chapter_table:
        if item['time'] >= 0:
            chapter_problems = ExerciseSet.objects.filter(chapter=item['chapter']).values_list('problem')
            students = User.objects.filter(userprofile__user_class=onlineclass)
            times = []
            for student in students:
                  userlog = UserLog.objects.filter(
                                            user=student,
                                            problem__in=chapter_problems,
                                            timestamp__gte=onlineclass.start_date).order_by('timestamp').all()
                  passed = UserLogView.objects.filter(user=user,
                                            problem__in=chapter_problems,
                                            final_outcome='P').order_by('timestamp')
                  progress = round(100 * len(passed)/len(chapter_problems))
                  if progress == 100 and len(userlog) != 0:
                      time = (passed.reverse()[0].timestamp - userlog[0].timestamp).days
                      times.append(time)
            class_times.append(mean(times))


    #color settings
    colors = []
    for i in range(len(student_times)):
        if student_times[i] == class_times[i]:
            colors.append('#2196F3');
        elif student_times[i] < class_times[i]:
            colors.append('rgb(84, 210, 87)')
        else:
            colors.append('rgb(255, 65, 65)')

    #generating times plot
    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(name=class_label,
                              x=labels,
                              y=class_times,
                              line_shape='linear',
                              line = dict(color='rgb(200,200,200)', width=5),
                              marker = dict(size=15, color='rgb(200,200,200)'),
                              hoverinfo='none'))
    
    fig3.add_trace(go.Scatter(name=user_label,
                              x=labels,
                              y=student_times,
                              line_shape='linear',
                              line = dict(color='#2196F3', width=5),
                              marker = dict(size=15, color=colors),
                              hoverinfo='none'))

    fig3.update_layout(autosize=True,
                       height=300,
                       margin=dict(
                          l=10,
                          r=10,
                          b=10,
                          t=0,
                          pad=4
                       ),
                       legend=dict(
                          bgcolor='rgba(0,0,0,0)',
                          traceorder='reversed',
                          yanchor="top",
                          y=0.99,
                          xanchor="right",
                          x=0.99,
                          orientation="h",
                          font=dict(size=16)
                       ),
                       plot_bgcolor='white',
                       xaxis_title=_('Chapter'),
                       xaxis = dict(
                         fixedrange = True,
                         tickmode = 'linear',
                         dtick = 1),
                       yaxis_title=_('Time (days)'),
                       yaxis = dict(
                         fixedrange = True,
                         tickmode = 'linear',
                         tick0 = 1,
                         dtick = 1),
                       font=dict(family="Nunito",
                                 size=14,
                                 color='rgb(76,83,90)'),
                       hoverlabel=dict(bgcolor='white',
                                       font_size=15,
                                       font_family='Nunito'))

    problems_plot = opy.plot(fig,
                             auto_open=False,
                             output_type='div')
    errors_plot = opy.plot(fig2,
                             auto_open=False,
                             output_type='div')
    time_plot = opy.plot(fig3,
                             auto_open=False,
                             output_type='div')

    student_name = user.first_name +' '+ user.last_name
    context = {
        "title": _("Outcomes") + ' - ' + student_name,
        "student_name": student_name,
        "problems_plot": problems_plot,
        "problems_time": problems_time,
        "errors": average_errors,
        "chapters": chapter_table,
        "errors_plot": errors_plot,
        "time_plot": time_plot,
    }

    return context



def class_dashboard(onlineclass):
    students = User.objects.filter(userprofile__user_class=onlineclass)
    chapters = Deadline.objects.filter(onlineclass=onlineclass).values_list('chapter', flat=True)
    problems = Problem.objects.filter(chapter__in=chapters)

    passed = UserLogView.objects.filter(user__in=students,
                                        problem__in=problems,
                                        final_outcome='P')
    failed = UserLogView.objects.filter(user__in=students,
                                        problem__in=problems,
                                        final_outcome='F')
    skipped = UserLogView.objects.filter(user__in=students,
                                        problem__in=problems,
                                        final_outcome='S')


    total = len(passed)+len(failed)+len(skipped)
    
    labels = [_("Passed"), _("Failed"), _("Skipped"), _("No attempt")]
    values = [len(passed),
                      len(failed),
                      len(skipped),
                      len(students)*len(problems)-total]
    colors =['rgb(84, 210, 87)','rgb(255, 65, 65)','#FEC809','rgb(222,226,230)']

    fig = go.Figure()

    fig.add_trace(go.Pie(labels=labels,
                         values=values, 
                         title=dict(
                            text=str(round(100*(len(passed)+len(failed)+len(skipped))/(len(students)*len(problems))))+"%",
                            font=dict(family="Nunito", size=50, color='rgb(76,83,90)')),
                         textinfo="none",
                         hole=.9,
                         marker=dict(colors=colors),
                         hoverinfo='percent'))

    fig.update_layout(autosize=True,
                      height=280,
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

    progress_plot = opy.plot(fig,
                             auto_open=False,
                             output_type='div')





    # names = []
    # z = []
    # for student in students:
    # 	names.append(f"{student.first_name} {student.last_name}")
    # 	times = []
    # 	for chapter in chapters:
    # 		chapter = Chapter.objects.get(id=chapter)
    # 		chapter_problems = Problem.objects.filter(chapter=chapter)
    # 		userlog = UserLog.objects.filter(
    # 			user=student,
    # 			problem__in=chapter_problems).order_by('timestamp')
    # 		passed = UserLogView.objects.filter(user=student,
    # 			problem__in=chapter_problems,
    # 			final_outcome='P').order_by('-timestamp')
    # 		progress = 0
    # 		if chapter_problems.count():
    # 			progress = round(100 * len(passed)/len(chapter_problems))

    # 		if progress == 100:
    # 			time = (passed[0].timestamp - userlog[0].timestamp).days
    # 		else:
    # 			time = None
    # 		times.append(time)
    # 	z.append(times)

    # labels = list(Chapter.objects.filter(id__in=chapters).values_list('label'))

    names = ['Aluno 1',
    		'Aluno 2',
    		'Aluno 3',
    		'Aluno 4',
    		'Aluno 5',
    		'Aluno 6',
    		'Aluno 7',
    		'Aluno 8',
    		'Aluno 9',
    		'Aluno 10',
    		'Aluno 11',
    		'Aluno 12',
    		'Aluno 13',
    		'Aluno 14',
    		'Aluno 15',
    		'Aluno 16',
    		'Aluno 17',
    		'Aluno 18',
    		'Aluno 19',
    		'Aluno 20',
    		'Aluno 21',
    		'Aluno 22',
    		'Aluno 23',
    		'Aluno 24',
    		'Aluno 25',
    ]
    labels = ['Aula 1','Aula 2','Aula 3','Aula 4','Aula 5','Aula 6','Aula 7','Aula 8']
    z = [[3,2,5,6,7,5,1,2], [0, 6, 8, 7, 8, 8, 7, 1], [2, 1, 1, 3, 4, 2, 3, 6], [1, 2, 3, 3, 5, 4, 1, 4], [1, 2, 4, 5, 7, 8, 2, 4], [1, 1, 4, 4, 6, 8, 4, 1], [1, 2, 3, 4, 7, 9, 5, 3], [1, 0, 1, 2, 5, 6, 6, 2], [1, 3, 3, 4, 5, 5, 1, 3], [0, 2, 3, 3, 4, 2, 1, 3], [0, 1, 1, 3, 5, 4, 1, 1], [0, 0, 1, 2, 3, 5, 0, 2], [1, 0, 2, 4, 5, 6, 0, 4], [1, 1, 3, 5, 5, 2, 3, 4], [3, 3, 5, 5, 5, 7, 7, 5], [0, 1, 2, 4, 4, 6, 3, 3], [0, 2, 4, 5, 4, 4, 1, 3], [1, 1, 1, 2, 2, 0, 3, 5], [0, 2, 4, 4, 4, 6, 5, 5], [1, 4, 5, 6, 8, 6, 3, 2], [0, 1, 2, 3, 4, 3, 0, 1], [2, 3, 3, 3, 7, 6, 6, 2], [0, 0, 0, 2, 6, 3, 3, 3], [0, 1, 2, 2, 5, 5, 3, 3], [3, 3, 4, 4, 6, 4, 0, 1]]
    
    for line in z:
    	line[2] += 1
    	line[3] -= 1
    	for n in range(4,6):
    		line[n] += 2

    total = []
    for line in z:
    	for n in range(8):
    		total.append(line[n])


    # z = np.random.randint(9, size=(25, 8))
    # for line in z:
    # 	line.sort()
    # 	for n in range(5,8):
    # 		line[n] -= random.randint(0,3)
    # 	for n in range(5,7):
    # 		line[n] += random.randint(0,2)
    # 	for n in range(6,8):
    # 		line[n] -= random.randint(2,5)
    # 	for n in range(5):
    # 		line[n] += random.randint(0,1)

    fig2 = go.Figure(data=go.Heatmap(
    	z=z,
        x=labels,
        y=names,
    colorscale=["rgba(33,150,243,0.1)", "rgb(33,150,243)"]))

    fig2.update_layout(height=670,
                       plot_bgcolor='white',
                      margin=dict(
                         l=0,
                         r=0,
                         b=0,
                         t=0,
                         pad=4
                      ),)
    fig2.update_traces(showscale=False)

    heatmap_plot = opy.plot(fig2,
		output_type='div')


    delays = []
    for name in names:
    	line=[]
    	for chapter in labels:
    		i = random.randint(0,13)
    		n = [0,0,0,0,0,0,0,0,0,2,1,1,1,0][i]
    		if n == 0:
    			line.append(None)
    		else:
    			line.append(n)
    	delays.append(line)

    delays = [
    [None, None, None, 1, None, None, None, 1],
    [None, 1, None, None, 1, 1, None, None], 
    [None, None, None, None, 1, 1, 1, 1], 
    [None, 1, None, None, 1, 2, None, None], 
    [None, None, 1, None, None, None, 1, None], 
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None], 
    [None, None, None, None, None, None, None, None],
    [None, 2, None, None, None, 2, None, None], 
    [None, None, 2, 2, None, 1, 1, 1], 
    [None, None, None, None, 2, 2, None, 2], 
    [None, None, 1, None, 2, 1, None, 1], 
    [None, None, None, None, None, None, None, None], 
    [None, 2, None, 1, None, None, 1, None], 
    [None, 1, 1, 2, None, None, None, None], 
    [None, None, None, None, None, None, None, None], 
    [None, 1, None, None, None, 2, None, None], 
    [None, None, 1, 2, 1, 1, 2, None], 
    [None, None, None, None, 1, None, None, None], 
    [None, None, None, None, None, None, None, None], 
    [None, None, None, 1, 1, 2, None, None], 
    [None, None, 1, 1, 1, None, 2, 2], 
    [None, None, None, None, None, None, None, None], 
    [None, None, None, None, 2, 1, None, 2], 
    [None, None, None, None, None, None, None, None]]

    fig3 = go.Figure(data=go.Heatmap(
    	z=delays,
        x=labels,
        y=names,
    colorscale=["#FEC809", "rgb(255, 65, 65)"]))

    fig3.update_layout(height=670,
    	 			   plot_bgcolor  = "rgba(0, 0, 0, 0)",
    	 			   paper_bgcolor = "rgba(0, 0, 0, 0)",
                      margin=dict(
                         l=0,
                         r=0,
                         b=0,
                         t=0,
                         pad=4
                      ),
                      xaxis_showgrid=False,
                      yaxis_showgrid=False)

    fig3.update_traces(showscale=False)

    heatmap2_plot = opy.plot(fig3,
		output_type='div')



    x = np.random.poisson(12,35)
    y = np.random.poisson(7,35)
    colors = [1,1,1,1,1,
    		  2,2,2,2,
    		  3,3,3,3,
    		  4,4,4,4,
    		  5,5,5,5,
    		  6,6,6,6,6,
    		  7,7,7,7,7,
    		  8,8,8,8]

    fig4 = go.Figure(data=go.Scatter(x=x, 
    								 y=y,
    								 marker=dict(size=10,
                					 color='rgba(33,150,243,0.8)',
                					 colorscale="portland"),
                					 mode='markers',))

    fig4.update_layout(height=270,
    				   plot_bgcolor  = "rgba(0, 0, 0, 0)",
    	 			   paper_bgcolor = "rgba(0, 0, 0, 0)",
                       margin=dict(
                         l=10,
                         r=10,
                         b=10,
                         t=0,
                         pad=4
                      ),
                      xaxis_showgrid=False,
                      yaxis_showgrid=False,
                      yaxis_title=_('Tentativas'),
                      xaxis_title=_('Tempo (minutos)'),)

    # fig4.update_traces(colorscale="hsv")

    problems_plot = opy.plot(fig4,
		output_type='div')


    size = 0.2*np.random.poisson(15,25)**3
    x = np.random.poisson(31,25)
    y = np.random.poisson(7,25)
    fig5 = go.Figure(data=[go.Scatter(
    	x=x,
    	y=y,
    	mode='markers',
    	marker=dict(
    		size=size,
    		sizemode='area',
            color='rgba(33,150,243,0.9)'
    		)
    	)])

    fig5.update_layout(height=330,
    				   plot_bgcolor  = "rgba(0, 0, 0, 0)",
    	 			   paper_bgcolor = "rgba(0, 0, 0, 0)",
                       margin=dict(
                         l=10,
                         r=10,
                         b=10,
                         t=0,
                         pad=4
                      ),
                      xaxis_showgrid=False,
                      yaxis_showgrid=False,
                      yaxis_title=_('Tentativas'),
                      xaxis_title=_('Problemas resolvidos (%)'),)

    students_plot = opy.plot(fig5,
		output_type='div')

    x = ["Aula 1","Aula 2","Aula 3","Aula 4","Aula 5","Aula 6","Aula 7","Aula 8",]
    y = [4,6,10,8,10,12,7,7]

    fig6 = make_subplots(specs=[[{"secondary_y": True}]])

    fig6.add_trace(go.Scatter(x=x, 
    						        y=y,
                			  line=dict( 
                				  color='rgba(33,150,243,1)',
                				  width=4),
                			  mode='lines',
                			  name="Tentativas",
                        # error_y=dict(
                        #   type='percent',
                        #   value=15,
                        #   visible=True,
                        #   color='rgba(33,150,243,0.4)')
                        ),
                        secondary_y=False)

    y2 = [10,15,13,12,18,15,16,14]
    fig6.add_trace(go.Scatter(x=x, 
    						        y=y2,
                			  line=dict( 
                				  color='#4C4C4C',
                				  width=4,
                				  dash='dot'),
                			  mode='lines',
                			  name="Tempo",
                        # error_y=dict(
                        #   type='percent',
                        #   value=20,
                        #   visible=True,
                        #   color='rgba(0,0,0,0.4)')
                        ),
                        secondary_y=True,)

    fig6.update_layout(height=300,
    				   plot_bgcolor  = "rgba(0, 0, 0, 0)",
    	 			   paper_bgcolor = "rgba(0, 0, 0, 0)",
                       margin=dict(
                         l=10,
                         r=30,
                         b=10,
                         t=0,
                         pad=4
                      ),
                       legend=dict(
                       	orientation="h",
                       	yanchor="bottom",
                       	y=1.02,
                       	xanchor="right",
                       	x=1
                       	),
                      xaxis_showgrid=False,
                      yaxis_showgrid=False)
    fig6.update_yaxes(title_text="Tentativas", secondary_y=False)
    fig6.update_yaxes(title_text="Tempo (minutos)", secondary_y=True)

    # fig4.update_traces(colorscale="hsv")

    chapters_plot = opy.plot(fig6,
		output_type='div')


    chapter_table = [{"chapter": "Aula 1", "progress": 95, "attempts": 4, "delays": 0, "time": 2, "problem_time": 10},
                     {"chapter": "Aula 2", "progress": 92, "attempts": 6, "delays": 4, "time": 3, "problem_time": 15},
                     {"chapter": "Aula 3", "progress": 90, "attempts": 10, "delays": 5, "time": 5, "problem_time": 13},
                     {"chapter": "Aula 4", "progress": 85, "attempts": 8, "delays": 4, "time": 4, "problem_time": 12},
                     {"chapter": "Aula 5", "progress": 60, "attempts": 10, "delays": 7, "time": 5, "problem_time": 18},
                     {"chapter": "Aula 6", "progress": 65, "attempts": 12, "delays": 6, "time": 6, "problem_time": 15},
                     {"chapter": "Aula 7", "progress": 10, "attempts": 7, "delays": 3, "time": 3, "problem_time": 16},
                     {"chapter": "Aula 8", "progress": 0, "attempts": 7, "delays": 4, "time": 4, "problem_time": 14}]
    # for chapter in chapters:
    #   chapter = Chapter.objects.get(id=chapter)
    #   chapter_table.append({"chapter": chapter, "progress": progress })


    students_table = [{"student": "Aluno 1", "progress": 100, "attempts": 4, "delays": 0, "time": 2, "problem_time": 12},
                      {"student": "Aluno 2", "progress": 70, "attempts": 8, "delays": 2, "time": 6, "problem_time": 18},
                      {"student": "Aluno 3", "progress": 80, "attempts": 10, "delays": 1, "time": 4, "problem_time": 10},
                      {"student": "Aluno 4", "progress": 35, "attempts": 10, "delays": 0, "time": 2, "problem_time": 13},
                      {"student": "Aluno 5", "progress": 50, "attempts": 6, "delays": 2, "time": 4, "problem_time": 17},]


    context = {
    "progress_plot": progress_plot,
    "heatmap_plot": heatmap_plot,
    "heatmap2_plot": heatmap2_plot,
    "problems_plot": problems_plot,
    "students_plot": students_plot,
    "chapters_plot": chapters_plot,
    "chapter_table": chapter_table,
    "students_table": students_table,
    "z": delays
    }

    return context
