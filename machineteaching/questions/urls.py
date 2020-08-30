from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start', views.get_next_problem, name='start'),
    path('next', views.get_next_problem, name='next'),
    path('savelog', views.save_user_log, name='savelog'),
    path('export', views.export, name='export'),
    path('update_strategy', views.update_strategy, name='update_strategy'),
    path('signup', views.signup, name='signup'),
    path('past_problems', views.get_past_problems, name='past_problems'),
    path('past_solutions/<int:id>', views.get_user_solution,
         name='past_solutions'),
    path('student_solutions/<int:id>', views.get_student_solutions,
         name='student_solutions'),
    path('student_solutions/<int:id>/<int:chapter>', views.get_student_solutions,
         name='student_solutions'),
    path('student_solutions/<int:id>/<int:chapter>/<int:problem>',
         views.get_student_solutions,
         name='student_solutions'),
    path('chapters', views.get_chapter_problems, name='chapters'),
    path('outcomes', views.show_outcome, name='show_outcome'),
    path('terms_and_conditions', TemplateView.as_view(
        template_name='questions/conditions.html'),
        name='terms_and_conditions'),
    path('privacy', TemplateView.as_view(
        template_name='questions/privacy.html'),
        name='privacy'),
    path('about', TemplateView.as_view(
        template_name='questions/about.html'),
        name='about'),

    # DEBUG PURPOSES
    path('<int:problem_id>/', views.show_problem, name='show_problem'),
]
