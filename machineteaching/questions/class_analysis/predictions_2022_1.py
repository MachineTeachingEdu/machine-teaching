from questions.models import (Professor, UserLog, User, OnlineClass)
from questions.get_dashboards import predict_drop_out
from datetime import datetime

classes = [120,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,140,141,142,143]
date = datetime(2022,6,22)
semester = '2022_1'

for id in classes:
    onlineclass = OnlineClass.objects.get(pk=id)
    professors = Professor.objects.all().values_list('user')
    students = User.objects.filter(userprofile__user_class=onlineclass).exclude(pk__in=professors)
    if onlineclass.professor.count():
        professor = onlineclass.professor.last().user
        
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
                f.write(i+'. '+student.first_name+' '+student.last_name+': '+last_log+' ('+student.email+')\n')
                i+=1
        except:
            pass
    f.close()
