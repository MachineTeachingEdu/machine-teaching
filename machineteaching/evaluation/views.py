from django.shortcuts import render
from django.db.models import Count
from django.conf import settings
from django.contrib.auth.models import User
from questions.models import Solution
from evaluation.models import SolutionConcept, Concept
from evaluation.forms import ConceptForm


# Create your views here.
def choose_concepts(request):
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
            return HttpResponse("form is not valid")

    # Count how many problems that user has done
    user_count = User.objects.filter(username=request.user.username).annotate(
        user_count=Count('solutionconcept'))[0].user_count

    # If there are still problems to solve, render a new problem
    if user_count < settings.MAX_EVAL_COUNT:
        solution = Solution.objects.filter(ignore=False).annotate(
            num_concepts=Count('solutionconcept')).order_by('num_concepts')[0]
        user_count = User.objects.filter(username=request.user.username).annotate(
            user_count=Count('solutionconcept'))[0].user_count
        form = ConceptForm()

        return render(request, 'evaluation/choose_concepts.html',
                    {'form': form, 'solution': solution,
                    'user_count': user_count,
                    'max_eval_count': settings.MAX_EVAL_COUNT})
    # Otherwise, go to next exercise
    else:
        return render(request, 'evaluation/intruder.html')
