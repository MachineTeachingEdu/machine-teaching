from django.urls import path
from django.views.generic import TemplateView
from evaluation import views

urlpatterns = [
    path('', views.index, name='evaluation_index'),
    path('concepts', views.choose_concepts, name='choose_concepts'),
    path('intruder', views.intruder, name='intruder'),
    path('topic_name', views.topic_name, name='topic_name'),
    path('thank_you', TemplateView.as_view(
        template_name='evaluation/thank_you.html'), name='thank_you')
]
