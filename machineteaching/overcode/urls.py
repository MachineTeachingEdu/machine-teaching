# overcode/urls.py

from django.urls import path
from overcode import views

app_name = "overcode"

urlpatterns = [
    path('escolher_turma', views.escolher_turma_problema, name='escolher'),
    path('resultado/<int:turma_id>/<int:problema_id>/', views.ver_resultado_overcode, name='resultado'),
    path('turmas/<int:turma_id>/problemas/<int:problema_id>/groups/', views.list_groups, name='groups'),
    path('turmas/<int:turma_id>/problemas/<int:problema_id>/groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('turmas/<int:turma_id>/problemas/<int:problema_id>/ignoradas/', views.ignored_detail, name='ignored_detail'),
    path('comentar/<int:turma_id>/<int:problema_id>/', views.salvar_comentario, name='salvar_comentario'),
    path('comentario/deletar/<int:comment_id>/', views.deletar_comentario, name='deletar_comentario'),
]