from django.urls import path
from downloadDB import views


from . import views
urlpatterns=[
    path('', views.index, name='downloadDB_index')
]