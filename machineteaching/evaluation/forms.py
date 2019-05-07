from django import forms
from evaluation.models import Concept


class MultiChoiceWidget(forms.widgets.CheckboxSelectMultiple):
    template_name = 'evaluation/concept_checkbox.html'


class ConceptForm(forms.Form):
    opt_concepts = Concept.objects.all().values_list('pk', 'label')
    concepts = forms.MultipleChoiceField(choices=opt_concepts,
                                         widget=MultiChoiceWidget)

class UserNoPasswordForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()

class IntruderForm(forms.Form):
    intruder = forms.ChoiceField(choices=[1,2,3,4])
