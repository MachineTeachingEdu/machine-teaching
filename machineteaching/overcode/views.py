from django.urls import reverse

from django.shortcuts import (render, redirect, get_object_or_404,)

from django.http import JsonResponse

from collections import defaultdict

from .tasks import iniciar_processamento_overcode

from questions.models import (Professor, UserLogView)
from .models import (GroupComment, IgnoredSolution, SolutionGroup)
from .forms import (EscolhaTurmaProblemaForm)


# Create your views here.

def escolher_turma_problema(request):

    if request.method == "POST":
        # PASSANDO USUÁRIO LOGADO PARA O FORMULÁRIO
        form = EscolhaTurmaProblemaForm(request.POST, user=request.user)

        if form.is_valid():
            turma = form.cleaned_data["turma"]
            problema = form.cleaned_data["problema"]

            iniciar_processamento_overcode(turma.id, problema.id)

            return render(
                request,
                "overcode/mensagem_inicio.html",
                {
                    "turma": turma,
                    "problema": problema,
                    "resultado_url": reverse(
                        "overcode:groups",
                        args=[turma.id, problema.id],
                    ),
                },
            )

    else:
        form = EscolhaTurmaProblemaForm(request.GET, user=request.user)

    return render(
        request,
        "overcode/escolha_form.html",
        {"form": form}
    )

def ver_resultado_overcode(request, turma_id, problema_id):
    return render(
        request,
        "overcode/inicio.html",
        {
            "turma_id": turma_id,
            "problem_id": problema_id,
        },
    )

def list_groups(request, turma_id, problema_id):
    groups = SolutionGroup.objects.filter(
        turma_id=turma_id,
        problem_id=problema_id,
    ).order_by("group_index")

    ignored_count = IgnoredSolution.objects.filter(
        problem_id=problema_id
    ).count()

    return render(
        request,
        "overcode/group_list.html",
        {
            "groups": groups,
            "turma_id": turma_id,
            "problem_id": problema_id,
            "ignored_count": ignored_count,
        },
    )

def group_detail(request, turma_id, problema_id, group_id):

    group = get_object_or_404(
        SolutionGroup,
        id=group_id,
        turma_id=turma_id,
        problem_id=problema_id,
    )

    member_ids = [int(m) for m in group.members]

    solutions = UserLogView.objects.filter(
        user_id__in=member_ids,
        problem_id=problema_id,
        user_class_id=turma_id
    ).select_related("user").order_by("user_id")

    comments = GroupComment.objects.filter(
        problem_id=problema_id,
        group=group
    ).select_related("author")

    # comentário de grupo
    group_comments = comments.filter(user__isnull=True)

    # comentários individuais
    comments_by_user = defaultdict(list)

    for c in comments:
        if c.user:
            comments_by_user[c.user.id].append(c)

    return render(
        request,
        "overcode/group_detail.html",
        {
            "group": group,
            "solutions": solutions,
            "group_comments": group_comments,
            "comments_by_user": dict(comments_by_user),
            "turma_id": turma_id,
            "problem_id": problema_id,
        },
    )

def ignored_detail(request, turma_id, problema_id):

    ignored = IgnoredSolution.objects.filter(problem_id=problema_id)

    solutions = []

    for item in ignored:
        log = UserLogView.objects.filter(
            user_id=item.solution_id,
            problem_id=problema_id,
            user_class_id=turma_id
        ).select_related("user").first()

        if log:
            solutions.append(log)

    comments = GroupComment.objects.filter(
        problem_id=problema_id,
        group__isnull=True
    ).select_related("author")

    comments_by_user = defaultdict(list)

    for c in comments:
        if c.user:
            comments_by_user[c.user.id].append(c)

    return render(
        request,
        "overcode/ignored_detail.html",
        {
            "solutions": solutions,
            "comments_by_user": dict(comments_by_user),
            "turma_id": turma_id,
            "problem_id": problema_id,
        }
    )

def salvar_comentario(request, turma_id, problema_id):

    if request.method == "POST":

        content = request.POST.get("content")
        group_id = request.POST.get("group_id")
        user_id = request.POST.get("user_id")
        selected_user = request.POST.get("selected_user")

        professor = Professor.objects.get(user=request.user.id)# TEMPORÁRIO

        if not content:
            return redirect(request.META.get("HTTP_REFERER", "/"))

        data = {
            "problem_id": problema_id,
            "author": professor,
            "content": content
        }

        # comentário de grupo
        if group_id:
            data["group_id"] = int(group_id)

        # comentário individual / ignorado
        if user_id:
            data["user_id"] = int(user_id)

        GroupComment.objects.create(**data)

        # se veio de um group
        if group_id:
            redirect_url = reverse(
                "overcode:group_detail",
                args=[turma_id, problema_id, group_id],
            )

        # se for ignored (sem group_id)
        else:
            redirect_url = reverse(
                "overcode:ignored_detail",
                args=[turma_id, problema_id],
            )

        # adiciona o hash
        if selected_user:
            redirect_url += f"#solution-{selected_user}"

        return redirect(redirect_url)

def deletar_comentario(request, comment_id):
    comment = get_object_or_404(GroupComment, id=comment_id)

    # se for AJAX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        comment.delete()
        return JsonResponse({"status": "ok"})

    # fallback normal (caso alguém acesse direto)
    turma_id = request.GET.get("turma_id")
    problema_id = request.GET.get("problem_id")

    group_id = comment.group_id
    user_id = comment.user_id

    comment.delete()

    if group_id:
        url = reverse(
            "overcode:group_detail",
            args=[turma_id, problema_id, group_id],
        )
    else:
        url = reverse(
            "overcode:ignored_detail",
            args=[turma_id, problema_id],
        )

    if user_id:
        url += f"#solution-{user_id}"

    return redirect(url)
