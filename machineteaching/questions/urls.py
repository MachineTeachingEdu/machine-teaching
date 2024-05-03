from django.urls import path
from django.views.generic import TemplateView

from . import views, context_processors
from django.conf.urls import url
from django.views.static import serve
# from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('', views.index, name='index'),
    path('saveaccess', views.save_access, name='saveaccess'),
    path('saveinteractive', views.save_interactive, name='saveinteractive'),
    path('saveprofile', context_processors.context, name='saveprofile'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('saveuniversity', views.save_university, name='saveuniversity'),
    path('start', views.start, name='start'),
    path('next', views.get_next_problem, name='next'),
    path('savelog', views.save_user_log, name='savelog'),
    path('export', views.export, name='export'),
    path('update_strategy', views.update_strategy, name='update_strategy'),
    path('signup', views.signup, name='signup'),
    path('past_problems', views.get_past_problems, name='past_problems'),
    path('past_solutions/<int:id>', views.get_user_solution,
         name='past_solutions'),
    path('student_solutions/<int:id>', views.get_student_logs,
         name='student_solutions'),
    path('student_solutions/<int:id>/<int:chapter>', views.get_student_solutions,
         name='student_solutions'),
    path('student_solutions/<int:id>/<int:chapter>/<int:problem>',
         views.get_student_logs, name='student_solutions'),
    path('problem_solutions/<int:problem_id>', views.get_past_solutions, name='problem_solutions'),
    path('problem_solutions/<int:problem_id>/<int:class_id>', views.get_problem_solutions, name='problem_solutions'),
    path('chapters', views.get_chapter_problems, name='chapters'),
    path('chapters/<int:chapter>', views.show_chapter, name='show_chapter'),
    path('new_chapter', views.new_chapter, name='new_chapter'),
    path('new', views.new_problem, name='new'),
    path('new/<int:chapter>', views.new_problem, name='new'),
    path('outcomes', views.show_outcome, name='show_outcome'),
    path('dashboard', views.get_dashboard, name='dashboard'),
    path('student_dashboard/<int:id>', views.get_student_dashboard, name='student_dashboard'),
    path('classes', views.classes, name='classes'),
    path('classes/manage/<int:onlineclass>', views.manage_class, name='manage_class'),
    path('classes/dashboard/<int:onlineclass>', views.get_class_dashboard, name='class_dashboard'),
    path('classes/new_dashboard/<int:onlineclass>', views.get_class_dashboard1, name='class_dashboard1'),
    path('class_active', views.class_active, name='class_active'),
    path('manager_dashboard', views.get_manager_dashboard, name='manager_dashboard'),
    path('delete_deadline/<int:onlineclass>/<int:deadline>', views.delete_deadline, name='delete_deadline'),
    path('terms_and_conditions', TemplateView.as_view(
        template_name='questions/conditions.html'),
        name='terms_and_conditions'),
    path('privacy', TemplateView.as_view(
        template_name='questions/privacy.html'),
        name='privacy'),
    path('about', views.about, name='about'),
    path('dashboard1', views.get_dashboard1, name='dashboard1'),  
    path('student_dashboard1/<int:id>', views.get_student_dashboard1, name='student_dashboard1'),

    # path('attempts/', views.AttemptsList.as_view(), name='attempts'),
    # path('recommendations/', views.Recommendations.as_view(), name='recommendations'),

    # DEBUG PURPOSES
    path('<int:problem_id>/', views.show_problem, name='show_problem'),

    # View to redirect to embed form
    path('satisfaction_form', views.satisfaction_form, name='satisfaction_form'),
]
