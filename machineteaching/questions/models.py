from django.db import models
from django.db.models.aggregates import Count
from django.contrib.auth.models import User
from random import randint

# Create your models here.
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
