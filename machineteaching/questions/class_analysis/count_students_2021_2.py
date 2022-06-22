from questions.models import (Professor, Problem, Deadline, User, UserLogView, OnlineClass)

classes = [119,102,103,97,99,100,101,104,109,110,98,112,113,115,117]
students = User.objects.filter(userprofile__user_class__in=classes)
print(students.count())
