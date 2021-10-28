import dash
import dash_html_components as html
import plotly.graph_objects as go
import plotly.offline as opy
from plotly.subplots import make_subplots

import numpy as np
import pandas as pd
from statistics import mean, median
import statsmodels.api as sm
from datetime import datetime

from questions.models import (Chapter, Problem, UserLog, OnlineClass,
                             UserLogView, User, ExerciseSet, Deadline,
                             UserLogError, DropOutModel)
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Avg, Count
import logging

import pickle


LOGGER = logging.getLogger(__name__)

# Funções para pegar dados
def get_logs_distribution(user, problems, onlineclass):
    passed = UserLogView.objects.filter(user__in=user,
                                        problem__in=problems,
                                        final_outcome='P',
                                        timestamp__gte=onlineclass.start_date)
    failed = UserLogView.objects.filter(user__in=user,
                                        problem__in=problems,
                                        final_outcome='F',
                                        timestamp__gte=onlineclass.start_date)
    skipped = UserLogView.objects.filter(user__in=user,
                                        problem__in=problems,
                                        final_outcome='S',
                                        timestamp__gte=onlineclass.start_date)
    return passed, failed, skipped

def percentage(value, total):
  if total:
    return 100 * value / total
  else:
    return 0

def get_progress_per_problem(user, problems, onlineclass):
  passed, failed, skipped = get_logs_distribution(user, problems, onlineclass)
  total = len(user) * len(problems)
  total_done = len(passed) + len(failed) + len(skipped)
  values = [percentage(len(passed), total),
            percentage(len(failed), total),
            percentage(len(skipped), total),
            percentage(total-total_done, total)]
  return values

def get_time_in_page_per_problem(user, problems, onlineclass):
  passed = UserLogView.objects.filter(user__in=user,
                                      problem__in=problems,
                                      final_outcome='P',
                                      timestamp__gte=onlineclass.start_date)
  
def get_time_to_finish_chapter(user, chapter, onlineclass):
  user_passed = UserLogView.objects.filter(user=user,
                                      final_outcome='P',
                                      timestamp__gte=onlineclass.start_date).values_list('problem')
  problems = Problem.objects.filter(chapter=chapter).exclude(id__in=user_passed)
  class_students = User.objects.filter(userprofile__user_class=onlineclass)
  medians = []
  for problem in problems:
    passed_times = UserLog.objects.filter(user__in=class_students,
                                      problem=problem,
                                      outcome='P',
                                      timestamp__gte=onlineclass.start_date).values_list('seconds_in_page', flat=True)
    if passed_times.count():
      medians.append(median(passed_times))
    else:
      passed_times = UserLog.objects.filter(problem=problem,
                                      outcome='P',
                                      timestamp__gte=onlineclass.start_date).values_list('seconds_in_page', flat=True)
      if passed_times.count():
        medians.append(median(passed_times))
  time_to_finish = round(sum(medians)/60)
  if problems.count() == 0:
    time_to_finish = None
  return time_to_finish

def get_error_per_problem(user, problems):
  pass

def get_error_type_per_chapter(user, chapter, onlineclass):
    userlogs = UserLog.objects.filter(user__in=user,
                                      problem__in=Problem.objects.filter(chapter__in=chapter).distinct(),
                                      timestamp__gte=onlineclass.start_date)
    errors = UserLogError.objects.filter(
                    userlog__in=userlogs).values('error').annotate(Count('error')).order_by('-error__count')
    return errors

def get_on_time_exercises(user, chapters, onlineclass):
  problems = Problem.objects.filter(chapter__in=chapters)
  deadline = Deadline.objects.filter(chapter__in=chapters,
                                     onlineclass=onlineclass).first().deadline
  on_time_exercises = UserLogView.objects.filter(user=user,
                                                 problem__in=problems,
                                                 final_outcome='P',
                                                 timestamp__gte=onlineclass.start_date,
                                                 timestamp__lte=deadline)
  return [[on_time_exercises.count()]]

def predict_drop_out(user, onlineclass):
  # Get last completed chapter and model
  completed_chapter = Deadline.objects.filter(onlineclass=onlineclass,
                        deadline__lte=datetime.now()).order_by('deadline').last().chapter
  model = completed_chapter.drop_out_model
  if model:
    chapters = model.completed_chapter.all()
    # Open model file
    with open(model.model_file, "rb") as pklfile:
      model = pickle.load(pklfile)

    X = get_on_time_exercises(user,chapters,onlineclass)
    X = sm.add_constant(X, has_constant='add')
    y_pred = model.predict(X)[0]

    if y_pred < 4:
      risk = _('High')
    elif y_pred < 8:
      risk = _('Medium')
    else:
      risk = _('Low')
    return round(y_pred), risk
  else:
    return None

# Funções de plot
def create_progress_plot(n_plots, values, size, text, hole, column_widths=[1]):
    labels = [_("Passed"), _("Failed"), _("Skipped"), _("No attempt")]
    #color settings
    colors =['rgb(84, 210, 87)','rgb(255, 65, 65)','#FEC809','rgb(222,226,230)']

    fig = make_subplots(1, n_plots, specs=[[{'type':'domain'}]*n_plots], column_widths=column_widths)
    for i in range(n_plots):
      fig.add_trace(go.Pie(labels=labels,
                          values=values[i], 
                          title=dict(
                              text=text[i],
                              font=dict(family="Nunito", size=size[i], color='rgb(76,83,90)')),
                          textinfo="none",
                          hole=hole[i],
                          marker=dict(colors=colors),
                            hoverinfo='percent'),1, i+1)

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

def student_dashboard(user, professor=False):
    # Separate labels from student view to professor view
    user_label = _("You")
    class_label = _("Your class")
    if professor:
        user_label = _("Student")
        class_label = _("Class")

    # Get user class and all its students
    onlineclass = user.userprofile.user_class
    students = User.objects.filter(userprofile__user_class=onlineclass)

    chapters = Deadline.objects.filter(onlineclass=onlineclass).order_by('deadline').values_list('chapter', flat=True)
    problems = Problem.objects.filter(chapter__in=chapters)

    #Progress plot
    student_values = get_progress_per_problem([user], problems, onlineclass)
    class_values = get_progress_per_problem(students, problems, onlineclass)

    text = [user_label, class_label]
    size = [40, 17]
    hole = [0.9, .85]
    column_widths = [0.7, 0.3]
    progress_plot = create_progress_plot(2, [student_values, class_values], size, text, hole, column_widths)

    # Average time view
    times = UserLog.objects.filter(user__in=students,
                                   problem__in=problems,
                                   outcome='P',
                                   timestamp__gte=onlineclass.start_date)
    student_times = times.filter(user=user).values_list('seconds_in_page')
    
    # Calculate average time in page to solve problem in minutes
    student_time = 0
    class_time = 0
    if student_times.aggregate(avg_time=Avg('seconds_in_page'))['avg_time']:
      student_time = round(student_times.aggregate(avg_time=Avg('seconds_in_page'))['avg_time']/60)
    if times.aggregate(avg_time=Avg('seconds_in_page'))['avg_time']:
      class_time = round(times.aggregate(avg_time=Avg('seconds_in_page'))['avg_time']/60) 
    problems_time = {'student': student_time, 'class': class_time}

    chapter_table = []
    errors_plot = None
    time_plot = None
    avg_errors = 0
    for chapter in chapters:
      chapter_problems = problems.filter(chapter=chapter)

      progress = round(100*UserLogView.objects.filter(user=user,
                                          problem__in=chapter_problems,
                                          final_outcome='P').count()/chapter_problems.count())

      logs = UserLog.objects.filter(user=user,
                                      problem__in=chapter_problems,
                                      timestamp__gte=onlineclass.start_date).order_by('timestamp')
      
      if logs.count():
        first_log = logs.first().timestamp
      times = []
      for problem in chapter_problems:
        passed = UserLog.objects.filter(user=user,
                                        problem=problem,
                                        outcome="P",
                                        timestamp__gte=onlineclass.start_date).order_by('timestamp')
        if passed.count():
          first_passed = passed.first()
          times.append(first_passed.timestamp)
      times.sort()

      chapter_time = None

      if len(times) == chapter_problems.count():
        chapter_passed = times[-1]
        chapter_time = (chapter_passed-first_log).days

      chapter_times = []
      for student in students:
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
            times.append(first_passed.timestamp)
        times.sort()
        if len(times) == chapter_problems.count():
          chapter_passed = times[-1]
          chapter_times.append((chapter_passed-first_log).days)

      class_time = None
      if len(chapter_times):
        class_time = round(mean(chapter_times))

      c_errors = []
      for problem in chapter_problems:
        # Faz sentido o primeiro acerto da turma TODA?
        passed = UserLog.objects.filter(user__in=students,
                                        problem=problem,
                                        outcome="P",
                                        timestamp__gte=onlineclass.start_date).order_by('timestamp')

        if passed.count():
          # Get timestamp from first success attempt
          timestamp = passed.first().timestamp
        else:
          timestamp = datetime.now()

        errors = UserLog.objects.filter(user__in=students,
                                        problem=problem,
                                        outcome='F',
                                        timestamp__gte=onlineclass.start_date,
                                        timestamp__lte=timestamp).count()
            
        c_errors.append(errors)

      class_errors = None
      if len(c_errors):
        class_errors = round(mean(c_errors))

      u_errors = []
      for problem in chapter_problems:
        passed = passed.filter(user=user)

        if passed.count():
          timestamp = passed.first().timestamp

          errors = UserLog.objects.filter(user=user,
                                          problem=problem,
                                          outcome='F',
                                          timestamp__gte=onlineclass.start_date,
                                          timestamp__lte=timestamp).count()
          u_errors.append(errors)

      user_errors = None
      if len(u_errors):
        user_errors = round(mean(u_errors))

      chapter = Chapter.objects.get(id=chapter)

      chapter_table.append({'label': chapter.label,
                            'id': chapter.id,
                            'progress': progress,
                            'chapter_time': chapter_time,
                            'class_time': class_time,
                            'class_errors': class_errors,
                            'user_errors': user_errors})
    if len(chapter_table) > 0:
      chapters_df = pd.DataFrame(chapter_table)
      chapters_df.dropna(subset = ['chapter_time','class_time','class_errors','user_errors'], inplace=True)

      # avg_errors = 0
      if chapters_df['user_errors'].count():
        avg_errors = round(chapters_df['user_errors'].mean())

      colors = []
      user_errors = chapters_df['user_errors'].tolist()
      class_errors = chapters_df['class_errors'].tolist()
      for i in range(len(user_errors)):
          if user_errors[i] == class_errors[i]:
              colors.append('#2196F3');
          elif user_errors[i] < class_errors[i]:
              colors.append('rgb(84, 210, 87)')
          else:
              colors.append('rgb(255, 65, 65)')

      x = []
      n=1
      for item in chapters_df['user_errors'].tolist():
        if item:
          x.append(n)
        n+=1

      fig2 = make_subplots()

      fig2.add_trace(go.Scatter(x=x, 
                          y=chapters_df['user_errors'],
                          line=dict( 
                            color='rgba(33,150,243,1)',
                            width=4),
                          name=user_label,
                          marker = dict(size=12, color=colors),
                          hovertemplate='<b>'+_('Chapter')+' %{x}</b><br>%{y} '+_('error(s)'),
                          # error_y=dict(
                          #   type='percent',
                          #   value=15,
                          #   visible=True,
                          #   color='rgba(33,150,243,0.4)')
                          ))

      fig2.add_trace(go.Scatter(x=x, 
                          y=chapters_df['class_errors'],
                          line=dict( 
                            color='#4C4C4C',
                            width=4,
                            dash='dot'),
                          mode='lines',
                          name=class_label,
                          hovertemplate='<b>'+_('Chapter')+' %{x}</b><br>%{y} '+_('error(s)'),
                          # error_y=dict(
                          #   type='percent',
                          #   value=20,
                          #   visible=True,
                          #   color='rgba(0,0,0,0.4)')
                          ))

      fig2.update_layout(height=300,
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
                        xaxis = dict(
                          title=_('Chapter'),
                          showgrid=False,
                          fixedrange = True,
                          tickmode = 'linear',
                          dtick = 1),
                        yaxis_showgrid=False,
                        yaxis = dict(
                          title=_('Errors'),
                          fixedrange = True,
                          tickmode = 'linear',
                          tick0 = 0,),)

      colors = []
      student_times = chapters_df['chapter_time'].tolist()
      class_times = chapters_df['class_time'].tolist()
      for i in range(len(student_times)):
          if student_times[i] == class_times[i]:
              colors.append('#2196F3');
          elif student_times[i] < class_times[i]:
              colors.append('rgb(84, 210, 87)')
          else:
              colors.append('rgb(255, 65, 65)')

      x = []
      n=1
      for item in chapters_df['user_errors'].tolist():
        if item:
          x.append(n)
        n+=1

      fig3 = make_subplots()

      fig3.add_trace(go.Scatter(x=x, 
                          y=chapters_df['chapter_time'],
                          line=dict( 
                            color='rgba(33,150,243,1)',
                            width=4),
                          name=user_label,
                          marker = dict(size=12, color=colors),
                          hovertemplate='<b>'+_('Chapter')+' %{x}</b><br>%{y} '+_('day(s)'),
                          # error_y=dict(
                          #   type='percent',
                          #   value=15,
                          #   visible=True,
                          #   color='rgba(33,150,243,0.4)')
                          ))

      fig3.add_trace(go.Scatter(x=x, 
                          y=chapters_df['class_time'],
                          line=dict( 
                            color='#4C4C4C',
                            width=4,
                            dash='dot'),
                          mode='lines',
                          name=class_label,
                          hovertemplate='<b>'+_('Chapter')+' %{x}</b><br>%{y} '+_('day(s)'),
                          # error_y=dict(
                          #   type='percent',
                          #   value=20,
                          #   visible=True,
                          #   color='rgba(0,0,0,0.4)')
                          ))

      fig3.update_layout(height=300,
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
                        xaxis = dict(
                          title=_('Chapter'),
                          showgrid=False,
                          fixedrange = True,
                          tickmode = 'linear',
                          dtick = 1),
                        yaxis_showgrid=False,
                        yaxis = dict(
                          title=_('Time (days)'),
                          fixedrange = True,
                          tickmode = 'linear',
                          tick0 = 0,),)

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
        "problems_plot": progress_plot,
        "problems_time": problems_time,
        "errors": avg_errors,
        "chapters": chapter_table,
        "errors_plot": errors_plot,
        "time_plot": time_plot,
    }

    return context



def class_dashboard(onlineclass):
    students = User.objects.filter(userprofile__user_class=onlineclass).order_by('-first_name','-last_name')
    chapters = Deadline.objects.filter(onlineclass=onlineclass).order_by('deadline').values_list('chapter', flat=True)
    problems = Problem.objects.filter(chapter__in=chapters)

    #Progress plot
    class_values = get_progress_per_problem(students, problems, onlineclass)
    passed, failed, skipped, no_attempts = class_values
    total_done = round(passed + failed + skipped)

    text = [str(total_done) + "%"]
    size = [50]
    hole = [0.9]
    progress_plot = create_progress_plot(1, [class_values], size, text, hole)

    # fig.update_layout(autosize=True,
    #                   height=280,
    #                   margin=dict(
    #                      l=10,
    #                      r=30,
    #                      b=0,
    #                      t=0,
    #                      pad=4
    #                   ),
    #                   legend=dict(
    #                   orientation="h",
    #                   xanchor='center',
    #                   x=0.5,
    #                   font=dict(family="Nunito",
    #                             size=16,
    #                             color='rgb(76,83,90)')),
    #                   hoverlabel=dict(bgcolor='white',
    #                                font_size=15,
    #                                font_family='Nunito'))


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
        deadline = Deadline.objects.filter(onlineclass=onlineclass, chapter=chapter).first().deadline

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

      prediction = predict_drop_out(student,onlineclass)

      student = {'name': student.first_name+' '+student.last_name,
                       'username': student.username,
                       'id': student.id,
                       'passed': user_passed,
                       'skipped': user_skipped,
                       'failed': user_failed,
                       'chapter_time': chapter_time,
                       'delays': delays,
                       'attempts': attempts,
                       'problem_time': problem_time,
                       'prediction': prediction}
      students_table.append(student)

    students_df = pd.DataFrame(students_table)
    students_df.dropna(subset = ['problem_time','passed','attempts'], inplace=True)


    names = []
    for student in students:
      names.append(student.first_name+' '+student.last_name)
    labels = []

    n=1
    for chapter in chapters:
      labels.append(n)
      n+=1

    def heatmap_height(names):
      height = 650
      x = len(names)
      if x > 34:
        height = x*20
      return height

    fig2 = go.Figure(data=go.Heatmap(
    	z=matrix1,
        x=labels,
        y=names,
        hoverinfo='none',
    colorscale=["rgba(33,150,243,0.2)", "rgb(33,150,243)"]))

    fig2.update_layout(height=heatmap_height(names),
                       width= 470,
                       plot_bgcolor='white',
                       xaxis=dict(fixedrange=True, tickmode='linear'),
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

    fig3.update_layout(height=heatmap_height(names),
                       width= 470,
                       xaxis=dict(fixedrange=True, tickmode='linear'),
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
      logs = UserLog.objects.filter(problem=problem, user_class=onlineclass, timestamp__gte=onlineclass.start_date)
      avg_time = None
      avg_attempts = None
      if logs.filter(outcome="P").count():
        passed_times = logs.filter(outcome="P").values_list('seconds_in_code', flat=True)
        if passed_times.count():
          avg_time = round(mean(passed_times)/60,2)

        problem_attempts = []
        for student in students:
          passed = logs.filter(user=student, outcome="P").order_by('timestamp')
          if passed.count():
            student_attempts = logs.filter(user=student,
                                           timestamp__lte=passed.first().timestamp).count()
            problem_attempts.append(student_attempts)
        avg_attempts = 0
        if len(problem_attempts):
          avg_attempts = round(mean(problem_attempts),2)

      problem_ids.append(str(problem.id)+" - "+problem.title)
      problem_times.append(avg_time)
      attempts.append(avg_attempts)


    fig4 = go.Figure(data=go.Scatter(x=problem_times, 
    								 y=attempts,
                     customdata=problem_ids,
                     hovertemplate='<b>%{customdata}</b><br>'+_('Attempts')+': %{y} ('+_('avg')+')<br>'+_('Time')+': %{x} min ('+_('avg')+')',
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
    		sizemode='diameter',
        sizemin=10,
        sizeref=50,
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




  #   chapter_table = []
  #   counter = 0
  #   for chapter in chapters:
  #     finished = 0
  #     for i in matrix1:
  #       n = i[counter]
  #       if n != None:
  #         finished += 1
        
  #     delays = 0
  #     for i in matrix2:
  #       n = i[counter]
  #       if n == 1:
  #         delays += 1

  #     progress = round(100*(delays+finished)/students.count())

  #     chapter_problems = problems.filter(chapter=chapter)

  #     chapter_times = []
  #     delays = 0
  #     attempts_list = []
  #     times_list = []
  #     for student in students:
  #       deadline = Deadline.objects.filter(onlineclass=onlineclass, chapter=chapter).first().deadline

  #       logs = UserLog.objects.filter(user=student,
  #                                     problem__in=chapter_problems,
  #                                     timestamp__gte=onlineclass.start_date).order_by('timestamp')
  #       if logs.count():
  #         first_log = logs.first().timestamp
  #       times = []
  #       for problem in chapter_problems:
  #         passed = UserLog.objects.filter(user=student,
  #                                         problem=problem,
  #                                         outcome="P",
  #                                         timestamp__gte=onlineclass.start_date).order_by('timestamp')
  #         if passed.count():
  #           first_passed = passed.first()
  #           problem_time = round(mean(list(passed.values_list('seconds_in_code', flat=True)))/60)
  #           times_list.append(problem_time)
  #           times.append(first_passed.timestamp)
  #           problem_attempts = logs.filter(problem=problem, timestamp__lte=first_passed.timestamp).count()
  #           attempts_list.append(problem_attempts)
  #       times.sort()
  #       if len(times) == chapter_problems.count():
  #         chapter_passed = times[-1]
  #         chapter_times.append((chapter_passed-first_log).days)
  #         if chapter_passed > deadline:
  #           delays += 1

  #     counter += 1


  #     chapter_time = None
  #     problem_time = None
  #     attempts = None

  #     if len(chapter_times):
  #       chapter_time = round(mean(chapter_times))
  #     if len(attempts_list):
  #       attempts = round(mean(attempts_list))
  #     if len(times_list):
  #       problem_time = round(mean(times_list))

  #     chapter = Chapter.objects.get(id=chapter)

  #     chapter_table.append({'label': chapter.label,
  #                           'id': chapter.id,
  #                           'progress': progress,
  #                           'chapter_time': chapter_time,
  #                           'delays': delays,
  #                           'attempts': attempts,
  #                           'problem_time': problem_time})

  #   chapters_df = pd.DataFrame(chapter_table)
  #   chapters_df.dropna(subset = ['problem_time','attempts'], inplace=True)
        



  #   #PLOT: chapters

  #   x = np.array(range(1,chapters_df['attempts'].count()+1))

  #   fig6 = make_subplots(specs=[[{"secondary_y": True}]])

  #   fig6.add_trace(go.Scatter(x=x, 
  #   						        y=chapters_df['attempts'],
  #               			  line=dict( 
  #               				  color='rgba(33,150,243,1)',
  #               				  width=4),
  #               			  mode='lines',
  #               			  name=_('Attempts'),
  #                       hovertemplate='<b>'+_('Chapter')+' %{x}</b><br>%{y} ('+_('avg')+')',
  #                       # error_y=dict(
  #                       #   type='percent',
  #                       #   value=15,
  #                       #   visible=True,
  #                       #   color='rgba(33,150,243,0.4)')
  #                       ),
  #                       secondary_y=False)

  #   fig6.add_trace(go.Scatter(x=x, 
  #   						        y=chapters_df['problem_time'],
  #               			  line=dict( 
  #               				  color='#4C4C4C',
  #               				  width=4,
  #               				  dash='dot'),
  #               			  mode='lines',
  #               			  name=_('Time'),
  #                       hovertemplate='<b>'+_('Chapter')+' %{x}</b><br>%{y} min ('+_('avg')+')',
  #                       # error_y=dict(
  #                       #   type='percent',
  #                       #   value=20,
  #                       #   visible=True,
  #                       #   color='rgba(0,0,0,0.4)')
  #                       ),
  #                       secondary_y=True)

  #   fig6.update_layout(height=300,
  #                       hoverlabel=dict(
  #                           bgcolor="white",
  #                           font_size=14,
  #                           font_family="Nunito",
  #                       ),
  #                      font=dict(family="Nunito",
  #                                size=14,
  #                                color='rgb(76,83,90)'),
  #   				           plot_bgcolor  = "rgba(0, 0, 0, 0)",
  #   	 			           paper_bgcolor = "rgba(0, 0, 0, 0)",
  #                      margin=dict(
  #                        l=10,
  #                        r=30,
  #                        b=10,
  #                        t=0,
  #                        pad=4
  #                     ),
  #                      legend=dict(
  #                      	orientation="h",
  #                      	yanchor="bottom",
  #                      	y=1.02,
  #                      	xanchor="right",
  #                      	x=1
  #                      	),
  #                     yaxis_tickmode = 'linear',
  #                     xaxis_showgrid=False,
  #                     yaxis_showgrid=False)
  #   fig6.update_yaxes(title_text=_('Attempts per problem'), secondary_y=False)
  #   fig6.update_yaxes(title_text=_('Time per problem (minutes)'), secondary_y=True)

  #   # fig4.update_traces(colorscale="hsv")

  #   chapters_plot = opy.plot(fig6,
		# output_type='div')


    context = { "title": 'Dashboard - '+onlineclass.name,
    "progress_plot": progress_plot,
    "heatmap_plot": heatmap_plot,
    "heatmap2_plot": heatmap2_plot,
    "problems_plot": problems_plot,
    "students_plot": students_plot,
    # "chapters_plot": chapters_plot,
    # "chapter_table": chapter_table,
    "students_table": students_table[-1::-1],
    "z": delays,
    'matrix1': matrix1
    }

    return context



def manager_dashboard():
    classes = OnlineClass.objects.filter(active=True)
    students = User.objects.filter(userprofile__user_class__in=classes).order_by('-first_name','-last_name')
    chapters = Deadline.objects.filter(onlineclass__in=classes).values_list('chapter', flat=True)
    problems = Problem.objects.filter(chapter__in=chapters)
    onlineclass = OnlineClass.objects.get(id=1)



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

    class_table = []
    matrix1 = []
    for onlineclass in classes:
      students = User.objects.filter(userprofile__user_class=onlineclass).order_by('-first_name','-last_name')
      delays = 0
      class_passed = 0
      class_skipped = 0
      class_failed = 0
      all_chapter_times = []
      all_attempts_list = []
      all_times_list = []
      all_line1 = []
      for student in students:
        #students progress
        class_passed += round(100*UserLogView.objects.filter(user=student,
                                            problem__in=problems,
                                            final_outcome='P').count()/problems.count())
        class_skipped += round(100*UserLogView.objects.filter(user=student,
                                            problem__in=problems,
                                            final_outcome='S').count()/problems.count())
        class_failed += round(100*UserLogView.objects.filter(user=student,
                                            problem__in=problems,
                                            final_outcome='F').count()/problems.count())

        chapter_times = []
        attempts_list = []
        times_list = []
        line1 = []
        for chapter in chapters:
          chapter_problems = problems.filter(chapter=chapter)

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
            line1.append((chapter_passed-first_log).days)

        if len(line1):
          all_line1.append(mean(line1))
        
        if len(chapter_times):
          all_chapter_times.extend(chapter_times)
        if len(attempts_list):
          all_attempts_list.extend(attempts_list)
        if len(times_list):
          all_times_list.extend(times_list)

      if len(all_chapter_times):
        chapter_time = round(mean(all_chapter_times))
      if len(all_attempts_list):
        attempts = round(mean(all_attempts_list))
      if len(all_times_list):
        problem_time = round(mean(all_times_list))

      onlineclass = {'name': onlineclass.name,
                  'id': onlineclass.id,
                  'chapter_time': chapter_time,
                  'delays': delays,
                  'attempts': attempts,
                  'problem_time': problem_time}
      class_table.append(onlineclass)

    class_df = pd.DataFrame(class_table)
    class_df.dropna(subset = ['problem_time','attempts'], inplace=True)


    names = []
    for onlineclass in classes:
      names.append(onlineclass.name)
      
    labels = []
    n=1
    for chapter in chapters:
      labels.append(n)
      n+=1

    fig2 = go.Figure(data=go.Heatmap(
      z=matrix1,
        x=labels,
        y=names,
        hoverinfo='none',
    colorscale=["rgba(33,150,243,0.2)", "rgb(33,150,243)"]))

    fig2.update_layout(height=650,
                       plot_bgcolor='white',
                       xaxis=dict(fixedrange=True, tickmode='linear'),
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
          avg_time = round(mean(passed_times)/60,2)

        problem_attempts = []
        for student in students:
          passed = logs.filter(user=student, outcome="P").order_by('timestamp')
          if passed.count():
            student_attempts = logs.filter(user=student,
                                           timestamp__lte=passed.first().timestamp).count()
            problem_attempts.append(student_attempts)
        avg_attempts = 0
        if len(problem_attempts):
          avg_attempts = round(mean(problem_attempts),2)

      problem_ids.append(str(problem.id)+" - "+problem.title)
      problem_times.append(avg_time)
      attempts.append(avg_attempts)


    fig4 = go.Figure(data=go.Scatter(x=problem_times, 
                     y=attempts,
                     customdata=problem_ids,
                     hovertemplate='<b>%{customdata}</b><br>'+_('Attempts')+': %{y} ('+_('avg')+')<br>'+_('Time')+': %{x} min ('+_('avg')+')',
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

    problems_plot2 = opy.plot(fig4,
    output_type='div')




    #PLOT: classes

    # size = list(class_df['problem_time']+0.1)
    # x = class_df['passed']
    # y = class_df['attempts']

    # if not len(size):
    #   size = [1]
      
    # fig5 = go.Figure(data=[go.Scatter(
    #   x=x,
    #   y=y,
    #   customdata=class_df['name'],
    #   hovertemplate='<b>%{customdata}</b><br>'+_('Solved problems')+': %{x}%<br>'+_('Attempts')+': %{y} ('+_('avg')+')<br>'+_('Time')+': %{marker.size:.0f} min ('+_('avg')+')',
    #   mode='markers',
    #   name = '',
    #   marker=dict(
    #     size=size,
    #     sizemode='diameter',
    #     sizemin=10,
    #     sizeref=50,
    #     color='rgba(33,150,243,0.9)'
    #     )
    #   )])

    # fig5.update_layout(height=330,
    #                    font=dict(family="Nunito",
    #                              size=14,
    #                              color='rgb(76,83,90)'),
    #                    hoverlabel=dict(
    #                         bgcolor="white",
    #                         font_size=14,
    #                         font_family="Nunito",
    #                    ),
    #                    plot_bgcolor  = "rgba(0, 0, 0, 0)",
    #                    paper_bgcolor = "rgba(0, 0, 0, 0)",
    #                    margin=dict(
    #                      l=10,
    #                      r=10,
    #                      b=10,
    #                      t=0,
    #                      pad=4
    #                   ),
    #                   xaxis_showgrid=False,
    #                   yaxis_showgrid=False,
    #                   yaxis_title=_('Attempts'),
    #                   xaxis_title=_('Solved problems')+' (%)',)

    # students_plot = opy.plot(fig5,
    # output_type='div')




    chapter_table = []
    counter = 0
    for chapter in chapters:
      # finished = 0
      # for i in matrix1:
      #   n = i[counter]
      #   if n != None:
      #     finished += 1
        
      # delays = 0
      # for i in matrix2:
      #   n = i[counter]
      #   if n == 1:
      #     delays += 1

      # counter += 1

      # progress = round(100*(delays+finished)/students.count())

      chapter_problems = problems.filter(chapter=chapter)
      all_chapter_times = []
      all_attempts_list = []
      all_times_list = []
      delays = 0

      for onlineclass in classes:
        students = User.objects.filter(userprofile__user_class=onlineclass).order_by('-first_name','-last_name')
        chapter_times = []
        attempts_list = []
        times_list = []
        for student in students:

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
            deadline = Deadline.objects.filter(onlineclass=onlineclass, chapter=chapter)
            if deadline.count():
              if chapter_passed > deadline.first().deadline:
                delays += 1


        if len(chapter_times):
          all_chapter_times.extend(chapter_times)
        if len(attempts_list):
          all_attempts_list.extend(attempts_list)
        if len(times_list):
          all_times_list.extend(times_list)

      if len(all_chapter_times):
        chapter_time = round(mean(all_chapter_times))
      if len(all_attempts_list):
        attempts = round(mean(all_attempts_list))
      if len(times_list):
        problem_time = round(mean(all_times_list))

      chapter = Chapter.objects.get(id=chapter)

      chapter_table.append({'label': chapter.label,
                            'id': chapter.id,
                            # 'progress': progress,
                            'chapter_time': chapter_time,
                            'delays': delays,
                            'attempts': attempts,
                            'problem_time': problem_time})

    chapters_df = pd.DataFrame(chapter_table)
    chapters_df.dropna(subset = ['problem_time','attempts'], inplace=True)
        



    #PLOT: chapters

    x = np.array(range(1,chapters_df['attempts'].count()+1))

    fig6 = make_subplots(specs=[[{"secondary_y": True}]])

    fig6.add_trace(go.Scatter(x=x, 
                        y=chapters_df['attempts'],
                        line=dict( 
                          color='rgba(33,150,243,1)',
                          width=4),
                        mode='lines',
                        name=_('Attempts'),
                        hovertemplate='<b>'+_('Chapter')+' %{x}</b><br>%{y} ('+_('avg')+')',
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
                        hovertemplate='<b>'+_('Chapter')+' %{x}</b><br>%{y} min ('+_('avg')+')',
                        # error_y=dict(
                        #   type='percent',
                        #   value=20,
                        #   visible=True,
                        #   color='rgba(0,0,0,0.4)')
                        ),
                        secondary_y=True)

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
                      yaxis_tickmode = 'linear',
                      xaxis_showgrid=False,
                      yaxis_showgrid=False)
    fig6.update_yaxes(title_text=_('Attempts per problem'), secondary_y=False)
    fig6.update_yaxes(title_text=_('Time per problem (minutes)'), secondary_y=True)

    # fig4.update_traces(colorscale="hsv")

    chapters_plot = opy.plot(fig6,
    output_type='div')


    context = { "title": 'Dashboard',
    "progress_plot": progress_plot,
    "heatmap_plot": heatmap_plot,
    "problems_plot": problems_plot,
    # "students_plot": students_plot,
    "chapters_plot": chapters_plot,
    "chapter_table": chapter_table,
    "students_table": class_table[-1::-1],
    "z": delays,
    'matrix1': matrix1
    }

    return context
