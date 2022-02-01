from questions.models import (Professor, UserLog, User, OnlineClass)
from questions.get_dashboards import predict_drop_out

# classes = [119,102,103,97,99,100,101,104,109,110,98,112,113,115,117]
classes = [1,2]

for id in classes:
    onlineclass = OnlineClass.objects.get(pk=id)
    professor = onlineclass.professor.first().user

    f = open(f"questions/class_analysis/{professor.first_name} - {onlineclass.name}.txt","w+")
    f.write(f'{onlineclass.name.upper()}\nProfessor: {professor.first_name} {professor.last_name} ({professor.email})\n\n')
    f.write('Através da análise de dados da ferramenta Machine Teaching, foi identificado que os seguintes alunos estão em risco de abandono da disciplina Comp1:\n\n')

    professors = Professor.objects.all().values_list('user')
    students = User.objects.filter(userprofile__user_class=onlineclass).exclude(pk__in=professors)
    i=1
    for student in students:
        try:
            predict = predict_drop_out(student.id, onlineclass)
        except:
            pass
        if predict < 7:
            try:
                last_log = "último exercício resolvido em "+UserLog.objects.filter(user=student).order_by('timestamp').last().timestamp.strftime("%m/%d/%Y")
            except:
                last_log = "nenhum exercício resolvido"
            f.write(f'{i}. {student.first_name} {student.last_name}: {last_log} ({student.email})\n')
            i+=1
    f.write('\n\n')
f.close()
