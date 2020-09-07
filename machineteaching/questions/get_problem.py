import logging
from questions.models import Problem, Solution, TestCase
import json

LOGGER = logging.getLogger(__name__)

def get_problem(problem_id):
    #try:
    # Get problem, test cases and solution
    problem = Problem.objects.get(pk=problem_id)
    options = problem.options.split("\r\n\r\n")
    LOGGER.debug("Got problem %d", problem.id)
    test_case = TestCase.objects.filter(problem=problem)
    test_case = [json.loads(test.content) for test in test_case]
    LOGGER.debug("Got test cases %s for problem %d", test_case, problem.id)
    solution = Solution.objects.filter(problem=problem, ignore=False).order_by('?')[0]
    expected_results = []

    # Transform solution into python function
    if problem.question_type == "C":
        function_obj = compile(solution.content, 'solution', 'exec')
        exec(function_obj)

        # For each test case, get expected output
        for args in test_case:
            expected_results.append(str(eval(solution.header)(*args)))
        #print(expected_results)
        #except Problem.DoesNotExist:
            #raise Problem.DoesNotExist

    context = {
        "problem": problem,
        "options": options,
        "solution": solution.content,
        "test_case": ["%s" % item for item in test_case],
        "expected_results": expected_results,
        "tip": solution.tip,
        "header": solution.header
    }

    return context
