from questions.models import (Professor, Problem, Deadline, User, UserLogView, OnlineClass)
import csv
import pickle
from datetime import datetime

from questions.get_dashboards import predict_drop_out

def count_on_time_exercises(user, chapters, onlineclass):
    on_time_list = []
    for c in chapters:
        problems = Problem.objects.filter(chapter=c)
        deadline = Deadline.objects.filter(chapter=c,
                                        onlineclass=onlineclass).first().deadline
        on_time_exercises = UserLogView.objects.filter(user=user,
                                                    problem__in=problems,
                                                    final_outcome='P',
                                                    timestamp__gte=onlineclass.start_date,
                                                    timestamp__lte=deadline)
        on_time_list.append(on_time_exercises.count())
    return sum(on_time_list)



classes = [119,102,103,97,99,100,101,104,109,110,98,112,113,115,117]

for id in classes:
    onlineclass = OnlineClass.objects.get(pk=id)
    professor = onlineclass.professor.first().user

    f = open("questions/class_analysis/results.csv","w+")
    writer = csv.writer(f)

    writer.writerow(['turma','aluno','previsao','exercicios_resolvidos'])

    professors = Professor.objects.all().values_list('user')
    students = User.objects.filter(userprofile__user_class=onlineclass).exclude(pk__in=professors)

    i=1
    for student in students:
        predict = predict_drop_out(student.id, onlineclass, datetime(2022,2,1))
        on_time_exercises = count_on_time_exercises(student, [17,19], onlineclass)
        try:
            if predict < 7:
                writer.writerow([student.userprofile.user_class.name,student.first_name,predict,on_time_exercises])
                i+=1
        except:
            pass
            
f.close()