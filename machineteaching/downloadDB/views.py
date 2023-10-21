from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import DownloadDumpForm
from django.core.mail import send_mail
from django.conf import settings
 
# Create your views here. 
def index(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = DownloadDumpForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            name = form.cleaned_data.get('name')
            mt_mail = settings.DEFAULT_FROM_EMAIL
            email = form.cleaned_data.get('email').lower()
            institution = form.cleaned_data.get('institution')
            pretended_use = form.cleaned_data.get('pretended_use')
            message_subject = 'Requisição de dados'
            message_content = 'Nome: {} \nE-mail: {} \nInstituição: {} \n\nUso pretendido: {}'.format(name, email, institution, pretended_use)
            message_html = """
            <div style='display: grid; grid-auto-flow: row; padding: 20px; width: 400px; height: 300px; background-color: #ffffff; border-radius: 10px;'>
              <h4 style='color: #292929; grid-column: 1;'> Requisição de dados.</h4> 
              <p style='color: #292929; margin-left: 20px; font-weight: 300; grid-column: 2;'> <strong>Nome:</strong> {} </p> 
              <p style='color: #292929; margin-left: 20px; font-weight: 300; grid-column: 3;'> <strong>Instituição:</strong> {}</p><br>
              <p style='color: #292929; margin-left: 20px; font-weight: 300; grid-column: 4;'> <strong>Uso pretendido:</strong> {}</p>
            </div>""".format(name, institution, pretended_use)
            
            send_mail(message_subject, message_content, None, [email, mt_mail], fail_silently=False, html_message=message_html)



            # process the data in form.cleaned_data as required
            
            # Recuperar os valores do form utilizando form.cleaned_data.get('VARIAVEL')
            # Cria o content e html do email com essas variaveis
            # send_email(....)

            # ...
            # redirect to a new URL:
            return HttpResponseRedirect("/thanks/") #TODO maybe return to start idk

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DownloadDumpForm() 

    return render(request, "downloadDB/index.html", {"form": form})
