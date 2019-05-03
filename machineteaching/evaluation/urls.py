from django.urls import path, reverse
from evaluation import views
from evaluation.forms import ConceptForm

urlpatterns = [
    path('', views.choose_concepts, name='choose_concepts')
]
