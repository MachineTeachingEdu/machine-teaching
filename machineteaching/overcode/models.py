from django.db import models
from django.contrib.auth.models import User

from questions.models import (Professor, Problem, OnlineClass)

# Create your models here.

# SOLUÇÕES IGNORADAS

class IgnoredSolution(models.Model):
    solution_id = models.CharField(max_length=20)
    problem_id = models.IntegerField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ignored Solution"
        verbose_name_plural = "Ignored Solutions"
        indexes = [
            models.Index(fields=["problem_id"]),
        ]

# GRUPO DE SOLUÇÕES

class SolutionGroup(models.Model):
    """
    Representa um agrupamento de soluções gerado pelo Machine Teaching
    (cada item do solutions.json).
    """

    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="solution_groups"
    )

    turma = models.ForeignKey(
        OnlineClass,
        on_delete=models.CASCADE,
        related_name="solution_groups"
    )

    group_index = models.IntegerField(
        help_text="ID do grupo conforme o solutions.json (campo 'id')"
    )

    correct = models.BooleanField(
        help_text="Se o grupo passa todos os testes"
    )

    members = models.JSONField(
        help_text="Lista de IDs das soluções/alunos pertencentes ao grupo"
    )

    count = models.IntegerField(
        help_text="Quantidade de soluções no grupo"
    )

    representative_code = models.TextField(
        help_text="Código representativo do grupo (gerado automaticamente pelo Overcode)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solution Group"
        verbose_name_plural = "Solution Groups"
        unique_together = ("problem", "turma", "group_index")

    def __str__(self):
        return f"Group {self.group_index} - Problem {self.problem_id}"

# GRUPO COMENTÁRIO

class GroupComment(models.Model):
    SOURCE_MANUAL = "manual"
    SOURCE_AI = "ai"

    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Professor"),
        (SOURCE_AI, "IA"),
    ]

    """
    Comentário do professor:
    - para um grupo de soluções
    - para um aluno específico (individual)
    - para soluções ignoradas (sem grupo, apenas user)
    """

    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    group = models.ForeignKey(
        SolutionGroup,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True
    )

    user = models.ForeignKey( # ALTEREI DE SOLUTION PARA USER...
        User, # PERGUNTAR LAURA: ESTAVA AUTHUSER NO OVERCODE, COMO DEIXO AQUI?
        on_delete=models.CASCADE,
        related_name="comments_received",
        null=True,
        blank=True,
        help_text="Aluno que recebe o comentário (individual ou ignorado)"
    )

    author = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()

    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default=SOURCE_MANUAL,
        help_text="Origem do comentário: escrito pelo professor ou gerado com IA"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Group Comment"
        verbose_name_plural = "Group Comments"
        indexes = [
            models.Index(fields=["problem"]),
            models.Index(fields=["group"]),
            models.Index(fields=["user"]),  # ALTEREI DE SOLUTION PARA USER...
        ]

    def __str__(self):
        if self.user:
            return f"Comment for user {self.user_id}"
        if self.group:
            return f"Comment on Group {self.group.group_index}"
        return f"General comment (Problem {self.problem_id})"


class LLMCommentEvaluation(models.Model):
    TARGET_REPRESENTATIVE = "representative"
    TARGET_INDIVIDUAL = "individual"
    TARGET_IGNORED = "ignored"

    TARGET_CHOICES = [
        (TARGET_REPRESENTATIVE, "Código representativo"),
        (TARGET_INDIVIDUAL, "Solução individual"),
        (TARGET_IGNORED, "Solução ignorada"),
    ]

    comment = models.OneToOneField(
        GroupComment,
        on_delete=models.CASCADE,
        related_name="llm_evaluation",
        help_text="Comentário gerado por IA avaliado pelo professor",
    )

    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="llm_comment_evaluations",
    )

    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="llm_comment_evaluations",
        null=True,
        blank=True,
    )

    turma = models.ForeignKey(
        OnlineClass,
        on_delete=models.CASCADE,
        related_name="llm_comment_evaluations",
        null=True,
        blank=True,
    )

    group = models.ForeignKey(
        SolutionGroup,
        on_delete=models.CASCADE,
        related_name="llm_comment_evaluations",
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="llm_comment_evaluations_received",
        null=True,
        blank=True,
        help_text="Aluno avaliado quando o comentário é individual ou ignorado",
    )

    target_type = models.CharField(
        max_length=20,
        choices=TARGET_CHOICES,
        null=True,
        blank=True,
        help_text="Tipo de código avaliado pelo comentário IA",
    )

    helpful = models.BooleanField()
    correct = models.BooleanField()
    improve = models.BooleanField()
    understand = models.BooleanField()
    contains_code = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "LLM Comment Evaluation"
        verbose_name_plural = "LLM Comment Evaluations"
        indexes = [
            models.Index(fields=["professor"]),
            models.Index(fields=["comment"]),
            models.Index(fields=["problem", "turma"]),
            models.Index(fields=["group"]),
            models.Index(fields=["user"]),
            models.Index(fields=["target_type"]),
        ]

    def __str__(self):
        return f"LLM evaluation for comment {self.comment_id}"
