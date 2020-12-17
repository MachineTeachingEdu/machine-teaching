from questions.models import OnlineClass, Chapter, Deadline, UserProfile
from django.http import JsonResponse

def context(request):
    context = {}
    if request.user.is_authenticated:
        try:
            course = request.GET['course']
            user = UserProfile.objects.get(user=request.user)
            user.course = course
            user.save()
        except:
        	pass
        
        student_course = request.user.userprofile.course
        onlineclass = request.user.userprofile.user_class
        deadline_chapters = Deadline.objects.filter(onlineclass=onlineclass
                                                    ).values_list('chapter',
                                                                  flat=True)
        available_chapters = Chapter.objects.filter(id__in=deadline_chapters).order_by('-deadline')
        context.update({'student_course': student_course, 'available_chapters': available_chapters})
    return context