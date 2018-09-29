from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings
import numpy as np
import pickle

from questions.models import Problem, Solution, UserLog, UserModel
from questions.forms import UserLogForm
from questions.get_problem import get_problem
from questions.sampling import get_next_sample

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

@login_required
def get_start_problem(request):
    # View to define starting problem. For the moment, let's always start with
    # the same problem
    try:
        context = get_problem(679)
    except Problem.DoesNotExist:
        raise Http404("Problem does not exist")
    return render(request, 'questions/show_problem.html', context)

@login_required
def get_random_problem(request):
    problem = Problem.objects.random()
    solution = Solution.objects.filter(problem=problem)[0]
    return render(request, 'questions/show_problem.html', {'problem': problem,
                                                           'solution': solution})

@login_required
def get_next_problem(request):
    ## TODO: Get user current status and calculate next best problem
    # View to define starting problem. For the moment, let's always start with
    # the same problem

    # Create X as an empty belief state (X is the machine's model of the student's distribution)
    X = np.zeros(settings.DOC_TOPIC_SHAPE)

    # Get Solution ids in a list, to serve as an index reference to X
    all_solutions = Solution.objects.filter(ignore=False)
    all_solutions_idx = list(all_solutions.values_list('id', flat=True).order_by('id'))

    # Set L as an unlabelled set
    L = []

    # Update with what the student already knows
    # Get skipped problems
    skipped_problems = UserLog.objects.filter(user=request.user, outcome="S").values_list('problem', flat=True).order_by('problem__id')
    skipped_solutions = Solution.objects.filter(problem__in=skipped_problems, ignore=False).values_list('id', 'cluster').order_by('id')
    for item in skipped_solutions:
        sol_id, cluster = item
        sol_idx = all_solutions_idx.index(sol_id)
        L.append(sol_idx)

    passed_problems = UserLog.objects.filter(user=request.user, outcome="P").values_list('problem', flat=True).order_by('problem__id')
    passed_solutions = Solution.objects.filter(problem__in=passed_problems, ignore=False).values_list('id', 'cluster').order_by('id')
    for item in passed_solutions:
        sol_id, cluster = item
        sol_idx = all_solutions_idx.index(sol_id)
        X[sol_idx, cluster] = 1
        L.append(sol_idx)

    # Save user model
    user_model = UserModel.objects.get(user=request.user)
    user_model.distribution = X
    user_model.save()

    # Create Y as a document_topic matrix. For the first version, each document belongs to one topic
    Y = np.zeros(settings.DOC_TOPIC_SHAPE)
    clusters = all_solutions.values_list('cluster', flat=True).order_by('id')
    for idx, cluster_value in enumerate(clusters):
        Y[idx, cluster_value] = 1

    # Unpickle similarity matrix (W)
    with open('similarity.pkl', 'rb') as pklfile:
        W = pickle.load(pklfile)

    # Get next sample
    solution_idx = get_next_sample(X, Y, W, L)
    solution_id = all_solutions_idx[solution_idx]
    problem_id = Solution.objects.get(pk=solution_id).problem.pk

    try:
        context = get_problem(problem_id)
    except Problem.DoesNotExist:
        raise Http404("Problem does not exist")
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
