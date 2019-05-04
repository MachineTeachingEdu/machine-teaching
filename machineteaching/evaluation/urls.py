from django.urls import path
from evaluation import views

urlpatterns = [
    path('', views.index, name='evaluation_index'),
    path('concepts', views.choose_concepts, name='choose_concepts')
]
