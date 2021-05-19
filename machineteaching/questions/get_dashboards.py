import dash
import dash_html_components as html
import plotly.graph_objects as go
import plotly.offline as opy
from plotly.subplots import make_subplots

import numpy as np
import pandas as pd
import random
from statistics import mean
from datetime import datetime

from questions.models import (Chapter, Problem, UserLog,
                             UserLogView, User, ExerciseSet, Deadline)
from django.utils.translation import gettext as _
from django.utils import timezone
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
                                   outcome='P',
                                   timestamp__gte=onlineclass.start_date)
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
        chapter_problems = Problem.objects.filter(chapter=chapter)
        passed = UserLogView.objects.filter(user=user,
                                            problem__in=chapter_problems,
                                            final_outcome='P')
        if len(passed) > 0:
            problem_errors = []
            for problem in chapter_problems:
                timestamp = passed.filter(problem=problem).values_list('timestamp')
                errors = UserLog.objects.filter(user=user,
                                                problem=problem,
                                                outcome='F',
                                                timestamp__gte=onlineclass.start_date,
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
        chapter_problems = Problem.objects.filter(chapter=chapter)
        passed = UserLogView.objects.filter(user__in=students,
                                            problem__in=chapter_problems,
                                            final_outcome='P')
        if len(passed) > 0:
            problem_errors = []
            for problem in chapter_problems:
                passed_problem = passed.filter(problem=problem)
                errors = 0
                for log in passed_problem:
                    log_errors = UserLog.objects.filter(user__in=students,
                                                        problem=problem,
                                                        outcome='F',
                                                        timestamp__gte=onlineclass.start_date,
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
              problem__in=chapter_problems,
              timestamp__gte=onlineclass.start_date).order_by('timestamp')
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



    #PLOT: class progress

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




    #PLOT: heatmap

    students_table = []
    matrix1 = []
    matrix2 = []
    for student in students:
      #students progress
      user_passed = round(100*UserLogView.objects.filter(user=student,
                                          problem__in=problems,
                                          final_outcome='P').count()/problems.count())
      user_skipped = round(100*UserLogView.objects.filter(user=student,
                                          problem__in=problems,
                                          final_outcome='S').count()/problems.count())
      user_failed = round(100*UserLogView.objects.filter(user=student,
                                          problem__in=problems,
                                          final_outcome='F').count()/problems.count())

      chapter_times = []
      delays = 0
      attempts_list = []
      times_list = []
      line1 = []
      line2 = []
      for chapter in chapters:
        chapter_problems = problems.filter(chapter=chapter)
        deadline = Deadline.objects.get(onlineclass=onlineclass, chapter=chapter).deadline

        logs = UserLog.objects.filter(user=student,
                                      problem__in=chapter_problems,
                                      timestamp__gte=onlineclass.start_date).order_by('timestamp')
        if logs.count():
          first_log = logs.first().timestamp
        times = []
        for problem in chapter_problems:
          passed = UserLog.objects.filter(user=student,
                                          problem=problem,
                                          outcome="P",
                                          timestamp__gte=onlineclass.start_date).order_by('timestamp')
          if passed.count():
            first_passed = passed.first()
            problem_time = round(mean(list(passed.values_list('seconds_in_code', flat=True)))/60)
            times_list.append(problem_time)
            times.append(first_passed.timestamp)
            problem_attempts = logs.filter(problem=problem, timestamp__lte=first_passed.timestamp).count()
            attempts_list.append(problem_attempts)
        times.sort()
        if len(times) == chapter_problems.count():
          chapter_passed = times[-1]
          chapter_times.append((chapter_passed-first_log).days)
          if chapter_passed > deadline:
            line1.append(None)
            line2.append(1)
            delays += 1
          else:
            line1.append((chapter_passed-first_log).days)
            line2.append(None)
        else:
          line1.append(None)
          if timezone.make_aware(datetime.now()) > deadline:
            line2.append(2)
          else:
            line2.append(None)



      matrix1.append(line1)
      matrix2.append(line2)
      
      chapter_time = None
      problem_time = None
      attempts = None

      if len(chapter_times):
        chapter_time = round(mean(chapter_times))
      if len(attempts_list):
        attempts = round(mean(attempts_list))
      if len(times_list):
        problem_time = round(mean(times_list))

      student = {'name': student.first_name+' '+student.last_name,
                       'username': student.username,
                       'id': student.id,
                       'passed': user_passed,
                       'skipped': user_skipped,
                       'failed': user_failed,
                       'chapter_time': chapter_time,
                       'delays': delays,
                       'attempts': attempts,
                       'problem_time': problem_time}
      students_table.append(student)

    students_df = pd.DataFrame(students_table)
    students_df.dropna(subset = ['problem_time','passed','attempts'], inplace=True)


    names = []
    for student in students:
      names.append(student.first_name+' '+student.last_name)
    labels = []
    for chapter in chapters:
      chapter = Chapter.objects.get(id=chapter)
      labels.append(chapter.label)

    fig2 = go.Figure(data=go.Heatmap(
    	z=matrix1,
        x=labels,
        y=names,
        hoverinfo='none',
    colorscale=["rgba(33,150,243,0.2)", "rgb(33,150,243)"]))

    fig2.update_layout(height=650,
                       plot_bgcolor='white',
                       xaxis=dict(fixedrange=True),
                       yaxis=dict(fixedrange=True),
                      margin=dict(
                         l=0,
                         r=0,
                         b=0,
                         t=0,
                         pad=4
                      ),
                       font=dict(family="Nunito",
                                 size=14,
                                 color='rgb(76,83,90)'),)
    fig2.update_traces(showscale=False)

    heatmap_plot = opy.plot(fig2,
		output_type='div')




    fig3 = go.Figure(data=go.Heatmap(
    	z=matrix2,
        x=labels,
        y=names,
        hoverinfo= 'none',
    colorscale=["#FEC809", "rgb(255, 65, 65)"]))

    fig3.update_layout(height=650,
                       xaxis=dict(fixedrange=True),
                       yaxis=dict(fixedrange=True),
                       font=dict(family="Nunito",
                                 size=14,
                                 color='rgb(76,83,90)'),
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



    #PLOT: problems

    problem_ids = []
    problem_times = []
    attempts = []
    for problem in problems:
      logs = UserLog.objects.filter(problem=problem, timestamp__gte=onlineclass.start_date)
      avg_time = None
      avg_attempts = None
      if logs.filter(outcome="P").count():
        passed_times = logs.filter(outcome="P").values_list('seconds_in_code', flat=True)
        if passed_times.count():
          avg_time = round(mean(passed_times)/60)

        problem_attempts = []
        for student in students:
          passed = logs.filter(user=student, outcome="P").order_by('timestamp')
          if passed.count():
            student_attempts = logs.filter(user=student,
                                           timestamp__lte=passed.first().timestamp).count()
            problem_attempts.append(student_attempts)
        avg_attempts = 0
        if len(problem_attempts):
          avg_attempts = mean(problem_attempts)

      problem_ids.append(problem.id)
      problem_times.append(avg_time)
      attempts.append(avg_attempts)


    fig4 = go.Figure(data=go.Scatter(x=problem_times, 
    								 y=attempts,
                     customdata=problem_ids,
                     hovertemplate=_('Problem')+' %{customdata}',
                     name = '',
    								 marker=dict(size=10,
                					 color='rgba(33,150,243,0.8)',
                					 colorscale="portland"),
                					 mode='markers',))

    fig4.update_layout(height=270,
                       font=dict(family="Nunito",
                                 size=14,
                                 color='rgb(76,83,90)'),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Nunito",
                        ),
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
                      yaxis_title=_('Attempts'),
                      xaxis_title=_('Time (minutes)'),)

    # fig4.update_traces(colorscale="hsv")

    problems_plot = opy.plot(fig4,
		output_type='div')




    #PLOT: students

    size = list(students_df['problem_time']+0.1)
    x = students_df['passed']
    y = students_df['attempts']

    if not len(size):
      size = [1]
      
    fig5 = go.Figure(data=[go.Scatter(
    	x=x,
    	y=y,
      customdata=students_df['name'],
      hovertemplate='<b>%{customdata}</b><br>'+_('Solved problems')+': %{x}%<br>'+_('Attempts')+': %{y} ('+_('avg')+')<br>'+_('Time')+': %{marker.size:.0f} min ('+_('avg')+')',
    	mode='markers',
      name = '',
    	marker=dict(
    		size=size,
        sizeref=2.*max(size)/5.**3,
    		sizemode='diameter',
        sizemin=1,
        color='rgba(33,150,243,0.9)'
    		)
    	)])

    fig5.update_layout(height=330,
                       font=dict(family="Nunito",
                                 size=14,
                                 color='rgb(76,83,90)'),
                       hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Nunito",
                       ),
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
                      yaxis_title=_('Attempts'),
                      xaxis_title=_('Solved problems')+' (%)',)

    students_plot = opy.plot(fig5,
		output_type='div')




    chapter_table = []
    counter = 0
    for chapter in chapters:
      finished = 0
      for i in matrix1:
        n = i[counter]
        if n != None:
          finished += 1
        
      delays = 0
      for i in matrix2:
        n = i[counter]
        if n == 1:
          delays += 1

      progress = round(100*(delays+finished)/students.count())

      chapter_problems = problems.filter(chapter=chapter)

      chapter_times = []
      delays = 0
      attempts_list = []
      times_list = []
      for student in students:
        deadline = Deadline.objects.get(onlineclass=onlineclass, chapter=chapter).deadline

        logs = UserLog.objects.filter(user=student,
                                      problem__in=chapter_problems,
                                      timestamp__gte=onlineclass.start_date).order_by('timestamp')
        if logs.count():
          first_log = logs.first().timestamp
        times = []
        for problem in chapter_problems:
          passed = UserLog.objects.filter(user=student,
                                          problem=problem,
                                          outcome="P",
                                          timestamp__gte=onlineclass.start_date).order_by('timestamp')
          if passed.count():
            first_passed = passed.first()
            problem_time = round(mean(list(passed.values_list('seconds_in_code', flat=True)))/60)
            times_list.append(problem_time)
            times.append(first_passed.timestamp)
            problem_attempts = logs.filter(problem=problem, timestamp__lte=first_passed.timestamp).count()
            attempts_list.append(problem_attempts)
        times.sort()
        if len(times) == chapter_problems.count():
          chapter_passed = times[-1]
          chapter_times.append((chapter_passed-first_log).days)
          if chapter_passed > deadline:
            delays += 1

      counter += 1


      chapter_time = None
      problem_time = None
      attempts = None

      if len(chapter_times):
        chapter_time = round(mean(chapter_times))
      if len(attempts_list):
        attempts = round(mean(attempts_list))
      if len(times_list):
        problem_time = round(mean(times_list))

      chapter = Chapter.objects.get(id=chapter)

      chapter_table.append({'label': chapter.label,
                            'progress': progress,
                            'chapter_time': chapter_time,
                            'delays': delays,
                            'attempts': attempts,
                            'problem_time': problem_time})

    chapters_df = pd.DataFrame(students_table)
    chapters_df.dropna(subset = ['problem_time','attempts'], inplace=True)
        



    #PLOT: chapters

    x = ["Aula 1","Aula 2","Aula 3","Aula 4","Aula 5","Aula 6","Aula 7","Aula 8",]

    fig6 = make_subplots(specs=[[{"secondary_y": True}]])

    fig6.add_trace(go.Scatter(x=x, 
    						        y=chapters_df['attempts'],
                			  line=dict( 
                				  color='rgba(33,150,243,1)',
                				  width=4),
                			  mode='lines',
                			  name=_('Attempts'),
                        hovertemplate='<b>%{x}</b><br>%{y} ('+_('avg')+')',
                        # error_y=dict(
                        #   type='percent',
                        #   value=15,
                        #   visible=True,
                        #   color='rgba(33,150,243,0.4)')
                        ),
                        secondary_y=False)

    fig6.add_trace(go.Scatter(x=x, 
    						        y=chapters_df['problem_time'],
                			  line=dict( 
                				  color='#4C4C4C',
                				  width=4,
                				  dash='dot'),
                			  mode='lines',
                			  name=_('Time'),
                        hovertemplate='<b>%{x}</b><br>%{y} min ('+_('avg')+')',
                        # error_y=dict(
                        #   type='percent',
                        #   value=20,
                        #   visible=True,
                        #   color='rgba(0,0,0,0.4)')
                        ),
                        secondary_y=True,)

    fig6.update_layout(height=300,
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Nunito",
                        ),
                       font=dict(family="Nunito",
                                 size=14,
                                 color='rgb(76,83,90)'),
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
    fig6.update_yaxes(title_text=_('Attempts per problem'), secondary_y=False)
    fig6.update_yaxes(title_text=_('Time per problem (minutes)'), secondary_y=True)

    # fig4.update_traces(colorscale="hsv")

    chapters_plot = opy.plot(fig6,
		output_type='div')


    context = { "title": 'Dashboard - '+onlineclass.name,
    "progress_plot": progress_plot,
    "heatmap_plot": heatmap_plot,
    "heatmap2_plot": heatmap2_plot,
    "problems_plot": problems_plot,
    "students_plot": students_plot,
    "chapters_plot": chapters_plot,
    "chapter_table": chapter_table,
    "students_table": students_table,
    "z": delays,
    'matrix1': matrix1
    }

    return context
