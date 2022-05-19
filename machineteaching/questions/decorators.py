from functools import wraps
import logging
from questions.models import Professor
from django.core.exceptions import PermissionDenied

LOGGER = logging.getLogger(__name__)

# Custom decorator
def must_be_yours(model=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # user = request.user
            # print user.id
            pk = kwargs["id"]
            obj = model.objects.get(pk=pk)
            # Must be yours or from your student
            is_professor = Professor.objects.filter(user=request.user)
            LOGGER.info("Logged user is professor: %s" % bool(is_professor))
            # Test if user is professor and if student is in his/her class
            user_professor = is_professor and (obj.user.userprofile.user_class in is_professor[0].prof_class.all())
            LOGGER.info("Logged user is student professor: %s" % bool(user_professor))
            if not (obj.user == request.user) and not user_professor:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """ 

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper