from django.contrib import admin
from .models import Problem, Solution, TestCase, UserLog, Cluster, UserModel


# Register your models here.
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'content')
    search_fields = ['id']

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

admin.site.register(Cluster)
admin.site.register(UserModel)
