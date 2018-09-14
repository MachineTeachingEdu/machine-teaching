from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

from .models import Problem, Solution
from questions.forms import UserLogForm
from questions.get_problem import get_problem

# Create your views here.
def index(request):
    return render(request, 'questions/index.html')

@permission_required('questions.can_add_problem', raise_exception=True)
def show_problem(request, problem_id):
    try:
        context = get_problem(problem_id)
    except Problem.DoesNotExist:
        raise Http404("Problem does not exist")
    return render(request, 'questions/show_problem.html', context)

def get_start_problem(request):
    # View to define starting problem. For the moment, let's always start with
    # the same problem
    try:
        context = get_problem(679)
    except Problem.DoesNotExist:
        raise Http404("Problem does not exist")
    return render(request, 'questions/show_problem.html', context)

def get_random_problem(request):
    problem = Problem.objects.random()
    solution = Solution.objects.filter(problem=problem)[0]
    return render(request, 'questions/show_problem.html', {'problem': problem,
                                                           'solution': solution})

def get_next_problem(request):
    ## TODO: Get user current status and calculate next best problem
    # View to define starting problem. For the moment, let's always start with
    # the same problem
    try:
        context = get_problem(141)
    except Problem.DoesNotExist:
        raise Http404("Problem does not exist")
    return render(request, 'questions/show_problem.html', context)
#    problem = Problem.objects.random()
#    solution = Solution.objects.filter(problem=problem)[0]
#    return render(request, 'questions/show_problem.html', {'problem': problem,
#                                                           'solution': solution})

def save_user_log(request):
    form = UserLogForm(request.GET)
    if form.is_valid():
        log = form.save(commit=False)
        log.user = request.user
        log.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})
