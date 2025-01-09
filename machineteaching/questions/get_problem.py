import logging
from questions.models import Problem, Solution, TestCase, Language
import json
from django.utils.translation import gettext as _
from django.conf import settings

LOGGER = logging.getLogger(__name__)

"""
def get_problem(problem_id):
    # Get problem, test cases and solution
    problem = Problem.objects.get(pk=problem_id)
    problem.content = problem.content.replace('\`','`').replace('`','\`').replace('(<','(').replace('>)',')')
    options = problem.options.split("\r\n\r\n")
    LOGGER.debug("Got problem %d", problem.id)
    all_test_cases = TestCase.objects.filter(problem=problem)
    all_test_cases = [json.loads(test.content) for test in all_test_cases]
    LOGGER.debug("Got test cases %s for problem %d", all_test_cases, problem.id)
    python_lang = Language.objects.get(name='Python')
    solution_python = Solution.objects.filter(problem=problem, ignore=False, language=python_lang).order_by('?')[0]
    
    dictSolutions = {}
    solutions = Solution.objects.filter(problem=problem, ignore=False)  #Pegando soluções de todas as linguagens
    for solution in solutions:
        lang_txt = Language.objects.get(pk=solution.language.id).name
        test_cases_lang = TestCase.objects.filter(problem=problem, languages=solution.language)
        #for testcase in test_cases_lang:
        #    print(testcase.content)
        test_cases_lang = [json.loads(test_case.content) for test_case in test_cases_lang]
        dictSolutions[lang_txt] = {"solution": solution.content, "tip": solution.tip, "return_type": solution.return_type, "func": solution.header, "test_cases": ["%s" % item for item in test_cases_lang]}
    dictSolutions = json.dumps(dictSolutions)
    worker_node_host = settings.WORKER_NODE_HOST
    worker_node_port = settings.WORKER_NODE_PORT

    context = {
        "problem": problem,
        "options": options,
        #"solution": solution_python.content,
        "solutions": dictSolutions,
        "test_case": ["%s" % item for item in all_test_cases],
        #"tip": solution_python.tip,
        "header": solution_python.header,
        "title": _('Problem'),
        "worker_node_host": worker_node_host,
        "worker_node_port": worker_node_port,
    }

    return context
"""


def get_problem(problem_id):
    problem = Problem.objects.get(pk=problem_id)
    problem.content = problem.content.replace('\`','`').replace('`','\`').replace('(<','(').replace('>)',')')
    options = problem.options.split("\r\n\r\n")
    LOGGER.debug("Got problem %d", problem.id)
    
    dictSolutions = {}
    solutions = Solution.objects.filter(problem=problem, ignore=False)  #Pegando soluções de todas as linguagens
    for solution in solutions:
        lang_txt = Language.objects.get(pk=solution.language.id).name
        dictSolutions[lang_txt] = {"solution": solution.content, "tip": solution.tip}    #Lembrar de apagar o campo "solution" ao fazer commit
    dictSolutions = json.dumps(dictSolutions)

    context = {
        "problem": problem,
        "options": options,
        "solutions": dictSolutions,
        "title": _('Problem'),
    }

    return context
