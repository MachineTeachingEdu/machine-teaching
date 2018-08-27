from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start', views.get_random_problem, name='start'),
    path('next', views.get_next_problem, name='next'),
    path('savelog', views.save_user_log, name='savelog'),

    ## DEBUG PURPOSES ##
    path('<int:problem_id>/', views.show_problem, name='show_problem'),
]
