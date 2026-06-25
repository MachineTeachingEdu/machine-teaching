from django.contrib import admin

from .models import GroupComment, LLMCommentEvaluation


@admin.register(GroupComment)
class GroupCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "problem", "group", "user", "author", "source", "created_at")
    list_filter = ("source", "created_at")
    search_fields = ("content", "user__username", "author__user__username")


@admin.register(LLMCommentEvaluation)
class LLMCommentEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "comment",
        "professor",
        "turma",
        "problem",
        "target_type",
        "group",
        "user",
        "helpful",
        "correct",
        "improve",
        "understand",
        "contains_code",
        "created_at",
    )
    list_filter = (
        "helpful",
        "correct",
        "improve",
        "understand",
        "contains_code",
        "target_type",
        "turma",
        "problem",
        "created_at",
    )
    search_fields = (
        "comment__content",
        "professor__user__username",
        "professor__user__first_name",
        "professor__user__last_name",
        "user__username",
        "user__first_name",
        "user__last_name",
    )
