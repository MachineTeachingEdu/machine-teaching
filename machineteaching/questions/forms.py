from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from questions.models import (UserLog, OnlineClass, Chapter, Problem,
                              Solution, PageAccess, Interactive, Deadline, Comment)
import random
import datetime

class UserLogForm(ModelForm):
    class Meta:
        model = UserLog
        exclude = ['timestamp', 'user', 'error_type', 'user_class']


class SignUpForm(UserCreationForm):
    PROGRAMMING = (("no", _("No")),
                   ("yes", _("Yes")))
    # PROFESSORS = Professor.objects.filter(active=True).values_list(
    #     "id", "user__first_name").order_by('user__first_name')
    # CLASSES = OnlineClass.objects.filter(active=True).values_list("id", "name")
    # professor = forms.ChoiceField(choices=PROFESSORS)
    # onlineclass = forms.ChoiceField(choices=CLASSES, label="Class")
    class_code = forms.CharField(label=_("Class code"))
    course = forms.CharField(label=_("Course"))
    registration = forms.CharField(label=_("Registration"))
    university = forms.CharField(label=_("University"))
    programming = forms.ChoiceField(choices=PROGRAMMING, label=_(u"Did you have any programming experience before this course?"))
    accepted = forms.BooleanField(label=mark_safe(_('I accept the ') + '<a href="/terms_and_conditions">' + _('Terms and Conditions') + '</a>'))
    read = forms.BooleanField(label=mark_safe(_('I\'ve read the ') + '<a href="/privacy">' + _('Privacy Policy') + '</a>'))

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if email.lower() and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_(u'Email addresses must be unique.'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('email').lower()
        if username.lower() and User.objects.filter(username=username).exists():
            raise forms.ValidationError(_(u'Usernames must be unique.'))
        return username

    def clean_class_code(self):
        class_code = self.cleaned_data.get('class_code')
        if not OnlineClass.objects.filter(class_code=class_code).exists():
            raise forms.ValidationError(_(u'Invalid Class Code.'))
        return class_code


class OutcomeForm(forms.Form):
    onlineclass = forms.ModelChoiceField(queryset=OnlineClass.objects.all(), label=_(u'Class'))
    #chapter = forms.ModelChoiceField(queryset=Chapter.objects.all(), label=_(u'Chapter'))
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.filter(active = True), label=_(u'Chapter'))
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OutcomeForm, self).__init__(*args, **kwargs)

    def clean_onlineclass(self):
        onlineclass = self.cleaned_data.get('onlineclass')
        if onlineclass not in OnlineClass.objects.filter(professor__user=self.user):
            raise forms.ValidationError(_(u'You don\'t have authorization to view this class.'))
        return onlineclass

class ChapterForm(forms.ModelForm):
    deadline = forms.DateTimeField()

    def __init__(self, *args, **kwargs):
        super(ChapterForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Chapter
        fields = ['label']

class ProblemForm(forms.ModelForm):
    html = forms.CharField(widget=forms.Textarea)
    order = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(ProblemForm, self).__init__(*args, **kwargs)
        self.fields['order'].required = False
        self.fields['html'].required = False

    class Meta:
        model = Problem
        fields = ['title','content','options','chapter', 'test_case_generator']

    def clean(self):
        test_case_generator = self.cleaned_data.get('test_case_generator')
        try:
            # Transform solution into python function
            function_obj = compile(test_case_generator,
                                   'generate()', 'exec')
            exec(function_obj)

            # Generate test cases
            test_cases = eval('generate')()

        except Exception as e:
            self.add_error("test_case_generator", e)
        return self.cleaned_data

class SolutionForm(forms.ModelForm):
    QUESTION_TYPES = (("C", _("Code")),
                   ("M", _("Multiple Choice")),
                   ("T", _("Text")))
    solution = forms.CharField(widget=forms.Textarea)
    question_type = forms.ChoiceField(choices=QUESTION_TYPES)

    def __init__(self, *args, **kwargs):
        super(SolutionForm, self).__init__(*args, **kwargs)
        self.fields['problem'].required = False
        self.fields['header'].required = True

    class Meta:
        model = Solution
        fields = ['header','problem','tip', 'cluster']

    def clean(self):
        solution = self.cleaned_data.get('solution')
        question_type = self.cleaned_data.get('question_type')

        if question_type == "C":
            try:
                exec(solution)
            except Exception as err:
                self.add_error("solution", err)
        return self.cleaned_data

class PageAccessForm(ModelForm):
    class Meta:
        model = PageAccess
        exclude = ['timestamp', 'user']

class InteractiveForm(ModelForm):
    class Meta:
        model = Interactive
        exclude = ['timestamp', 'user']

class EditProfileForm(ModelForm):
    class_code = forms.CharField(label=_("Class code"))
    
    class Meta:
        model = User
        fields = []

    def clean_class_code(self):
        class_code = self.cleaned_data.get('class_code')
        if not OnlineClass.objects.filter(class_code=class_code).exists():
            raise forms.ValidationError(_(u'Invalid Class Code.'))
        return class_code

class NewClassForm(ModelForm):
    class Meta:
        model = OnlineClass
        fields = ['name', 'start_date']

class DeadlineForm(forms.Form):
    #chapter = forms.ModelChoiceField(queryset=Chapter.objects.all(), label=_(u'Chapter'))
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.filter(active = True), label=_(u'Chapter'))
    date = forms.CharField()
    time = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(DeadlineForm, self).__init__(*args, **kwargs)
        self.fields['chapter'].required = True
        self.fields['date'].required = True
        self.fields['time'].required = True

    def clean_date(self):
        date = self.cleaned_data.get('date')
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except:
            raise forms.ValidationError(_(u'The date must be in the format "yyyy-mm-dd" and must be valid.'))
        return date

    def clean_time(self):
        time = self.cleaned_data.get('time')
        try:
            datetime.datetime.strptime(time, "%H:%M")
        except:
            raise forms.ValidationError(_(u'The time must be in the format "HH:MM" and must be valid.'))
        return time

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ['user', 'userlog']