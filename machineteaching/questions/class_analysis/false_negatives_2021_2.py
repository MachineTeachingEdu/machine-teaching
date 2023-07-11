from questions.models import (Professor, Problem, Deadline, User, UserLogView, OnlineClass)
import csv
from datetime import datetime

from questions.get_dashboards import predict_drop_out

def count_on_time_exercises(user, chapters, onlineclass):
    on_time_list = []
    for c in chapters:
        try:
            problems = Problem.objects.filter(chapter=c)
            deadline = Deadline.objects.filter(chapter=c,
                                            onlineclass=onlineclass).first().deadline
            on_time_exercises = UserLogView.objects.filter(user=user,
                                                        problem__in=problems,
                                                        final_outcome='P',
                                                        timestamp__gte=onlineclass.start_date,
                                                        timestamp__lte=deadline)
            on_time_list.append(on_time_exercises.count())
        except:
            pass
    return sum(on_time_list)

def count_exercises(user, chapters, onlineclass):
    on_time_list = []
    for c in chapters:
        try:
            problems = Problem.objects.filter(chapter=c)
            deadline = Deadline.objects.filter(chapter=c,
                                            onlineclass=onlineclass).first().deadline
            on_time_exercises = UserLogView.objects.filter(user=user,
                                                        problem__in=problems,
                                                        final_outcome='P',
                                                        timestamp__gte=onlineclass.start_date)
            on_time_list.append(on_time_exercises.count())
        except:
            pass
    return sum(on_time_list)


classes = [119,102,103,97,99,100,101,104,109,110,98,112,113,115,117]
date = datetime(2022,2,1)
semester = '2021_2'

f = open("questions/class_analysis/"+semester+"/false_negatives_"+semester+".csv","w+")
writer = csv.writer(f)
writer.writerow(['turma','aluno','previsao','exercicios_resolvidos_8_9','aula_2','aula_2_on_time','aula_3','aula_3_on_time','aula_4','aula_4_on_time','aula_3_on_time','aula_4','aula_4_on_time','aula_5_on_time','aula_5','aula_6_on_time','aula_6_on_time','aula_7','aula_7_on_time'])


for id in classes:
    onlineclass = OnlineClass.objects.get(pk=id)
    professors = Professor.objects.all().values_list('user')
    students = User.objects.filter(userprofile__user_class=onlineclass).exclude(pk__in=professors)
    profiles = UserLogView.objects.filter(user_class=onlineclass).values("user").distinct()
    students = User.objects.filter(pk__in=profiles).exclude(pk__in=professors).order_by("first_name","last_name")

    i=1
    for student in students:
        predict = predict_drop_out(student.id, onlineclass, date)
        on_time_exercises = count_on_time_exercises(student, [17,19], onlineclass)

        try:
            if predict >= 7 and on_time_exercises < 7:

                aula_2 = count_exercises(student, [20], onlineclass)
                aula_3 = count_exercises(student, [12], onlineclass)
                aula_4= count_exercises(student, [13], onlineclass)
                aula_5 = count_exercises(student, [25], onlineclass)
                aula_6 = count_exercises(student, [26], onlineclass)
                aula_7 = count_exercises(student, [16], onlineclass)
                
                on_time_2 = count_on_time_exercises(student, [20], onlineclass)
                on_time_3 = count_on_time_exercises(student, [12], onlineclass)
                on_time_4= count_on_time_exercises(student, [13], onlineclass)
                on_time_5 = count_on_time_exercises(student, [25], onlineclass)
                on_time_6 = count_on_time_exercises(student, [26], onlineclass)
                on_time_7 = count_on_time_exercises(student, [16], onlineclass)
        
                writer.writerow([student.userprofile.user_class.name,
                                 student.first_name,
                                 predict,
                                 on_time_exercises,
                                 aula_2,
                                 on_time_2,
                                 aula_3,
                                 on_time_3,
                                 aula_4,
                                 on_time_4,
                                 aula_5,
                                 on_time_5,
                                 aula_6,
                                 on_time_6,
                                 aula_7,
                                 on_time_7])
                i+=1
        except:
            pass
            
f.close()