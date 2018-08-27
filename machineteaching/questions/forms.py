from django.forms import ModelForm
from questions.models import UserLog

class UserLogForm(ModelForm):
    class Meta:
        model = UserLog
        exclude = ['timestamp', 'user']
