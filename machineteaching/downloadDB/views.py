from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import NameForm, EmailForm, InstitutionForm, PretendedUseForm, AgreeForm
 
# Create your views here. 
def index(request):
  return render(request, 'downloadDB/index.html')


def get(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        name_form = NameForm(request.POST)
        email_form = EmailForm(request.POST)
        institution_form = InstitutionForm(request.POST)
        pretended_use_form = PretendedUseForm(request.POST)
        agree_form = AgreeForm(request.POST)
        # check whether it's valid:
        if form.is_valid() and email_form.is_valid() and institution_form.is_valid() and pretended_use_form.is_valid() and agree_form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect("/thanks/")#TODO - thanks page

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
        email_form = EmailForm()
        institution_form = InstitutionForm()
        pretended_use_form = PretendedUseForm()
        agree_form = AgreeForm()

    return render(request, "index.html", {"name_form": name_form, "email_form" : email_form,
                                          "institution_form" : institution_form, "pretended_use_form" : pretended_use_form})

