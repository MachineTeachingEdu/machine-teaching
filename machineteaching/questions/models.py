from django.db import models
from django.db.models.aggregates import Count
from django.contrib.auth.models import User
from picklefield.fields import PickledObjectField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import random
from random import randint, SystemRandom
import numpy as np


# Create your models here.
class OnlineClass(models.Model):
    name = models.CharField(max_length=200, blank=False)

    class Meta:
        verbose_name_plural = 'OnlineClasses'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return "%s" % self.name


class Professor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prof_class = models.ManyToManyField(OnlineClass)

    def __unicode__(self):
        return self.user

    def __str__(self):
        return "%s" % self.user

class UserProfile(models.Model):
    PROGRAMMING = (("yes", "Yes"),
                   ("no", "No"))
    STRATEGIES = (("random", "random"),
                  ("eer", "eer"),
                  ("sequential", "sequential"))
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    professor = models.ForeignKey(Professor, on_delete=models.PROTECT,
                                  null=True)
    programming = models.CharField(max_length=3, choices=PROGRAMMING)
    accepted = models.BooleanField(default=False)
    strategy = models.CharField(max_length=10, choices=STRATEGIES)
    seed = models.CharField(max_length=81)
    user_class = models.ForeignKey(OnlineClass, on_delete=models.PROTECT,
                                   null=True)
    sequential = models.BooleanField(default=True)


    def __unicode__(self):
        return self.user

    def __str__(self):
        return "%s" % self.user


class Cluster(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50, blank=False)

    def __unicode__(self):
        return self.label

    def __str__(self):
        return "%d - %s" % (self.id, self.label)


class Chapter(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=200, blank=False)

    def __unicode__(self):
        return self.label

    def __str__(self):
        return "%d - %s" % (self.id, self.label)


class ProblemManager(models.Manager):
    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Problem(models.Model):
    title = models.CharField(max_length=200, blank=False)
    content = models.TextField(blank=False)
    difficulty = models.CharField(max_length=200, blank=True)
    link = models.URLField(blank=True)
    retrieved_date = models.DateTimeField(blank=True)
    crawler = models.CharField(max_length=200, blank=True)
    hint = models.TextField(blank=True)
    objects = ProblemManager()
    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT, null=True)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return "%d - %s" % (self.id, self.title)


class Solution(models.Model):
    content = models.TextField(blank=False)
    header = models.TextField(blank=False)
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    link = models.URLField(blank=True, null=True)
    retrieved_date = models.DateTimeField(blank=False)
    ignore = models.BooleanField(default=False)
    tip = models.TextField(blank=True,
                           default="#Start your python function here")
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True)

    def __unicode__(self):
        return self.problem.title

    def __str__(self):
        return self.problem.title


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    content = models.TextField(blank=False)


class UserLog(models.Model):
    OUTCOMES = (("F", "Failed"),
                ("P", "Passed"),
                ("S", "Skipped"))
    ERROR_TYPE = (("C", "Conceptual"),
                  ("S", "Syntax"),
                  ("D", "Distraction"),
                  ("I", "Interpretation"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    solution = models.TextField(blank=True)
    outcome = models.CharField(max_length=2, choices=OUTCOMES)
    seconds_in_code = models.IntegerField()
    seconds_in_page = models.IntegerField()
    seconds_to_begin = models.IntegerField()
    solution_lines = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    error_type = models.CharField(max_length=2, choices=ERROR_TYPE,
                                  default="D")


class UserModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    distribution = PickledObjectField()

    def __unicode__(self):
        return self.user

    def __str__(self):
        return "%s" % self.user


@receiver(post_save, sender=User)
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
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Generate data for the random fields of UserProfile
        instance.strategy = random.choice(settings.STRATEGIES)
        alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        generator = SystemRandom()
        instance.seed = u''.join(generator.choice(alphabet) for _ in range(81))
        instance.save()
