from django.urls import path
from downloadDB import views
from django.views.generic import TemplateView


from . import views
urlpatterns=[
    path('', views.index, name='downloadDB_index'),
    path('thanks', TemplateView.as_view(template_name='downloadDB/thanks.html'), name='thanks')
]   