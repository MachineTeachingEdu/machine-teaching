import logging
from django.shortcuts import render, redirect
from django.db.models import Count
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
from functools import wraps
import random

from questions.models import Solution, Cluster
from evaluation.models import SolutionConcept, Concept, Intruder, TopicName
from evaluation.forms import (ConceptForm, UserNoPasswordForm,
                              IntruderForm, TopicNameForm)


LOGGER = logging.getLogger(__name__)


# Custom decorator
def login_required_nopwd(model=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            return redirect('evaluation_index')
        return _wrapped_view
    return decorator


# Create your views here.
def index(request):
    # If user is not authenticated or doesn't exist, create and/or login
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = UserNoPasswordForm(request.POST)
            if form.is_valid():
                user, created = User.objects.get_or_create(
                    username=form.cleaned_data['name'],
                    first_name=form.cleaned_data['name'],
                    email=form.cleaned_data['email']
                )
                login(request, user)
            else:
                return render(
                    request, '400.html',
                    {"error": "Name or e-mail already in the database"})
        else:
            form = UserNoPasswordForm()
            return render(request, 'evaluation/index.html',
                          {"form": form})
    # if user is already logged in, redirect to concept page
    return redirect('choose_concepts')


@login_required_nopwd(model=Concept)
def choose_concepts(request):
    """ Retrieve solution with less evaluations to show to evaluators """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ConceptForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            for item in form.cleaned_data['concepts']:
                new_concept = SolutionConcept()
                new_concept.user = request.user
                new_concept.solution = Solution.objects.get(
                    pk=request.POST['solution_id'])
                new_concept.concept = Concept.objects.get(pk=item)
                new_concept.save()
        else:
            return render(request, '400.html',
                          {"error": "Concepts can't be empty"})

    # Count how many problems that user has done
    user_count = User.objects.filter(
        username=request.user.username).annotate(
            user_count=Count(
                'solutionconcept__solution', distinct=True))[0].user_count

    # If there are still problems to solve, render a new problem
    if user_count < settings.MAX_EVAL_COUNT:
        solution = Solution.objects.filter(ignore=False).annotate(
            num_concepts=Count('solutionconcept')).order_by('num_concepts')[0]
        form = ConceptForm()

        return render(request, 'evaluation/choose_concepts.html',
                      {'form': form, 'solution': solution,
                       'user_count': user_count,
                       'max_eval_count': settings.MAX_EVAL_COUNT})
    # Otherwise, go to next exercise
    else:
        return redirect('intruder')


def intruder(request):
    """ Retrieve 3 solutions from the same topic and an intruder. """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = IntruderForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            for idx, solution in enumerate(request.POST['solutions_ids'].split(',')):
                intruder = Intruder()
                intruder.user = request.user
                intruder.cluster = Cluster.objects.get(
                    pk=request.POST['cluster'])
                intruder.solution = Solution.objects.get(pk=solution)

                if (idx+1) == int(form.cleaned_data['intruder']):
                    intruder.intruder = True
                else:
                    intruder.intruder = False
                intruder.save()

    # Get and exclude clusters already analyzed by the user
    analyzed_clusters = Intruder.objects.filter(
        user=request.user).values_list('cluster', flat=True).distinct()
    clusters = Cluster.objects.exclude(pk__in=analyzed_clusters)

    # If there are still clusters to analyze
    if clusters.count() > 0:
        # Shuffle clusters
        cluster = sorted(clusters,
                         key=lambda x: random.random())[0]

        # Get 3 random solutions for the cluster
        solutions = Solution.objects.filter(ignore=False, cluster=cluster)
        solutions = sorted(solutions,
                           key=lambda x: random.random())[:3]

        # Get 4th solution outside the cluster
        intruder_solution = Solution.objects.filter(
            ignore=False, cluster__isnull=False).exclude(cluster=cluster)
        intruder_solution = [sorted(intruder_solution,
                                    key=lambda x: random.random())[0]]

        # Merge querysets and shuffle them for visualization
        solution_queryset = solutions + intruder_solution
        solution_queryset = sorted(solution_queryset,
                                   key=lambda x: random.random())

        form = IntruderForm()
        return render(request, 'evaluation/intruder.html', {
            "solutions": solution_queryset,
            "solutions_ids": ",".join(
                [str(item.pk) for item in solution_queryset]),
            "cluster": cluster.pk,
            "user_count": analyzed_clusters.count()+1,
            "total_count": analyzed_clusters.count() + clusters.count(),
            "form": form})
    else:
        return redirect('topic_name')


def topic_name(request):
    """ Retrieve 4 solutions from the same topic and ask for a name. """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TopicNameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            topic = TopicName()
            topic.user = request.user
            topic.label = form.cleaned_data['name']
            topic.cluster = Cluster.objects.get(pk=request.POST['cluster'])
            topic.save()

    # Get and exclude clusters already analyzed by the user
    analyzed_clusters = TopicName.objects.filter(
        user=request.user).values_list('cluster', flat=True).distinct()
    clusters = Cluster.objects.exclude(pk__in=analyzed_clusters)

    # If there are still clusters to analyze
    if clusters.count() > 0:
        # Shuffle clusters
        cluster = sorted(clusters,
                         key=lambda x: random.random())[0]

        # Get 4 random solutions for the cluster
        solutions = Solution.objects.filter(ignore=False, cluster=cluster)
        solutions = sorted(solutions,
                           key=lambda x: random.random())[:4]

        form = TopicNameForm()
        return render(request, 'evaluation/topic_name.html', {
            "solutions": solutions,
            "cluster": cluster.pk,
            "user_count": analyzed_clusters.count()+1,
            "total_count": analyzed_clusters.count() + clusters.count(),
            "form": form})
    else:
        return redirect('thank_you')
