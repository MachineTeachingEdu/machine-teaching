from questions.models import (Professor, UserLog, User, OnlineClass)
from questions.get_dashboards import predict_drop_out
from datetime import datetime

classes = [119,102,103,97,99,100,101,104,109,110,98,112,113,115,117]
date = datetime(2022,2,1)
semester = '2021_2'

for id in classes:
    onlineclass = OnlineClass.objects.get(pk=id)
    professors = Professor.objects.all().values_list('user')
    students = User.objects.filter(userprofile__user_class=onlineclass).exclude(pk__in=professors)
        
    f = open("questions/class_analysis/"+semester+"/"+professor.first_name+" - "+onlineclass.name+".txt","w+")
    f.write(onlineclass.name.upper()+'\nProfessor: '+professor.first_name=' '+professor.last_name+' ('+professor.email+')\n\n')
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
                f.write(i+'. '+student.first_name+' '+student.last_name+': '+last_log+' ('+student.email+')\n')
                i+=1
        except:
            pass
    f.close()
