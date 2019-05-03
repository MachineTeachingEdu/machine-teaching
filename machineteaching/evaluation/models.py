from django.db import models
from django.contrib.auth.models import User
from questions.models import Solution


# Create your models here.
class Concept(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50, blank=False)

    def __unicode__(self):
        return self.label

    def __str__(self):
        return "%d - %s" % (self.id, self.label)


class SolutionConcept(models.Model):
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)

    def __unicode__(self):
        return "%s - %s - %s" % (self.solution.problem.title,
                                 self.user.username,
                                 self.concept.label)

    def __str__(self):
        return "%s - %s - %s" % (self.solution.problem.title,
                                 self.user.username,
                                 self.concept.label)
