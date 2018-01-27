from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

from .models import Problem

# Create your views here.
def index(request):
    return render(request, 'questions/index.html')

@permission_required('questions.can_add_problem', raise_exception=True)
def show_problem(request, problem_id):
    try:
        problem = Problem.objects.get(pk=problem_id)
    except Problem.DoesNotExist:
        raise Http404("Problem does not exist")
    return render(request, 'questions/show_problem.html', {'problem': problem})

def get_random_problem(request):
    problem = Problem.objects.random()
    return render(request, 'questions/show_problem.html', {'problem': problem})

def get_next_problem(request):
    ## TODO: Get user current status and calculate next best problem
    problem = Problem.objects.random()
    return render(request, 'questions/show_problem.html', {'problem': problem})
