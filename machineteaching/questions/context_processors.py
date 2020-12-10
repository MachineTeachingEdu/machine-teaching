from questions.models import OnlineClass, Chapter, Deadline

def context(request):
    if request.user.is_authenticated:
        onlineclass = request.user.userprofile.user_class
        deadline_chapters = Deadline.objects.filter(onlineclass=onlineclass
                                                    ).values_list('chapter',
                                                                  flat=True)
        available_chapters = Chapter.objects.filter(id__in=deadline_chapters).order_by('-deadline')
        return {'available_chapters': available_chapters}
    else:
    	return {}