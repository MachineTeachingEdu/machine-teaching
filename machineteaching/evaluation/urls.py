from django.urls import path
from evaluation import views

urlpatterns = [
    path('', views.index, name='evaluation_index'),
    path('concepts', views.choose_concepts, name='choose_concepts'),
    path('intruder', views.intruder, name='intruder'),
    path('topic_name', views.topic_name, name='topic_name'),
]
