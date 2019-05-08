from django import forms
from evaluation.models import Concept, TopicName


class MultiChoiceWidget(forms.widgets.CheckboxSelectMultiple):
    template_name = 'evaluation/concept_checkbox.html'


class ConceptForm(forms.Form):
    opt_concepts = Concept.objects.all().values_list('pk', 'label')
    concepts = forms.MultipleChoiceField(choices=opt_concepts,
                                         widget=MultiChoiceWidget,
                                         label="")


class UserNoPasswordForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()


class IntruderForm(forms.Form):
    CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4))
    intruder = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect,
                                 label="")


class TopicNameForm(forms.Form):
    name = forms.CharField(label="Este tópico reune códigos sobre ",
                           widget=forms.TextInput(attrs={'style': 'width:60%'}))
