from questions.models import OnlineClass, Chapter, Deadline, UserProfile
from django.http import JsonResponse
import logging
from django.conf import settings

LOGGER = logging.getLogger(__name__)


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
                                                                  flat=True
                                                                  ).order_by('deadline')
        available_chapters = []
        # Get one at a time to keep it sorted
        for chapter in deadline_chapters:
            available_chapters.append(Chapter.objects.get(pk=chapter))
        LOGGER.debug("Available chapters: %s" % available_chapters)
        context.update({'student_course': student_course, 
                        'available_chapters': available_chapters})
    return context

def show_satisfaction_form(request):
    return {'SHOW_SATISFACTION_FORM': settings.SHOW_SATISFACTION_FORM}