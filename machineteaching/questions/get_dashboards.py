import dash
import dash_html_components as html
import plotly.graph_objects as go
import plotly.offline as opy
from plotly.subplots import make_subplots

from statistics import mean

from questions.models import (Chapter, Problem, UserLog,
                             UserLogView, User, ExerciseSet, Deadline)
from django.utils.translation import gettext as _
import logging

LOGGER = logging.getLogger(__name__)


def dashboard(user, professor=False):
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
