import logging
from questions.models import Problem, Solution, TestCase, Language
import json
import copy
from django.utils.translation import gettext as _

LOGGER = logging.getLogger(__name__)

# Modules than can be used inside the solution
import math


def get_problem(problem_id):
    #try:
    # Get problem, test cases and solution
    problem = Problem.objects.get(pk=problem_id)
    problem.content = problem.content.replace('\`','`').replace('`','\`').replace('(<','(').replace('>)',')')
    options = problem.options.split("\r\n\r\n")
    LOGGER.debug("Got problem %d", problem.id)
    all_test_cases = TestCase.objects.filter(problem=problem)
    all_test_cases = [json.loads(test.content) for test in all_test_cases]
    LOGGER.debug("Got test cases %s for problem %d", all_test_cases, problem.id)
    #solution = Solution.objects.filter(problem=problem, ignore=False).order_by('?')[0]
    python_lang = Language.objects.get(name='Python')
    solution_python = Solution.objects.filter(problem=problem, ignore=False, language=python_lang).order_by('?')[0]
    
    dictSolutions = {}
    solutions = Solution.objects.filter(problem=problem, ignore=False)  #Pegando soluções de todas as linguagens
    for solution in solutions:
        lang_txt = Language.objects.get(pk=solution.language.id).name
        test_cases_lang = TestCase.objects.filter(problem=problem, languages=solution.language)
        test_cases_lang = [json.loads(test_case.content) for test_case in test_cases_lang]
        dictSolutions[lang_txt] = {"solution": solution.content, "text": solution.tip, "return_type": solution.return_type, "func": solution.header, "test_cases": ["%s" % item for item in test_cases_lang]}
    dictSolutions = json.dumps(dictSolutions)
    
    """
    expected_results = []

    # Transform solution into python function
    if problem.question_type == "C":
        function_obj = compile(solution_python.content, 'solution', 'exec')
        exec(function_obj)

        # For each test case, get expected output
        for args_case in test_case:
            # Make list deepcopy
            args = copy.deepcopy(args_case)
            result = eval(solution_python.header)(*args)
            if type(result) == str:
                expected_results.append("'"+str(result)+"'")
            else:
                expected_results.append(str(result))
        #print(expected_results)
        #except Problem.DoesNotExist:
            #raise Problem.DoesNotExist
    """

    context = {
        "problem": problem,
        "options": options,
        "solution": solution_python.content,
        "solutions": dictSolutions,
        "test_case": ["%s" % item for item in all_test_cases],
        #"expected_results": expected_results,
        "tip": solution_python.tip,
        "header": solution_python.header,
        "title": _('Problem')
    }

    return context
