from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
import json

from .models import Problem, Solution, TestCase

# Create your views here.
def index(request):
    return render(request, 'questions/index.html')

@permission_required('questions.can_add_problem', raise_exception=True)
def show_problem(request, problem_id):
    try:
        # Get problem, test cases and solution
        problem = Problem.objects.get(pk=problem_id)
        test_case = TestCase.objects.filter(problem=problem)
        test_case = [json.loads(test.content) for test in test_case]
        solution = Solution.objects.filter(problem=problem, ignore=False)[0]

        # Transform solution into python function
        function_obj = compile(solution.content, 'solution', 'exec')
        exec(function_obj)

        # For each test case, get expected output
        expected_results = []
        for args in test_case:
            expected_results.append(str(eval(solution.header)(*args)))

    except Problem.DoesNotExist:
        raise Http404("Problem does not exist")
    return render(request, 'questions/show_problem.html', {
        'problem': problem, 'test_case': test_case,
        'expected_results': expected_results,
        'tip': solution.tip, 'header': solution.header})

def get_random_problem(request):
    problem = Problem.objects.random()
    solution = Solution.objects.filter(problem=problem)[0]
    return render(request, 'questions/show_problem.html', {'problem': problem,
                                                           'solution': solution})

def get_next_problem(request):
    ## TODO: Get user current status and calculate next best problem
    problem = Problem.objects.random()
    solution = Solution.objects.filter(problem=problem)[0]
    return render(request, 'questions/show_problem.html', {'problem': problem,
                                                           'solution': solution})
