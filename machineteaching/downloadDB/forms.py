from django import forms
from django.utils.translation import gettext as _

class DownloadDumpForm(forms.Form):
    name = forms.CharField(label=_("Name"),max_length=200) 
    email = forms.EmailField(label=_("E-mail"),max_length=200)
    institution = forms.CharField(label=_("Institution"), max_length= 200)
    pretended_use = forms.CharField(label=_("Pretended use"), widget=forms.Textarea(attrs={'rows': 4,'cols': 40}))
    agree_form = forms.BooleanField(label=_("I agree that I am not authorized to use this data for commercial purposes"), widget=forms.CheckboxInput)
    
    def __init__(self, *args, **kwargs):
        super(DownloadDumpForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['name'].required = True
        self.fields['institution'].required = True
        self.fields['pretended_use'].required = True
        self.fields['agree_form'].required = True
