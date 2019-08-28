# from django.http import Http404, JsonResponse
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
# from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Lower
# import random
import json
from functools import wraps
import time

from questions.models import (Problem, Solution, UserLog, UserProfile,
                              Professor, OnlineClass, UserLogView)
from questions.forms import UserLogForm, SignUpForm, OutcomeForm
from questions.get_problem import get_problem
from questions.strategies import STRATEGIES_FUNC

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
            user.refresh_from_db()  # load the instance created by the signal
            LOGGER.debug(form.cleaned_data.get('professor'))
            professor = Professor.objects.get(pk=int(form.cleaned_data.get(
                'professor')))
            user.userprofile.professor = professor
            user.userprofile.programming = form.cleaned_data.get('programming')
            user.userprofile.accepted = form.cleaned_data.get('accepted')
            user_class = OnlineClass.objects.get(pk=int(form.cleaned_data.get(
                'onlineclass')))
            user.userprofile.user_class = user_class
            user.userprofile.save()
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('start')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# @permission_required('questions.can_add_problem', raise_exception=True)
@login_required
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
    if request.user.userprofile.sequential:
        strategy = 'sequential'
    else:
        strategy = 'random'
        # TODO: Temp hack while EER strategy is not updated with new clusters and problems
        ## strategy = request.user.userprofile.strategy
    problem_id = STRATEGIES_FUNC[strategy](request.user)
    LOGGER.debug("Got problem %s", problem_id)

    if not problem_id:
        return render(request, 'questions/finished.html', {})
    context = get_problem(problem_id)
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
    past_problems = UserLog.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'questions/past_problems.html', {
        'past_problems': past_problems, 'user': request.user})

@permission_required('questions.view_userlogview', raise_exception=True)
@login_required
def get_student_solutions(request, id, chapter=None, problem=None):
    user = User.objects.get(pk=id)
    userlog = UserLog.objects.filter(user_id=id)
    if chapter:
        userlog = userlog.filter(problem__chapter=chapter)
    if problem:
        userlog = userlog.filter(problem=problem)
    return render(request, 'questions/past_problems.html', {
        'past_problems': userlog, 'student': student})

@login_required
def get_chapter_problems(request):
    problems = Problem.objects.filter(chapter__isnull=False).order_by(
            '-chapter_id', 'id')
    # Get exercise where student passed
    passed = UserLog.objects.filter(user=request.user, outcome='P'
            ).values_list('problem_id', flat=True).distinct()
    skipped = UserLog.objects.filter(user=request.user, outcome='S'
            ).values_list('problem_id', flat=True).distinct()
    failed = UserLog.objects.filter(user=request.user, outcome='F'
            ).values_list('problem_id', flat=True).distinct()
    return render(request, 'questions/chapters.html', {
        'problems': problems,
        'passed': passed,
        'skipped': skipped,
        'failed': failed
        })

@permission_required('questions.view_userlogview', raise_exception=True)
@login_required
def show_outcome(request):
    outcomes = []
    if request.method == 'POST':
        form = OutcomeForm(request.POST, user=request.user)
        if form.is_valid():
            onlineclass = form.cleaned_data['onlineclass']
            chapter = form.cleaned_data['chapter']

            # Get class problems
            problems = list(Problem.objects.filter(chapter=chapter).order_by(
                    'id').values_list('id', flat=True))

            # Get latest student outcome for every student in class
            students = UserLogView.objects.filter(
                user__userprofile__user_class=onlineclass,
                problem_id__in=problems).order_by(
                    Lower('user__first_name').asc(),
                    Lower('user__last_name').asc(),
                    'problem_id').values('user_id',
                        'user__first_name', 'user__last_name',
                        'problem_id', 'final_outcome', 'timestamp')

            # For each student in class, let's organize it in a table
            start = time.time()
            if students.count():
                current_student = students[0]["user_id"]
                student_name = "%s %s" % (students[0]["user__first_name"],
                                          students[0]["user__last_name"])
                outcome_student = [(None, None)]*len(problems)
                for student in students:
                    if current_student == student["user_id"]:
                        outcome_student[
                            problems.index(student["problem_id"])
                        ] = (student["final_outcome"],
                             student["timestamp"].isoformat())
                    # Previous student is finished, lets start a new one
                    else:
                        only_outcomes = list(zip(*outcome_student))[0]
                        student_row = {
                            "name": (student_name, current_student),
                            "outcomes": outcome_student,
                            "total": {
                                "P": only_outcomes.count("P"),
                                "F": only_outcomes.count("F"),
                                "S": only_outcomes.count("S")
                            }
                        }
                        outcomes.append(student_row)
                        # Get new student
                        outcome_student = [(None,None)]*len(problems)
                        current_student = student["user_id"]
                        student_name = "%s %s" % (student["user__first_name"],
                                                  student["user__last_name"])
                        outcome_student[
                            problems.index(student["problem_id"])
                        ] = (student["final_outcome"],
                             student["timestamp"].isoformat())
                # Add last student
                outcome_student[
                    problems.index(student["problem_id"])
                ] = (student["final_outcome"],
                        student["timestamp"].isoformat())
                student_row = {"name": (student_name, current_student),
                                "outcomes": outcome_student,
                                "total": {"P": outcome_student.count("P"),
                                            "F": outcome_student.count("F"),
                                            "S": outcome_student.count("S")}}
                outcomes.append(student_row)
            end = time.time()
            LOGGER.info("Elapsed time: %d" % (end-start))
    else:
        form = OutcomeForm()
        problems = []
    form.fields['onlineclass'].queryset = OnlineClass.objects.filter(
        professor__user=request.user).order_by('name')
    LOGGER.info("Available classes: %s" % form.fields['onlineclass'].queryset)
    LOGGER.info("Showing students and outcomes: %s" % json.dumps(outcomes))
    return render(request, 'questions/outcomes.html',
                  {'form': form, 'problems': problems, 'outcomes':outcomes})


@login_required
@must_be_yours(model=UserLog)
def get_user_solution(request, id):
    userlog = UserLog.objects.get(pk=id)
    return render(request, 'questions/past_solutions.html', {'log': userlog})

@login_required
def update_strategy(request):
    try:
        sequential = request.GET['sequential']
        user = UserProfile.objects.get(user=request.user)
        user.sequential = bool(int(sequential))
        user.save()
        return JsonResponse({'status': 'success'})
    except Exception:
        return JsonResponse({'status': 'failed'})
