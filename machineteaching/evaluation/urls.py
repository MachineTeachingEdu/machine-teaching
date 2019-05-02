from django.views.generic import CreateView
from evaluation.models import PythonConcepts

urlpatterns = [
    path('', CreateView.as_view(model=PythonConcepts,
         get_success_url=lambda: reverse('model_countries'),
            template_name='your_countries.html'), form_class=ChoiceForm, name='model_countries'),)
]
