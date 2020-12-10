# from django.http import Http404, JsonResponse
import logging
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.messages import success, error
#from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Lower
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
# import random
import json
from functools import wraps
import time
from questions.models import (Problem, Solution, UserLog, UserProfile,
                              Professor, OnlineClass, UserLogView, Chapter,
                              Deadline, UserLogError, ExerciseSet)
from questions.forms import (UserLogForm, SignUpForm, OutcomeForm, ChapterForm,
                             ProblemForm, SolutionForm, PageAccessForm, InteractiveForm)
from questions.get_problem import get_problem
from questions.get_dashboards import get_student_dashboard
from questions.strategies import STRATEGIES_FUNC

import csv

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


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('start')
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.username = form.cleaned_data.get('email')
            user.save()
            user.refresh_from_db()  # load the instance created by the signal
            LOGGER.debug(form.cleaned_data.get('professor'))
            # Deprecated: student is now related to class, not to professor
            # Kept in model for backwards compatibility
            # professor = Professor.objects.get(pk=int(form.cleaned_data.get(
            #     'professor')))
            # user.userprofile.professor = professor
            user.userprofile.programming = form.cleaned_data.get('programming')
            user.userprofile.accepted = True
            user.userprofile.read = True
            user_class = OnlineClass.objects.get(
                class_code=form.cleaned_data.get('class_code'))
            user.userprofile.user_class = user_class
            user.userprofile.save()
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('start')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'title':_('Create account'),'form': form})


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
        return render(request, 'questions/finished.html', {'title': _('Finished')})
    context = get_problem(problem_id)
    return render(request, 'questions/show_problem.html', context)

@login_required
def save_user_log(request):
    form = UserLogForm(request.POST)
    LOGGER.debug("Log received for user %s with outcome %s: %s",
                 request.user,
                 request.POST['outcome'],
                 request.POST['solution'])
    if form.is_valid():
        log = form.save(commit=False)
        log.user = request.user
        log.save()
        return JsonResponse({'status': 'success'})
    LOGGER.debug("Log failed")
    return JsonResponse({'status': 'failed'})

@login_required
def get_past_problems(request):
    logs = UserLog.objects.filter(user=request.user).order_by('-timestamp')
    past_problems = []
    for log in logs:
        error = UserLogError.objects.filter(userlog=log).values_list('error')
        past_problems.append({'log': log, 'error': error})
    return render(request, 'questions/past_problems.html', {
        'title': _('Past problems'), 'past_problems': past_problems, 'user': request.user})

@permission_required('questions.view_userlogview', raise_exception=True)
@login_required
def get_student_solutions(request, id, chapter=None, problem=None):
    user = User.objects.get(pk=id)
    logs = UserLog.objects.filter(
        user_id=id, timestamp__gte=user.userprofile.user_class.start_date)
    if chapter:
        logs = logs.filter(problem__chapter=chapter)
    if problem:
        logs = logs.filter(problem=problem)
    past_problems = []
    for log in logs.order_by('-timestamp'):
        error = UserLogError.objects.filter(userlog=log).values_list('error')
        past_problems.append({'log': log, 'error': error})
    return render(request, 'questions/past_problems.html', {
        'title': user.first_name+' '+user.last_name, 'past_problems': past_problems, 'student': user})

@login_required
def get_chapter_problems(request):
    onlineclass = request.user.userprofile.user_class
    LOGGER.debug("Online class: %s" % onlineclass)
    available_chapters = Deadline.objects.filter(onlineclass=onlineclass
                                                ).values_list('chapter',
                                                              flat=True).order_by('-deadline')
    LOGGER.debug("Available chapters: %s" % available_chapters)

    chapters = []
    problems = []
    for i in range(0,len(available_chapters),3):
        chapter = Chapter.objects.get(pk=available_chapters[i])
        chapters.append(chapter)
        problems.append(ExerciseSet.objects.filter(chapter=chapter).order_by('order','-id'))
    col_1 = list(zip(chapters,problems))

    chapters = []
    problems = []
    for i in range(1,len(available_chapters),3):
        chapter = Chapter.objects.get(pk=available_chapters[i])
        chapters.append(chapter)
        problems.append(ExerciseSet.objects.filter(chapter=chapter).order_by('order','-id'))
    col_2 = list(zip(chapters,problems))

    chapters = []
    problems = []
    for i in range(2,len(available_chapters),3):
        chapter = Chapter.objects.get(pk=available_chapters[i])
        chapters.append(chapter)
        problems.append(ExerciseSet.objects.filter(chapter=chapter).order_by('order','-id'))
    col_3 = list(zip(chapters,problems))

    # Get exercise where student passed
    userlog = UserLog.objects.filter(
        user=request.user,
        timestamp__gte=request.user.userprofile.user_class.start_date)
    passed = userlog.filter(outcome='P').values_list('problem_id', flat=True
                                              ).distinct()
    skipped = userlog.filter(outcome='S').values_list('problem_id', flat=True
                                              ).distinct()
    failed = userlog.filter(outcome='F').values_list('problem_id', flat=True
                                              ).distinct()

    return render(request, 'questions/chapters.html', {
        'title': _('Chapters'),
        'chapters': [col_1,col_2,col_3],
        'passed': passed,
        'skipped': skipped,
        'failed': failed,
        'available_chapters': available_chapters
        })

@login_required
@csrf_exempt
# TODO: por que é preciso tirar o CSRF?
def show_chapter(request, chapter):
    chapter = Chapter.objects.get(pk=chapter)
    LOGGER.debug("Chapter: %s" % chapter)
    problems = ExerciseSet.objects.filter(chapter=chapter).order_by('order', '-id')
    LOGGER.debug("Chapter problems: %s" % problems)
    onlineclass = request.user.userprofile.user_class
    LOGGER.debug("Online class: %s" % onlineclass)
    # Get farthest deadline
    deadline = Deadline.objects.filter(onlineclass=onlineclass,
                                       chapter=chapter).order_by('-deadline')
    if deadline:
        deadline = deadline[0].deadline
    else:
        deadline = 0

    LOGGER.debug("Deadline: %s" % deadline)
    userlogs = UserLog.objects.filter(problem__in=Problem.objects.filter(chapter=chapter).distinct())
    errors = UserLogError.objects.filter(userlog__in=userlogs).values_list('error')
    counter = {}
    for error in errors:
        if error in counter:
            counter[error] += 1
        else:
            counter[error] = 1
    main_errors = sorted(counter, key=counter.get, reverse=True)[:2]

    # Get exercise where student passed
    userlog = UserLog.objects.filter(
        user=request.user,
        timestamp__gte=request.user.userprofile.user_class.start_date)
    passed = userlog.filter(outcome='P').values_list('problem_id', flat=True
                                              ).distinct()
    skipped = userlog.filter(outcome='S').values_list('problem_id', flat=True
                                              ).distinct()
    failed = userlog.filter(outcome='F').values_list('problem_id', flat=True
                                              ).distinct()

    if request.method == 'POST':
        problem_ids = str(list(request.POST)[0])
        for index, pk in enumerate(problem_ids.split(','), start=1):
            exerciseset = ExerciseSet.objects.get(chapter=chapter, problem=int(pk))
            exerciseset.order = index
            exerciseset.save()
        return HttpResponse('')

    return render(request, 'questions/show_chapter.html', {
        'title': chapter,
        'chapter': chapter,
        'deadline': deadline,
        'problems': problems,
        'errors': main_errors,
        'passed': passed,
        'skipped': skipped,
        'failed': failed
        })

@csrf_exempt
# TODO: por que é preciso tirar o CSRF?
@permission_required('questions.view_userlogview', raise_exception=True)
@login_required
def new_chapter(request):
    chapter = None
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.save()
            date = form.cleaned_data['deadline'].strftime('%Y-%m-%d 23:59:59')
            deadline = Deadline(chapter=chapter, deadline=date)
            deadline.save()
            classes = OnlineClass.objects.filter(professor__user=request.user)
            for item in classes:
                item.chapter.add(chapter)
                deadline.onlineclass.add(item)
            deadline.save()

            return redirect('show_chapter', chapter=chapter.id)
    else:
        form = ChapterForm()
    return redirect('chapters')

@login_required
def show_outcome(request):
    # TODO: link direto na interface
    if not request.user.has_perm('questions.view_userlogview'):
        context = get_student_dashboard(request.user)
        return render(request, 'questions/student_dashboard.html', context)

    outcomes = []
    onlineclass = None
    if request.method == 'POST':
        form = OutcomeForm(request.POST, user=request.user)
        if form.is_valid():
            onlineclass = form.cleaned_data['onlineclass']
            chapter = form.cleaned_data['chapter']

            # Get class problems
            problems_all = Problem.objects.filter(chapter=chapter).order_by(
                    'title', 'id')
            problems = list(problems_all.values_list('id', flat=True))

            # Get latest student outcome for every student in class
            students = UserLogView.objects.filter(
                user__userprofile__user_class=onlineclass,
                problem_id__in=problems, timestamp__gte=onlineclass.start_date
            ).order_by(Lower('user__first_name').asc(),
                       Lower('user__last_name').asc(),
                       'user_id',
                       'problem__title',
                       'problem_id').values('user_id',
                                            'user__first_name',
                                            'user__last_name',
                                            'problem_id',
                                            'final_outcome',
                                            'timestamp')

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
                             timezone.localtime(student[
                                 "timestamp"]).strftime("%Y-%m-%d %H:%M:%S"))
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
                             timezone.localtime(student[
                                 "timestamp"]).strftime("%Y-%m-%d %H:%M:%S"))
                # Add last student
                outcome_student[
                    problems.index(student["problem_id"])
                ] = (student["final_outcome"],
                     timezone.localtime(student[
                         "timestamp"]).strftime("%Y-%m-%d %H:%M:%S"))
                only_outcomes = list(zip(*outcome_student))[0]
                student_row = {"name": (student_name, current_student),
                                "outcomes": outcome_student,
                                "total": {"P": only_outcomes.count("P"),
                                            "F": only_outcomes.count("F"),
                                            "S": only_outcomes.count("S")}}
                outcomes.append(student_row)
            end = time.time()
            LOGGER.info("Elapsed time: %d" % (end-start))
    else:
        form = OutcomeForm()
        problems_all = []
    form.fields['onlineclass'].queryset = OnlineClass.objects.filter(
        professor__user=request.user).order_by('name')
    LOGGER.info("Available classes: %s" % form.fields['onlineclass'].queryset)
    LOGGER.info("Showing students and outcomes: %s" % json.dumps(outcomes))
    return render(request, 'questions/outcomes.html',
                  {'title': _('Outcomes'),'form': form, 'problems': problems_all, 'outcomes':outcomes, 'class':onlineclass})


@login_required
@must_be_yours(model=UserLog)
def get_user_solution(request, id):
    userlog = UserLog.objects.get(pk=id)
    context = get_problem(userlog.problem_id)
    context.update({'log': userlog, 'title': _('Solution')})
    return render(request, 'questions/past_solutions.html', context)


@permission_required('questions.view_userlogview', raise_exception=True)
def show_solutions(request, problem_id, class_id):
    logs = UserLog.objects.filter(
                user__userprofile__user_class=class_id,
                problem_id=problem_id).order_by('user__first_name',
                                                'user__last_name',
                                                'user_id',
                                                '-timestamp').values('user_id',
                                                                     'user__first_name',
                                                                     'user__last_name',
                                                                     'solution',
                                                                     'outcome',
                                                                     'timestamp')
    students = []
    if logs.count():
        current_student = logs[0]["user_id"]
        student_name = "%s %s" % (logs[0]["user__first_name"],
                                  logs[0]["user__last_name"])
        student = {'name':student_name,'logs':[]}
        for log in logs:
            if log["user_id"] != current_student:
                students.append(student)
                current_student = log["user_id"]
                student_name = "%s %s" % (log["user__first_name"],
                                          log["user__last_name"])
                student = {'name':student_name,'logs':[]}
            student['logs'].append(log)
        students.append(student)
    problem = get_problem(problem_id)

    return render(request, 'questions/solutions.html', {'title': problem['problem'].title,
                                                        'problem': problem,
                                                        'students': students})


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

@permission_required('questions.view_userlogview', raise_exception=True)
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Student', 'Problem', 'Outcome', 'Timestamp'])
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
                problem_id__in=problems, timestamp__gte=onlineclass.start_date
            ).order_by(Lower('user__first_name').asc(),
                       Lower('user__last_name').asc(),
                       'problem_id').values('user__first_name',
                                            'user__last_name',
                                            'problem_id',
                                            'problem__title',
                                            'final_outcome',
                                            'timestamp')

            for student in students:
                outcomes = {'P':'Passed','F':'Failed','S':'Skipped'}
                userlog = [str(student['user__first_name'])+' '+student['user__last_name'],
                    str(student['problem_id'])+' - '+student['problem__title'],
                    outcomes[student['final_outcome']],
                    timezone.localtime(student['timestamp']).strftime("%Y-%m-%d %H:%M:%S")]
                writer.writerow(userlog)

    else:
        form = OutcomeForm()
        problems = []
    form.fields['onlineclass'].queryset = OnlineClass.objects.filter(
        professor__user=request.user).order_by('name')
    LOGGER.info("Available classes: %s" % form.fields['onlineclass'].queryset)
    LOGGER.info("Showing students and outcomes: %s" % json.dumps(outcomes))

    response['Content-Disposition'] = 'attachment; filename="userlog.csv"'

    return response

@permission_required('questions.view_userlogview', raise_exception=True)
def new_problem(request, chapter=None):
    if request.method == 'POST':
        problem_form = ProblemForm(request.POST)
        solution_form = SolutionForm(request.POST)
        if problem_form.is_valid() and solution_form.is_valid():
            problem = problem_form.save(commit=False)
            problem.question_type = solution_form.cleaned_data.get('question_type')
            problem.save()
            solution = solution_form.save(commit=False)
            solution.content = solution_form.cleaned_data.get('solution')
            solution.problem_id = problem.id
            solution.save()
            chapter = list(problem_form.cleaned_data.get('chapter'))[0]
            order = problem_form.cleaned_data.get('order')
            if not order:
                problems = ExerciseSet.objects.filter(chapter=chapter).values_list('order')
                order = len(list(problems))+1
            exerciseset = ExerciseSet(chapter=chapter, problem=problem, order=order)
            exerciseset.save()

            success(request, 'The problem was added')

            return redirect('show_chapter', chapter=chapter.id)
        else:
            error(request, 'The problem was not added')

    else:
        problem_form = ProblemForm()
        solution_form = SolutionForm()

    return render(request, 'questions/new_problem.html',{
        'title': _('New problem'),
        'chapter': chapter,
        'problem_form': problem_form,
        'solution_form': solution_form
        })

@login_required
# TODO: por que é preciso tirar o CSRF?
@csrf_exempt
def save_access(request):
    form = PageAccessForm(request.POST)
    if form.is_valid():
        access = form.save(commit=False)
        access.user = request.user
        access.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})

@login_required
@csrf_exempt
# TODO: por que é preciso tirar o CSRF?
def save_interactive(request):
    form = InteractiveForm(request.POST)
    if form.is_valid():
        interactive = form.save(commit=False)
        interactive.user = request.user
        interactive.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})
