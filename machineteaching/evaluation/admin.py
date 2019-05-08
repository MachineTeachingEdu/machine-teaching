from django.contrib import admin
from evaluation.models import Concept, SolutionConcept, Intruder

# Register your models here.
admin.site.register(Concept)
admin.site.register(Intruder)


@admin.register(SolutionConcept)
class SolutionConceptAdmin(admin.ModelAdmin):
    list_display = ('concept', 'user', 'solution')
    search_fields = ('concept', 'user', 'solution')
