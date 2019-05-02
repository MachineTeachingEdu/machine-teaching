from django.forms import ModelForm
from django import forms

class ConceptForm(ModelForm):
    class Meta:
        model = PythonConcepts

    def __init__(self, *args, **kwargs):
        super(ConceptForm, self).__init__(*args, **kwargs)
        self.fields['concepts'] =  forms.ModelChoiceField(queryset=PythonConcepts.objects.all(),
                                                    empty_label="Choose a countries",)
