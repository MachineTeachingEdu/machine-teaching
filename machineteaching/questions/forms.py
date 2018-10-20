from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.urls import reverse
from questions.models import UserLog

class UserLogForm(ModelForm):
    class Meta:
        model = UserLog
        exclude = ['timestamp', 'user']

class SignUpForm(UserCreationForm):
    PROFESSORS = (("carla", "Carla"),
               ("joao", "João Carlos"))
    PROGRAMMING = (("no", "No"),
                   ("yes", "Yes"))
    professor = forms.ChoiceField(choices=PROFESSORS)
    programming = forms.ChoiceField(choices=PROGRAMMING, label="Did you have any programming experience before this course?")
    accepted = forms.BooleanField(label=mark_safe('I accept the <a href="/terms_and_conditions">Terms and Conditions</a>'))

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'Email addresses must be unique.')
        return email
