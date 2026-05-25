import logging
from questions.models import Problem, Solution, TestCase, Language
import json
from django.utils.translation import gettext as _
from django.conf import settings

LOGGER = logging.getLogger(__name__)

def get_problem(problem_id):
    problem = Problem.objects.get(pk=problem_id)
    problem.content = problem.content.replace('\`','`').replace('`','\`').replace('(<','(').replace('>)',')')
    options = problem.options.split("\r\n\r\n")
    LOGGER.debug("Got problem %d", problem.id)
    
    dictSolutions = {}
    solutions = Solution.objects.filter(problem=problem, ignore=False)  #Pegando soluções de todas as linguagens
    for solution in solutions:
        lang_txt = Language.objects.get(pk=solution.language.id).name
        #dictSolutions[lang_txt] = {"solution": solution.content, "tip": solution.tip}    #Para debug
        dictSolutions[lang_txt] = {"tip": solution.tip}    #Lembrar de apagar o campo "solution" ao fazer commit!!
    dictSolutions = json.dumps(dictSolutions)

    context = {
        "problem": problem,
        "options": options,
        "solutions": dictSolutions,
        "title": _('Problem'),
    }

    return context
