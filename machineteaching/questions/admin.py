from django.contrib import admin
from .models import Problem, Solution, TestCase, UserLog


# Register your models here.
admin.site.register(Problem)
admin.site.register(Solution)

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'content')

@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'outcome', 'timestamp')
