from django.contrib import admin
from .models import (Problem, Solution, TestCase, UserLog, Cluster, UserModel,
                     UserProfile, Professor, OnlineClass, Chapter, Deadline,
                     ExerciseSet, UserLogError, PageAccess, Interactive)
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ExportActionMixin


# Register your models here.
@admin.register(Solution)
class SolutionAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'problem', 'content', 'cluster')
    search_fields = ['id', 'problem__title', 'problem__id']
    list_filter = ('ignore', 'problem__chapter')
    exclude = ('link',)


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'content')
    autocomplete_fields = ['problem']


@admin.register(UserLog)
class UserLogAdmin(ExportActionMixin, admin.ModelAdmin):
    exclude = ('error_type',)
    list_display = ('user_name', 'problem', 'outcome', 'timestamp', 'user_class')
    search_fields = ['problem__title', 'user__username', 'user__first_name',
                     'user__last_name', 'user__userprofile__user_class__name']
    list_filter = ('outcome', 'problem__chapter')

    def user_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

    def user_class(self, obj):
        return obj.user.userprofile.user_class

    def get_queryset(self, request):
        qs = super(UserLogAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user__userprofile__user_class__professor__user=request.user)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_class', 'programming', 'accepted', 'read')
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_filter = ('user_class', 'programming', 'strategy')
    autocomplete_fields = ['user']

    def user_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

    def get_queryset(self, request):
        qs = super(UserProfileAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_class__professor__user=request.user)


@admin.register(Professor)
class ProfessorAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'assistant', 'active')
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_filter = ('assistant', 'active')

    def get_queryset(self, request):
        qs = super(ProfessorAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(active=True)


@admin.register(OnlineClass)
class OnlineClassAdmin(SimpleHistoryAdmin):
    exclude = ('class_code',)
    list_display = ('name', 'class_code', 'active', 'start_date')
    list_filter = ('active',)
    filter_horizontal = ('chapter',)

    def get_queryset(self, request):
        qs = super(OnlineClassAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(active=True)


class ExerciseSetInline(admin.TabularInline):
    model = ExerciseSet
    extra = 1


@admin.register(Problem)
class ProblemAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'title', 'content', 'chapter_all', 'question_type')
    search_fields = ['id', 'title']
    list_filter = ('chapter', 'question_type')
    filter_horizontal = ('chapter',)
    exclude = ('crawler', 'hint')
    inlines = (ExerciseSetInline,)

    def chapter_all(self, obj):
        return ", ".join(list(obj.chapter.all().values_list(
            "label", flat=True)))


@admin.register(Chapter)
class ChapterAdmin(SimpleHistoryAdmin):
    inlines = (ExerciseSetInline,)


@admin.register(Deadline)
class DeadlineAdmin(SimpleHistoryAdmin):
    list_display = ('deadline', 'chapter', 'onlineclass_all')
    filter_horizontal = ('onlineclass',)

    def onlineclass_all(self, obj):
        return ", ".join(list(obj.onlineclass.all().values_list(
            "name", flat=True)))

    def get_queryset(self, request):
        qs = super(DeadlineAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(onlineclass__professor__user=request.user).distinct()

@admin.register(PageAccess)
class PageAccessAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user_name', 'page', 'name', 'timestamp')
    search_fields = ['user__username', 'user__first_name', 'page', 'name']

    def user_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

@admin.register(Interactive)
class InteractiveAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user_name', 'problem', 'content', 'timestamp')
    search_fields = ['user__username', 'user__first_name', 'problem', 'content']

    def user_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name


admin.site.register(Cluster)
admin.site.register(UserModel)
admin.site.register(UserLogError)
