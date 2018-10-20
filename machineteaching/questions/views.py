#from django.http import Http404, JsonResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.core.exceptions import PermissionDenied
import random
from functools import wraps

from questions.models import Problem, Solution, UserLog, UserModel
from questions.forms import UserLogForm, SignUpForm
from questions.get_problem import get_problem
from questions.strategies import STRATEGIES_FUNC

#Custom decorator
def must_be_yours(model=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            #user = request.user
            #print user.id
            pk = kwargs["id"]
            obj = model.objects.get(pk=pk)
            if not (obj.user == request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Create your views here.
def index(request):
    return render(request, 'questions/index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.username = form.cleaned_data.get('email')
            user.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.userprofile.professor = form.cleaned_data.get('professor')
            user.userprofile.programming = form.cleaned_data.get('programming')
            user.userprofile.accepted = form.cleaned_data.get('accepted')
            user.userprofile.save()
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('start')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@permission_required('questions.can_add_problem', raise_exception=True)
def show_problem(request, problem_id):
    #try:
    context = get_problem(problem_id)
    #except Problem.DoesNotExist:
        #raise Http404("Problem does not exist")
    return render(request, 'questions/show_problem.html', context)

#@login_required
#def get_start_problem(request):
    ## View to define starting problem. For the moment, let's always start with
    ## the same problem
    #try:
        #context = get_problem(679)
    #except Problem.DoesNotExist:
        #raise Http404("Problem does not exist")
    #return render(request, 'questions/show_problem.html', context)

@login_required
def get_random_problem(request):
    problem = Problem.objects.random()
    solution = Solution.objects.filter(problem=problem)[0]
    return render(request, 'questions/show_problem.html', {'problem': problem,
                                                           'solution': solution})

@login_required
def get_next_problem(request):
    strategy = request.user.userprofile.strategy
    problem_id = STRATEGIES_FUNC[strategy](request.user)
    #try:
    context = get_problem(problem_id)
    #except Problem.DoesNotExist:
        #raise Http404("Problem does not exist")
        #raise DoesNotExist
    return render(request, 'questions/show_problem.html', context)

@login_required
def save_user_log(request):
    form = UserLogForm(request.GET)
    if form.is_valid():
        log = form.save(commit=False)
        log.user = request.user
        log.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})

@login_required
def get_past_problems(request):
    past_problems = UserLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'questions/past_problems.html', {'past_problems': past_problems})

@login_required
@must_be_yours(model=UserLog)
def get_user_solution(request, id):
    userlog = UserLog.objects.get(pk=id)
    return render(request, 'questions/past_solutions.html', {'log': userlog})
