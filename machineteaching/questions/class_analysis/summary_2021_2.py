from questions.models import (Professor, Problem, Deadline, User, UserLogView, OnlineClass)
import csv
from datetime import datetime

import pandas as pd

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


classes = [102,103,97,99,100,101,104,109,110,98,112,113,115,117]
# classes = [1]
date = datetime(2022,2,1)
semester = '2021_2'

f = open("questions/class_analysis/"+semester+"/summary_"+semester+".csv","w")
writer = csv.writer(f)
writer.writerow(['turma','aluno','previsao','exercicios_resolvidos_8_9','clf_1','clf_2','clf_3'])

# Lista de alunos com as classficações
for id in classes:
    onlineclass = OnlineClass.objects.get(pk=id)
    professors = Professor.objects.all().values_list('user')
    profiles = UserLogView.objects.filter(user_class=onlineclass).values("user").distinct()
    students = User.objects.filter(pk__in=profiles).exclude(pk__in=professors).order_by("first_name","last_name")

    i=1
    for student in students:
        try:
            predict = predict_drop_out(student.id, onlineclass, date)
            on_time_exercises = count_on_time_exercises(student, [17,19], onlineclass)

            results = []
            for clf in [(6.5,4),(7.2,7),(8.9,7)]:
                C = clf[0]
                K = clf[1]
                if predict < C:
                    if on_time_exercises < K:
                        result = "VP"
                    else:
                        result = "FP"
                else:
                    if on_time_exercises < K:
                        result = "FN"
                    else:
                        result = "VN"
                results.append(result)

            writer.writerow([student.id,
                             onlineclass.name,
                             student.first_name+" "+student.last_name,
                             predict,
                             on_time_exercises,
                             result[0],
                             result[1],
                             result[2]])
            i+=1
        except:
            pass
            
f.close()

# Lista de classificadores com métricas
f = open("questions/class_analysis/"+semester+"/classifiers_"+semester+".csv","w+")
writer = csv.writer(f)
writer.writerow(["clf","VP","VN","FP","FN","TFP","TVP","TVN","F1_P","F1_N"])

df = pd.read_csv("questions/class_analysis/"+semester+"/summary_"+semester+".csv")

for i in 1,2,3:
    col = "clf_"+str(i)
    VP = len(df[df[col] == 'VP'])
    VN = len(df[df[col] == 'VN'])
    FP = len(df[df[col] == 'FP'])
    FN = len(df[df[col] == 'FN'])
    TFP = FP/(FP+VN)
    TVP = VP/(VP+FN)
    TVN = VN/(FP+VN)
    try:
        VPP = VP/(VP+FP)
        F1_P = 2*VPP*TVP/(VPP+TVP)
    except:
        VPP = nan
        F1_P = nan
    try:
        VPN = VN/(FN+VN)
        F1_N = 2*VPN*TVN/(VPN+TVN)
    except:
        VPN = nan
        F1_N = nan

    writer.writerow([i, VP, VN, FP, FN, TFP, TVP, TVN, F1_P, F1_N])