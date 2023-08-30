from django import forms

class NameForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)

class EmailForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=100)

class InstitutionForm(forms.Form):
    institution = forms.CharField(label="Institution", max_length=150)

class PretendedUseForm(forms.Form):
    pretended_use = forms.CharField(widget=forms.Textarea)

class AgreeForm(forms.Form):
    agree_form = forms.BooleanField()




#TODO - checkbox 'eu concordo'