from django.db import models
from django.db.models.aggregates import Count
from django.contrib.auth.models import User
from picklefield.fields import PickledObjectField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from random import randint
import numpy as np

# Create your models here.
class Cluster(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50, blank=False)

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
    link = models.URLField(blank=False)
    retrieved_date = models.DateTimeField(blank=False)
    crawler = models.CharField(max_length=200, blank=True)
    hint = models.TextField(blank=True)
    objects = ProblemManager()

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
    tip = models.TextField(blank=True, default="#Start your python function here")
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True)

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    content = models.TextField(blank=False)

class UserLog(models.Model):
    OUTCOMES = (("F", "Failed"),
                ("P", "Passed"),
                ("S", "Skipped"))

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    solution = models.TextField(blank=True)
    outcome = models.CharField(max_length=2, choices=OUTCOMES)
    seconds_in_code = models.IntegerField()
    seconds_in_page = models.IntegerField()
    seconds_to_begin = models.IntegerField()
    solution_lines = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

class UserModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    distribution = PickledObjectField()

@receiver(post_save, sender=User)
def create_user_model(sender, instance, created, **kwargs):
    if created:
        model = UserModel()
        model.user = instance
        # TODO: UPDATE!
        # Fixed in number of problems and topics (54 x 3)
        model.distribution = np.zeros(settings.DOC_TOPIC_SHAPE)
        model.save()
