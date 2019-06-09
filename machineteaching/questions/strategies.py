from django.conf import settings
import random
from random import randint
import numpy as np
import pickle

from questions.models import Problem, Solution, UserLog, UserModel, Cluster
from questions.sampling import get_next_sample

CLUSTER_IDX = list(Cluster.objects.values_list('pk', flat=True).order_by('pk'))

## STRATEGIES (random or eer)
def random_strategy(user):
    # Set seed so we can always return to the same problem, even if page is refreshed
    random.seed(user.userprofile.seed)

    ## Get random problem from available list that the user has not done yet
    done_problems = UserLog.objects.filter(user=user, outcome__in=("S", "P")).values_list('problem__id', flat=True).distinct()
    problems = list(Problem.objects.filter(solution__ignore=False).values_list('id', flat=True).order_by('id'))
    random.shuffle(problems)

    # Remove all done problems and get the next one
    for done in done_problems:
        problems.remove(done)

    return problems[0]

def eer_strategy(user):
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
    skipped_problems = UserLog.objects.filter(user=user, outcome="S").values_list('problem', flat=True).order_by('problem__id')
    skipped_solutions = Solution.objects.filter(problem__in=skipped_problems, ignore=False).values_list('id', 'cluster').order_by('id')
    for item in skipped_solutions:
        sol_id, cluster = item
        sol_idx = all_solutions_idx.index(sol_id)
        L.append(sol_idx)

    passed_problems = UserLog.objects.filter(user=user, outcome="P").values_list('problem', flat=True).order_by('problem__id')
    passed_solutions = Solution.objects.filter(problem__in=passed_problems, ignore=False).values_list('id', 'cluster').order_by('id')
    for item in passed_solutions:
        sol_id, cluster = item
        sol_idx = all_solutions_idx.index(sol_id)
        X[sol_idx, CLUSTER_IDX.index(cluster)] = 1
        L.append(sol_idx)

    # Save user model
    user_model = UserModel.objects.get(user=user)
    user_model.distribution = X
    user_model.save()

    # Create Y as a document_topic matrix. For the first version, each document belongs to one topic
    Y = np.zeros(settings.DOC_TOPIC_SHAPE)
    clusters = all_solutions.values_list('cluster', flat=True).order_by('id')
    for idx, cluster_value in enumerate(clusters):
        Y[idx, CLUSTER_IDX.index(cluster_value)] = 1

    # Unpickle similarity matrix (W)
    with open('similarity.pkl', 'rb') as pklfile:
        W = pickle.load(pklfile)

    # Get next sample
    solution_idx = get_next_sample(X, Y, W, L)
    solution_id = all_solutions_idx[solution_idx]
    problem_id = Solution.objects.get(pk=solution_id).problem.pk

    return problem_id

STRATEGIES_FUNC = {
    "random": random_strategy,
    "eer": eer_strategy
}
