import logging
import random
from django.conf import settings
import numpy as np
import pickle

from questions.models import Problem, Solution, UserLog, UserModel, Cluster, ExerciseSet, Deadline
from questions.sampling import get_next_sample

LOGGER = logging.getLogger(__name__)


# STRATEGIES (random or eer)
def random_strategy(user):
    # Set seed so we can always return to the same problem, even if page is refreshed
    random.seed(user.userprofile.seed)

    # Get random problem from available list that the user has not done yet
    done_problems = UserLog.objects.filter(user=user, outcome__in=("S", "P"),
            problem__solution__ignore=False).values_list('problem__id', flat=True).distinct()
    LOGGER.debug("User %s has done problems: %s", user.username, done_problems)
    problems = list(Problem.objects.filter(solution__ignore=False).values_list('id', flat=True).distinct().order_by('id'))
    LOGGER.debug("Analisying %d problems", len(problems))
    random.shuffle(problems)

    # Remove all done problems and get the next one
    for done in done_problems:
        LOGGER.debug("Removing problem %d", done)
        problems.remove(done)

    LOGGER.debug("Remaining problems: %s", problems)
    try:
        problem_id = problems[0]
    except IndexError:
        problem_id = None
    return problem_id


def eer_strategy(user):
    # TODO: Get user current status and calculate next best problem
    # View to define starting problem. For the moment, let's always start with
    # the same problem

    # Set CLUSTER_IDX
    CLUSTER_IDX = list(Cluster.objects.values_list('pk', flat=True).order_by('pk'))

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

def sequential_strategy(user):
    # Get user solutions
    user_passed = UserLog.objects.filter(user=user, outcome__in=["P", "S"]).values_list(
            'problem', flat=True)

    # Go to next available problem
    try:
        problem_id = ExerciseSet.objects.filter(chapter__in=Deadline.objects.filter(onlineclass=user.userprofile.user_class
                                                ).values_list('chapter',
                                                              flat=True)).exclude(
                problem__in=user_passed).order_by('chapter','order').values_list('problem')[0][0]
        LOGGER.debug("Selecting problem %d from sequential strategy", problem_id)
    except IndexError:
        problem_id = None
        LOGGER.debug("No problems left in sequential strategy")

    return problem_id


STRATEGIES_FUNC = {
    "random": random_strategy,
    "eer": eer_strategy,
    "sequential": sequential_strategy
}

