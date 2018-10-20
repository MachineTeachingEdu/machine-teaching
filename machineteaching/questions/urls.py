from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start', views.get_next_problem, name='start'),
    path('next', views.get_next_problem, name='next'),
    path('savelog', views.save_user_log, name='savelog'),
    path('signup', views.signup, name='signup'),
    path('past_problems', views.get_past_problems, name='past_problems'),
    path('past_solutions/<int:id>', views.get_user_solution, name='past_solutions'),

    ## DEBUG PURPOSES ##
    path('<int:problem_id>/', views.show_problem, name='show_problem'),
]
