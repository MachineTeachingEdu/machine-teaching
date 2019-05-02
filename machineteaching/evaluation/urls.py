from django.views.generic import CreateView

urlpatterns = [
    url(r'^$',CreateView.as_view(model=YourModel, get_success_url=lambda: reverse('model_countries'),
            template_name='your_countries.html'), form_class=ChoiceForm, name='model_countries'),)
