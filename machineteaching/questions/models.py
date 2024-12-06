from django.db import models
from django.db.models.aggregates import Count
from django.contrib.auth.models import User, Group
from picklefield.fields import PickledObjectField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.conf import settings
import random
import json
from random import randint, SystemRandom
import numpy as np
from simple_history.models import HistoricalRecords
from django.utils.translation import ugettext_lazy as _
from questions.decorators import disable_for_loaddata

# Create your models here.
class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=200, blank=False)
    drop_out_model = models.ForeignKey('DropOutModel', on_delete=models.SET_NULL,
                                null=True, blank=True)
    history = HistoricalRecords()
    #active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.label

    def __str__(self):
        return "%s" % self.label

    class Meta:
        verbose_name = _('Chapter')
        verbose_name_plural = _('Chapters')


class ProblemManager(models.Manager):
    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Problem(models.Model):
    QUESTION_TYPES = (("C", "Code"),
                      ("M", "Multiple Choice"),
                      ("T", "Text"))

    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES,
                                     default="C")
    title = models.CharField(max_length=200, blank=False)
    content = models.TextField(blank=False)
    options = models.TextField(blank=True)
    difficulty = models.CharField(max_length=200, blank=True)
    link = models.URLField(blank=True)
    retrieved_date = models.DateTimeField(blank=True, auto_now_add=True)
    crawler = models.CharField(max_length=200, blank=True)
    hint = models.TextField(blank=True)
    objects = ProblemManager()
    chapter = models.ManyToManyField(Chapter, through='ExerciseSet')
    test_case_generator = models.TextField(blank=True, null=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return "%d - %s" % (self.id, self.title)

    class Meta:
        verbose_name = _('Problem')
        verbose_name_plural = _('Problems')


class ExerciseSet(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    history = HistoricalRecords()

    def __unicode__(self):
        return "%d - %s" % (self.order, self.problem)

    def __str__(self):
        return "%d - %s" % (self.order, self.problem)

    class Meta:
        verbose_name = _('Exercise Set')
        verbose_name_plural = _('Exercises Sets')


class OnlineClass(models.Model):
    name = models.CharField(max_length=200, blank=False)
    # chapter = models.ManyToManyField(Chapter)
    class_code = models.CharField(unique=True, max_length=200, null=True)
    active = models.BooleanField(default=True)
    start_date = models.DateField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('OnlineClass')
        verbose_name_plural = _('OnlineClasses')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return "%s" % self.name


class Deadline(models.Model):
    deadline = models.DateTimeField(blank=False, null=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    onlineclass = models.ManyToManyField(OnlineClass,
                                         limit_choices_to={'active': True})
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Deadline')
        verbose_name_plural = _('Deadlines')

    def __unicode__(self):
        return "%s - %s" % (self.chapter, self.deadline)

    def __str__(self):
        return "%s - %s" % (self.chapter, self.deadline)


class Professor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)   #Mudei aqui porque estava dando problema na migration
    prof_class = models.ManyToManyField(OnlineClass, related_name='professor')
    assistant = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.user

    def __str__(self):
        return "%s" % self.user

    class Meta:
        verbose_name_plural = _('Professors')


class UserProfile(models.Model):
    PROGRAMMING = (("yes", "Yes"),
                   ("no", "No"))
    STRATEGIES = (("random", "random"),
                  ("eer", "eer"),
                  ("sequential", "sequential"))
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    professor = models.ForeignKey(Professor, on_delete=models.PROTECT,
                                  null=True, blank=True)
    programming = models.CharField(max_length=3, choices=PROGRAMMING)
    accepted = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    strategy = models.CharField(max_length=10, choices=STRATEGIES)
    seed = models.CharField(max_length=81)
    user_class = models.ForeignKey(OnlineClass, on_delete=models.PROTECT,
                                   null=True)
    course = models.CharField(max_length=200, blank=False, null=True)
    sequential = models.BooleanField(default=True)
    history = HistoricalRecords()
    university = models.CharField(max_length=200, blank=False, null=True)
    registration = models.CharField(max_length=200, blank=False, null=True)

    def __unicode__(self):
        return self.user

    def __str__(self):
        return "%s" % self.user

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')


class Cluster(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50, blank=False)

    def __unicode__(self):
        return self.label

    def __str__(self):
        return "%d - %s" % (self.id, self.label)


class Language(models.Model):
    #Linguagens de programação
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')

class Solution(models.Model):
    content = models.TextField(blank=False)
    header = models.TextField(blank=True, null=True)
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    link = models.URLField(blank=True, null=True)
    retrieved_date = models.DateTimeField(blank=False, auto_now_add=True)
    ignore = models.BooleanField(default=False)
    tip = models.TextField(blank=True,
                           default="#Start your python function here")
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL,
                                null=True, blank=True)
    #Linguagens de programação
    language = models.ForeignKey(Language, on_delete=models.SET_DEFAULT, default=1)
    #Tipos de retorno
    TYPE_CHOICES = [
        ('int', 'int'),
        ('float', 'float'),
        ('double', 'double'),
        ('char', 'char'),
        ('long', 'long'),
        ('long long', 'long long'),
        ('short', 'short'),
        ('unsigned int', 'unsigned int'),
        ('unsigned long', 'unsigned long'),
        ('const char*', 'const char*'),
    ]
    return_type = models.CharField(max_length=50, choices=TYPE_CHOICES, null=True, blank=True)
    
    history = HistoricalRecords()

    def __unicode__(self):
        return self.problem.title

    def __str__(self):
        return self.problem.title

    class Meta:
        verbose_name = _('Solution')
        verbose_name_plural = _('Solutions')


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    languages = models.ManyToManyField(Language)  #Relacionamento Many-to-Many com Language
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Test Case')
        verbose_name_plural = _('Test Cases')


class UserLog(models.Model):
    OUTCOMES = (("F", "Failed"),
                ("P", "Passed"),
                ("S", "Skipped"))
    ERROR_TYPE = (("C", "Conceptual"),
                  ("S", "Syntax"),
                  ("D", "Distraction"),
                  ("I", "Interpretation"))

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    solution = models.TextField(blank=True)
    outcome = models.CharField(max_length=2, choices=OUTCOMES)
    console = models.TextField(blank=True)
    seconds_in_code = models.IntegerField()
    seconds_in_page = models.IntegerField()
    seconds_to_begin = models.IntegerField()
    solution_lines = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    error_type = models.CharField(max_length=2, choices=ERROR_TYPE,
                                  default="D")
    test_case_hits = models.IntegerField(blank=True, null=True)
    user_class = models.ForeignKey(OnlineClass, on_delete=models.PROTECT, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, default=1)

    class Meta:
        verbose_name = _('User log')
        verbose_name_plural = _('User logs')


class UserLogView(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, primary_key=True)
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    final_outcome = models.CharField(max_length=2)
    timestamp = models.DateTimeField()
    user_class = models.ForeignKey(OnlineClass, on_delete=models.PROTECT)
    seconds_in_code = models.IntegerField()
    seconds_in_page = models.IntegerField()

    class Meta:
        managed = False


class UserModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    distribution = PickledObjectField()

    def __unicode__(self):
        return self.user

    def __str__(self):
        return "%s" % self.user


class UserLogError(models.Model):
    userlog = models.ForeignKey(UserLog, on_delete=models.CASCADE, related_name='error')
    error = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s" % (self.error)

    def __str__(self):
        return "%s" % (self.error)


class PageAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.CharField(max_length=200, blank=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Page access')
        verbose_name_plural = _('Page accesses')

class Interactive(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Interactive')

class Recommendations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, null=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Recommendations')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userlog = models.ForeignKey(UserLog, on_delete=models.CASCADE)
    content = models.TextField(blank=False)

    class Meta:
        verbose_name = _('Comment')


class DropOutModel(models.Model):
    model_file = models.CharField(max_length=200, blank=False) # guarda o pickle do modelo
    #attributes = JsonField  # guarda uma lista de atributos a serem utilizados. Aí no código, cada atributo pode chamar uma função para calcular o valor daquele atributo
    completed_chapter = models.ManyToManyField(Chapter) # modelo a ser usado quando o último capitulo completo for esse

    class Meta:
        verbose_name = _('Drop out model')
        verbose_name_plural = _('Drop out models')

    def __unicode__(self):
        return self.model_file

    def __str__(self):
        return "%s" % self.model_file


class Collaborator(models.Model):
  name = models.CharField(max_length=255)
  description = models.CharField(max_length=1000)
  active = models.BooleanField(default=True)
  image = models.ImageField(upload_to='static/img/equipe/')

  class Meta:
        verbose_name = _('Collaborator')
        verbose_name_plural = _('Collaborators')


@receiver(post_save, sender=User)
@disable_for_loaddata
def create_user_model(sender, instance, created, **kwargs):
    if created:
        # Create profile
        UserProfile.objects.create(user=instance)
        instance.userprofile.save()

        # Create user model
        model = UserModel()
        model.user = instance
        # TODO: UPDATE!
        # Fixed in number of problems and topics (54 x 3)
        model.distribution = np.zeros(settings.DOC_TOPIC_SHAPE)
        model.save()


@receiver(post_save, sender=UserProfile)
@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Generate data for the random fields of UserProfile
        instance.strategy = random.choice(settings.STRATEGIES)
        alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        generator = SystemRandom()
        instance.seed = u''.join(generator.choice(alphabet) for _ in range(81))
        instance.save()


@receiver(post_save, sender=OnlineClass)
@disable_for_loaddata
def create_class_code(sender, instance, created, **kwargs):
    if created:
        # Generate random string code to identify OnlineClass
        unique_id = get_random_string(length=9)
        instance.class_code = '-'.join([
            unique_id[i:i+3] for i in range(0, len(unique_id), 3)])
        instance.save()


@receiver(post_save, sender=Professor)
@disable_for_loaddata
def add_professor_group(sender, instance, created, **kwargs):
    # Add as Professor group
    group = Group.objects.get(name="Professor")
    instance.user.groups.add(group)
    # Add as staff to be able to login in Admin
    instance.user.is_staff = True
    instance.user.save()


@receiver(post_delete, sender=Professor)
def delete_professor_group(sender, instance, **kwargs):
    # Remove from the Professor group
    group = Group.objects.get(name="Professor")
    instance.user.groups.remove(group)
    # Remove Admin access
    instance.user.is_staff = False
    instance.user.save()


@receiver(post_save, sender=Problem)
@disable_for_loaddata
def create_test_cases(sender, instance, created, **kwargs):
    # If generate test case is provided with the Problem, generate and
    # save the test cases
    if instance.test_case_generator is not None and \
            instance.test_case_generator != '':

        # Transform solution into python function
        function_obj = compile(instance.test_case_generator,
                               'generate', 'exec')
        exec(function_obj)

        # Generate test cases
        test_cases = eval('generate')()

        # If valid test cases
        if test_cases:
            # Delete old ones
            old_test_cases = TestCase.objects.filter(problem=instance)
            old_test_cases.delete()

            # Add new ones
            for item in test_cases:
                test_case = TestCase()
                test_case.problem = instance
                test_case.content = json.dumps(item)
                test_case.save()
                all_languages = Language.objects.all()
                test_case.languages.add(*all_languages)  #Adicionando todas as linguagens

@receiver(post_save, sender=UserLog)
@disable_for_loaddata
def create_userlog_error(sender, instance, created, **kwargs):
    if instance.outcome == 'F' and instance.console != '':
        clean_errors = []
        user_errors = instance.console.split('\n')
        if instance.language == Language.objects.get(name='Python'):
            # TODO: This is considering that Python errors have the word Error on
            # them. More elaborate strategies to log this are welcome.
            clean_errors = list(set([error.split(":")[0] for error in
                                user_errors if "Error" in error.split(":")[0]]))
        elif instance.language == Language.objects.get(name='Julia'):
            try:
                #clean_errors = list(set([error.split(":")[1].strip() for error in
                #                    user_errors if "Error" in error.split(":")[1] or "syntax" in error.split(":")[1]]))
                for error in user_errors:
                    error_type = error.split(":")[1]
                    if "Error" in error_type:
                        clean_errors.append(error.split(":")[1].strip())
                    elif "syntax" in error_type:
                        clean_errors.append("SyntaxError")
                clean_errors = list(set(clean_errors))
            except:
                clean_errors = []
        elif instance.language == Language.objects.get(name='C'):
            try:
                for error in user_errors:
                    error_type = error.split(":")[0]
                    if "RUNTIME ERROR" in error_type:
                        clean_errors.append("RuntimeError")
                    elif "COMPILE ERROR" in error_type:
                        clean_errors.append("CompileError")
                clean_errors = list(set(clean_errors))
            except:
                clean_errors = []
                
        for error in user_errors:
            if "Time limit exceeded" in error.split(":")[0]: 
                clean_errors.append("TimeoutError")
                break
        # Add error to Log Error model
        for error in clean_errors:
            log_error = UserLogError()
            log_error.userlog = instance
            log_error.error = error
            log_error.save()



