from functools import wraps
import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.shortcuts import (render, redirect, get_object_or_404,)

from django.http import JsonResponse

from collections import defaultdict

from .tasks import iniciar_processamento_overcode

from questions.models import (Professor, UserLogView)
from .models import (
    GroupComment,
    IgnoredSolution,
    LLMCommentEvaluation,
    SolutionGroup,
)
from .forms import (EscolhaTurmaProblemaForm)


# Create your views here.


def is_active_professor(user):
    return (
        user.is_authenticated
        and Professor.objects.filter(user=user, active=True).exists()
    )


def professor_required(view_func):
    return login_required(
        user_passes_test(is_active_professor, login_url="login")(view_func),
        login_url="login",
    )


def professor_turma_required(view_func):
    @wraps(view_func)
    @professor_required
    def wrapped(request, *args, **kwargs):
        turma_id = kwargs.get("turma_id")

        if not Professor.objects.filter(
            user=request.user,
            active=True,
            prof_class__id=turma_id,
        ).exists():
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapped


@professor_required
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
                    "title": "Processamento iniciado",
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
        {
            "form": form,
            "title": "Executar Overcode",
        }
    )

@professor_turma_required
def ver_resultado_overcode(request, turma_id, problema_id):
    return render(
        request,
        "overcode/inicio.html",
        {
            "turma_id": turma_id,
            "problem_id": problema_id,
        },
    )

@professor_turma_required
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
            "title": "Grupos de Soluções",
        },
    )

@professor_turma_required
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
    ).select_related("author").order_by("created_at", "id")

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
            "title": f"Grupo {group.group_index}",
        },
    )

@professor_turma_required
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
    ).select_related("author").order_by("created_at", "id")

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
            "title": "Soluções Ignoradas",
        }
    )

@professor_turma_required
def salvar_comentario(request, turma_id, problema_id):

    if request.method == "POST":

        content = request.POST.get("content")
        group_id = request.POST.get("group_id")
        user_id = request.POST.get("user_id")
        selected_user = request.POST.get("selected_user")
        source = request.POST.get("source", GroupComment.SOURCE_MANUAL)

        professor = Professor.objects.get(user=request.user, active=True)

        if not content:
            return redirect(request.META.get("HTTP_REFERER", "/"))

        data = {
            "problem_id": problema_id,
            "author": professor,
            "content": content,
            "source": source
            if source in dict(GroupComment.SOURCE_CHOICES)
            else GroupComment.SOURCE_MANUAL,
        }

        # comentário de grupo
        if group_id:
            data["group_id"] = int(group_id)

        # comentário individual / ignorado
        if user_id:
            data["user_id"] = int(user_id)

        comment = GroupComment.objects.create(**data)

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "comment_id": comment.id,
            })

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

@professor_required
def deletar_comentario(request, comment_id):
    comment = get_object_or_404(GroupComment, id=comment_id)
    turma_id = request.GET.get("turma_id")
    problem_id = request.GET.get("problem_id") or comment.problem_id

    if comment.group:
        turma_id = comment.group.turma_id

    if not turma_id or not Professor.objects.filter(
        user=request.user,
        active=True,
        prof_class__id=turma_id,
    ).exists():
        raise PermissionDenied

    # se for AJAX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        comment.delete()
        return JsonResponse({"status": "ok"})

    # fallback normal (caso alguém acesse direto)
    problema_id = problem_id

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


@professor_required
@require_POST
def salvar_avaliacao_llm(request):

    data = json.loads(request.body)
    professor = Professor.objects.get(user=request.user, active=True)
    comment_id = data.get("comment_id")

    if not comment_id:
        return JsonResponse({
            "success": False,
            "error": "comment_id is required",
        }, status=400)

    comment = get_object_or_404(
        GroupComment.objects.select_related(
            "group",
            "user__userprofile",
        ),
        id=comment_id,
        source=GroupComment.SOURCE_AI,
    )

    if comment.group:
        turma_id = comment.group.turma_id
        turma = comment.group.turma
    elif comment.user_id:
        turma_id = comment.user.userprofile.user_class_id
        turma = comment.user.userprofile.user_class
    else:
        return JsonResponse({
            "success": False,
            "error": "Unable to determine comment class",
        }, status=400)

    if comment.group and comment.user_id:
        target_type = LLMCommentEvaluation.TARGET_INDIVIDUAL
    elif comment.group:
        target_type = LLMCommentEvaluation.TARGET_REPRESENTATIVE
    else:
        target_type = LLMCommentEvaluation.TARGET_IGNORED

    if not professor.prof_class.filter(id=turma_id).exists():
        raise PermissionDenied

    required_fields = [
        "helpful",
        "correct",
        "improve",
        "understand",
        "contains_code",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data or not isinstance(data[field], bool)
    ]

    if missing_fields:
        return JsonResponse({
            "success": False,
            "error": "Invalid evaluation fields",
            "fields": missing_fields,
        }, status=400)

    evaluation, _created = LLMCommentEvaluation.objects.update_or_create(
        comment=comment,
        defaults={
            "professor": professor,
            "problem": comment.problem,
            "turma": turma,
            "group": comment.group,
            "user": comment.user,
            "target_type": target_type,
            "helpful": data["helpful"],
            "correct": data["correct"],
            "improve": data["improve"],
            "understand": data["understand"],
            "contains_code": data["contains_code"],
        },
    )

    return JsonResponse({
        "success": True,
        "evaluation_id": evaluation.id,
    })

from .services.llm_service import generate_group_comment, generate_student_comment

@csrf_exempt
@professor_required
def llm_group_comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)

        code = data.get("code")
        group_id = data.get("group_id")
        user_id = data.get("user_id")
        ignored = data.get("ignored", False)

        if not code:
            return JsonResponse({"error": "missing code"}, status=400)

        if user_id:
            comment = generate_student_comment(code, ignored=ignored)
        else:
            comment = generate_group_comment(code)

        return JsonResponse({
            "comment": comment,
            "group_id": group_id,
            "user_id": user_id
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
