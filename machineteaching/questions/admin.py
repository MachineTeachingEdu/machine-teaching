from django.contrib import admin
from .models import (Problem, Solution, TestCase, UserLog, Cluster, UserModel,
                     UserProfile)


# Register your models here.
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'content')
    search_fields = ['id', 'title']

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'content', 'cluster')
    search_fields = ['id']
    list_filter = ('ignore', )

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'content')
    autocomplete_fields = ['problem']

@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'outcome', 'timestamp')
    search_fields = ['problem']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'professor', 'programming', 'strategy', 'accepted', 'seed')

admin.site.register(Cluster)
admin.site.register(UserModel)
