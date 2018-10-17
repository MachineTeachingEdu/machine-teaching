from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from questions.models import UserLog

class UserLogForm(ModelForm):
    class Meta:
        model = UserLog
        exclude = ['timestamp', 'user']

class SignUpForm(UserCreationForm):
    PROFESSORS = (("carla", "Carla"),
               ("joao", "João Carlos"))
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    professor = forms.ChoiceField(choices=PROFESSORS)
    programming = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',
                  'professor', 'programming')
