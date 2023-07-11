from django.contrib import admin
from evaluation.models import Concept, SolutionConcept, Intruder, TopicName

# Register your models here.
admin.site.register(Concept)


@admin.register(SolutionConcept)
class SolutionConceptAdmin(admin.ModelAdmin):
    list_display = ('concept', 'user', 'solution')
    search_fields = ('concept', 'user', 'solution')


@admin.register(TopicName)
class TopicNameAdmin(admin.ModelAdmin):
    list_display = ('user', 'cluster', 'label')
    search_fields = ('user', 'cluster', 'label')


@admin.register(Intruder)
class IntruderAdmin(admin.ModelAdmin):
    list_display = ('user', 'cluster', 'solution', 'intruder')
    search_fields = ('user', 'cluster', 'solution', 'intruder')
