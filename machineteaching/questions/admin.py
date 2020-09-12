from django.contrib import admin
from .models import (Problem, Solution, TestCase, UserLog, Cluster, UserModel,
                     UserProfile, Professor, OnlineClass, Chapter)
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ExportActionMixin


# Register your models here.
@admin.register(Problem)
class ProblemAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'title', 'content')
    search_fields = ['id', 'title']


@admin.register(Solution)
class SolutionAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'problem', 'content', 'cluster')
    search_fields = ['id', 'problem__title']
    list_filter = ('ignore', )


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'content')
    autocomplete_fields = ['problem']


@admin.register(UserLog)
class UserLogAdmin(ExportActionMixin, admin.ModelAdmin):
    exclude = ('error_type',)
    list_display = ('user', 'problem', 'outcome', 'timestamp', 'user_class')
    search_fields = ['problem__title', 'user__username', 'user__first_name',
                     'user__last_name', 'user__userprofile__user_class__name']
    list_filter = ('outcome', 'problem__chapter')

    def user_class(self, obj):
        return obj.user.userprofile.user_class

    def get_queryset(self, request):
        qs = super(UserLogAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user__userprofile__user_class__professor__user=request.user)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_class', 'programming', 'accepted', 'read')
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_filter = ('user_class', 'programming', 'strategy')
    autocomplete_fields = ['user']

    def get_queryset(self, request):
        qs = super(UserProfileAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_class__professor__user=request.user)


@admin.register(Professor)
class ProfessorAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'assistant')
    search_fields = ['user']
    list_filter = ('assistant',)

    def get_queryset(self, request):
        qs = super(ProfessorAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(active=True)


@admin.register(OnlineClass)
class OnlineClassAdmin(SimpleHistoryAdmin):
    exclude = ('class_code',)
    list_display = ('name', 'class_code', 'active')

    def get_queryset(self, request):
        qs = super(OnlineClassAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(active=True)

admin.site.register(Cluster)
admin.site.register(UserModel)
admin.site.register(Chapter, SimpleHistoryAdmin)
