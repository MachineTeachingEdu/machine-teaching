from questions.models import (Professor, UserLog, User, OnlineClass, UserLogView, Deadline)
from questions.get_dashboards import predict_drop_out
from datetime import datetime
import csv

classes = [102,103,97,99,100,101,104,109,110,98,112,113,115,117]
date = datetime(2022,2,1)
semester = '2021_2'

r = open("questions/class_analysis/"+semester+"/classes_"+semester+".csv","w+")
writer = csv.writer(r)
writer.writerow(['id','nome','professor','ultima_aula','modelo','n_alunos','n_risco'])

for id in classes:
    onlineclass = OnlineClass.objects.get(pk=id)
    professors = Professor.objects.all().values_list('user')
    profiles = UserLogView.objects.filter(user_class=onlineclass).values("user").distinct()
    students = User.objects.filter(pk__in=profiles).exclude(pk__in=professors).order_by("first_name","last_name")

    completed_chapter = Deadline.objects.filter(onlineclass=onlineclass,
                                                deadline__lte=date).order_by('deadline').last().chapter

    if onlineclass.professor.count():
        professor = onlineclass.professor.exclude(pk__in=[319,344]).exclude(assistant=True).last().user
            
        f = open("questions/class_analysis/"+semester+"/"+professor.first_name+" - "+onlineclass.name.replace("/","_")+".txt","w+")
        f.write(onlineclass.name.upper()+'\nProfessor: '+professor.first_name+' '+professor.last_name+' ('+professor.email+')\n\n')
        f.write('Através da análise de dados da ferramenta Machine Teaching, foi identificado que os seguintes alunos estão em risco de abandono da disciplina Comp1:\n\n')


        i=1
        for student in students:
            predict = predict_drop_out(student.id, onlineclass, date)
            
            try:
                if predict < 7:
                    try:
                        last_log = "último exercício resolvido em "+UserLog.objects.filter(user=student).order_by('timestamp').last().timestamp.strftime("%m/%d/%Y")
                    except:
                        last_log = "nenhum exercício resolvido"
                    f.write(str(i)+'. '+student.first_name+' '+student.last_name+': '+last_log+' ('+student.email+')\n')
                    i+=1
            except:
                pass
        writer.writerow([id,onlineclass.name,professor.first_name,completed_chapter.label,completed_chapter.drop_out_model,students.count(),i])
        f.close()
