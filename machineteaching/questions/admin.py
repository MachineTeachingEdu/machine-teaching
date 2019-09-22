from django.contrib import admin
from .models import (Problem, Solution, TestCase, UserLog, Cluster, UserModel,
                     UserProfile, Professor, OnlineClass, Chapter)


# Register your models here.
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content')
    search_fields = ['id', 'title']


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'content', 'cluster')
    search_fields = ['id', 'problem']
    list_filter = ('ignore', )


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'content')
    autocomplete_fields = ['problem']


@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'outcome', 'timestamp')
    search_fields = ['problem__title', 'user__username', 'user__first_name',
                     'user__last_name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'professor', 'programming', 'strategy', 'accepted',
                    'seed')
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_filter = ('professor', 'programming', 'strategy')
    autocomplete_fields = ['user']


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('user', 'assistant')
    search_fields = ['user']
    list_filter = ('assistant',)


admin.site.register(Cluster)
admin.site.register(UserModel)
admin.site.register(OnlineClass)
admin.site.register(Chapter)
