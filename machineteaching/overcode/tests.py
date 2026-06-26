import json
import os
from unittest.mock import patch

from django.contrib.auth.models import Group, Permission, User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import sync_playwright

from questions.models import (
    Chapter,
    Deadline,
    ExerciseSet,
    Language,
    OnlineClass,
    Problem,
    Professor,
    UserLog,
)

from .models import (
    GroupComment,
    IgnoredSolution,
    LLMCommentEvaluation,
    SolutionGroup,
)


def create_overcode_fixture():
    professor_group, _created = Group.objects.get_or_create(name="Professor")

    turma = OnlineClass.objects.create(
        name="Turma OverCode",
        start_date="2026-01-01",
    )
    chapter = Chapter.objects.create(label="Aula OverCode")
    problem = Problem.objects.create(
        title="Problema OverCode",
        content="Resolva o problema de teste.",
    )
    ExerciseSet.objects.create(chapter=chapter, problem=problem, order=1)
    deadline = Deadline.objects.create(
        chapter=chapter,
        deadline=timezone.now() + timezone.timedelta(days=7),
    )
    deadline.onlineclass.add(turma)

    professor_user = User.objects.create_user(
        username="professor_overcode",
        email="professor@example.com",
        password="123456",
        first_name="Professor",
        last_name="Teste",
    )
    professor_user.groups.add(professor_group)
    professor_user.user_permissions.add(
        Permission.objects.get(codename="view_userlogview")
    )
    professor_user.is_staff = True
    professor_user.save()
    professor_user.userprofile.user_class = turma
    professor_user.userprofile.accepted = True
    professor_user.userprofile.read = True
    professor_user.userprofile.save()

    professor = Professor.objects.create(user=professor_user, active=True)
    professor.prof_class.add(turma)

    student = User.objects.create_user(
        username="student_overcode",
        email="student@example.com",
        password="123456",
        first_name="Aluno",
        last_name="Teste",
    )
    student.userprofile.user_class = turma
    student.userprofile.accepted = True
    student.userprofile.read = True
    student.userprofile.save()

    other_student = User.objects.create_user(
        username="ignored_student",
        email="ignored@example.com",
        password="123456",
        first_name="Aluno",
        last_name="Ignorado",
    )
    other_student.userprofile.user_class = turma
    other_student.userprofile.accepted = True
    other_student.userprofile.read = True
    other_student.userprofile.save()

    language, _created = Language.objects.get_or_create(name="Python")

    UserLog.objects.create(
        user=student,
        problem=problem,
        solution="def soma(a, b):\n    return a + b",
        outcome="P",
        console="",
        seconds_in_code=10,
        seconds_in_page=20,
        seconds_to_begin=1,
        solution_lines=2,
        user_class=turma,
        language=language,
    )
    UserLog.objects.create(
        user=other_student,
        problem=problem,
        solution="def soma(a, b):\n    return a - b",
        outcome="F",
        console="AssertionError",
        seconds_in_code=15,
        seconds_in_page=25,
        seconds_to_begin=2,
        solution_lines=2,
        user_class=turma,
        language=language,
    )

    group = SolutionGroup.objects.create(
        problem=problem,
        turma=turma,
        group_index=1,
        correct=True,
        members=[student.id],
        count=1,
        representative_code="def soma(a, b):\n    return a + b",
    )
    ignored = IgnoredSolution.objects.create(
        solution_id=str(other_student.id),
        problem_id=problem.id,
        reason="Solução fora dos grupos principais.",
    )

    other_turma = OnlineClass.objects.create(
        name="Turma Sem Acesso",
        start_date="2026-01-01",
    )
    other_group = SolutionGroup.objects.create(
        problem=problem,
        turma=other_turma,
        group_index=2,
        correct=False,
        members=[],
        count=0,
        representative_code="def soma(a, b):\n    return 0",
    )

    return {
        "turma": turma,
        "problem": problem,
        "professor_user": professor_user,
        "professor": professor,
        "student": student,
        "ignored_student": other_student,
        "group": group,
        "ignored": ignored,
        "other_turma": other_turma,
        "other_group": other_group,
    }


@override_settings(DEBUG=True)
class OverCodeInterfaceTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        headless = os.environ.get("OVERCODE_HEADLESS", "true").lower() != "false"
        cls.browser = cls.playwright.chromium.launch(headless=headless)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.data = create_overcode_fixture()

    def open_logged_page(self, path):
        page = self.browser.new_page()
        page.set_default_timeout(10000)
        page.goto(f"{self.live_server_url}/pt-br/accounts/login/?next={path}")
        page.fill('input[name="username"]', "professor@example.com")
        page.fill('input[name="password"]', "123456")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        return page

    def test_01_login_redirects_back_to_overcode(self):
        page = self.open_logged_page("/pt-br/overcode/escolher_turma")
        self.assertIn("/pt-br/overcode/escolher_turma", page.url)
        self.assertIn("Executar Overcode", page.text_content("body"))
        page.close()

    def test_02_overcode_menu_link_is_available_for_professor(self):
        page = self.open_logged_page("/pt-br/start")
        self.assertIn("OverCode", page.text_content("body"))
        overcode_link = page.get_by_role("link", name="OverCode", exact=True)
        href = overcode_link.get_attribute("href")
        self.assertIn("/overcode/escolher_turma", href)
        page.goto(f"{self.live_server_url}{href}")
        page.wait_for_load_state("networkidle")
        self.assertIn("/overcode/escolher_turma", page.url)
        page.close()

    def test_03_group_list_displays_groups_and_ignored_solutions(self):
        url = (
            f"/pt-br/overcode/turmas/{self.data['turma'].id}"
            f"/problemas/{self.data['problem'].id}/groups/"
        )
        page = self.open_logged_page(url)
        body = page.text_content("body")
        self.assertIn("Grupo 1", body)
        self.assertIn("solução ignorada", body)
        page.close()

    def test_04_group_detail_opens_on_representative_code(self):
        group = self.data["group"]
        url = (
            f"/pt-br/overcode/turmas/{self.data['turma'].id}"
            f"/problemas/{self.data['problem'].id}/groups/{group.id}/"
        )
        page = self.open_logged_page(url)
        self.assertTrue(page.locator("#representative").is_visible())
        self.assertIn("Código representativo", page.text_content("body"))
        page.close()

    def test_05_group_detail_lists_individual_solutions(self):
        group = self.data["group"]
        student = self.data["student"]
        url = (
            f"/pt-br/overcode/turmas/{self.data['turma'].id}"
            f"/problemas/{self.data['problem'].id}/groups/{group.id}/"
        )
        page = self.open_logged_page(url)
        page.click('button[data-tab-target="solutions"]')
        self.assertIn(student.get_full_name(), page.text_content("body"))
        page.close()

    def test_06_ignored_solutions_display_student_solution(self):
        url = (
            f"/pt-br/overcode/turmas/{self.data['turma'].id}"
            f"/problemas/{self.data['problem'].id}/ignoradas/"
        )
        page = self.open_logged_page(url)
        body = page.text_content("body")
        self.assertIn("Aluno Ignorado", body)
        self.assertIn("return a - b", body)
        page.close()

    def test_07_save_and_delete_group_comment_visually(self):
        group = self.data["group"]
        url = (
            f"/pt-br/overcode/turmas/{self.data['turma'].id}"
            f"/problemas/{self.data['problem'].id}/groups/{group.id}/"
        )
        page = self.open_logged_page(url)
        page.fill('textarea[name="content"]', "Comentário manual do teste")
        page.click("text=Salvar comentário")
        page.wait_for_load_state("networkidle")
        self.assertIn("Comentário manual do teste", page.text_content("body"))

        page.on("dialog", lambda dialog: dialog.accept())
        page.click(".delete-comment-overcode")
        page.wait_for_load_state("networkidle")
        self.assertNotIn("Comentário manual do teste", page.text_content("body"))
        page.close()

    @patch("overcode.views.generate_group_comment")
    def test_08_generate_ai_comment_and_save_evaluation_visually(self, mocked_llm):
        mocked_llm.return_value = "Comentário IA do teste"
        group = self.data["group"]
        url = (
            f"/pt-br/overcode/turmas/{self.data['turma'].id}"
            f"/problemas/{self.data['problem'].id}/groups/{group.id}/"
        )
        page = self.open_logged_page(url)
        page.click("text=Gerar comentário automático")
        page.wait_for_selector("text=Comentário IA do teste")
        page.locator(f"#llm-output-{group.id}").get_by_text("Usar comentário").click()
        page.locator(f"#llm-output-{group.id}").get_by_text("Salvar comentário").click()
        page.wait_for_selector("text=Avaliação do comentário IA")
        page.locator(f'input[name="helpful-{group.id}"][value="true"]').check()
        page.locator(f'input[name="correct-{group.id}"][value="true"]').check()
        page.locator(f'input[name="improve-{group.id}"][value="true"]').check()
        page.locator(f'input[name="understand-{group.id}"][value="false"]').check()
        page.locator(f'input[name="contains_code-{group.id}"][value="false"]').check()
        with page.expect_response(
            lambda response: (
                "llm/evaluation/" in response.url
                and response.status == 200
            )
        ):
            page.click("text=Finalizar formulário")

        self.assertTrue(
            LLMCommentEvaluation.objects.filter(
                comment__content="Comentário IA do teste",
                target_type=LLMCommentEvaluation.TARGET_REPRESENTATIVE,
            ).exists()
        )
        page.close()


class OverCodeEndpointTests(TestCase):
    def setUp(self):
        self.data = create_overcode_fixture()
        self.client.force_login(self.data["professor_user"])

    def test_01_choose_class_and_problem_starts_processing(self):
        with patch("overcode.views.iniciar_processamento_overcode") as mocked_task:
            response = self.client.post(
                reverse("overcode:escolher"),
                {
                    "turma": self.data["turma"].id,
                    "problema": self.data["problem"].id,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Processamento iniciado")
        mocked_task.assert_called_once_with(
            self.data["turma"].id,
            self.data["problem"].id,
        )

    def test_02_result_page_renders(self):
        response = self.client.get(
            reverse(
                "overcode:resultado",
                args=[self.data["turma"].id, self.data["problem"].id],
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_03_group_list_page_renders(self):
        response = self.client.get(
            reverse(
                "overcode:groups",
                args=[self.data["turma"].id, self.data["problem"].id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grupo 1")

    def test_04_group_detail_page_renders(self):
        response = self.client.get(
            reverse(
                "overcode:group_detail",
                args=[
                    self.data["turma"].id,
                    self.data["problem"].id,
                    self.data["group"].id,
                ],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Código representativo")

    def test_05_ignored_detail_page_renders(self):
        response = self.client.get(
            reverse(
                "overcode:ignored_detail",
                args=[self.data["turma"].id, self.data["problem"].id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aluno Ignorado")

    def test_06_save_group_comment(self):
        response = self.client.post(
            reverse(
                "overcode:salvar_comentario",
                args=[self.data["turma"].id, self.data["problem"].id],
            ),
            {
                "content": "Comentário manual",
                "group_id": self.data["group"].id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            GroupComment.objects.filter(
                content="Comentário manual",
                source=GroupComment.SOURCE_MANUAL,
                group=self.data["group"],
            ).exists()
        )

    @patch("overcode.views.generate_group_comment")
    def test_07_llm_group_comment_endpoint_uses_group_prompt(self, mocked_llm):
        mocked_llm.return_value = "Comentário gerado"

        response = self.client.post(
            reverse("overcode:llm_group_comment"),
            data=json.dumps({
                "code": "def soma(a, b): return a + b",
                "group_id": self.data["group"].id,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["comment"], "Comentário gerado")

    def test_08_save_ai_evaluation_for_representative_code(self):
        comment = GroupComment.objects.create(
            problem=self.data["problem"],
            group=self.data["group"],
            author=self.data["professor"],
            content="Comentário IA",
            source=GroupComment.SOURCE_AI,
        )

        response = self.client.post(
            reverse("overcode:salvar_avaliacao_llm"),
            data=json.dumps({
                "comment_id": comment.id,
                "helpful": True,
                "correct": True,
                "improve": True,
                "understand": True,
                "contains_code": False,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        evaluation = LLMCommentEvaluation.objects.get(comment=comment)
        self.assertEqual(
            evaluation.target_type,
            LLMCommentEvaluation.TARGET_REPRESENTATIVE,
        )
        self.assertEqual(evaluation.turma, self.data["turma"])
        self.assertEqual(evaluation.problem, self.data["problem"])

    def test_09_save_ai_evaluation_for_individual_solution(self):
        comment = GroupComment.objects.create(
            problem=self.data["problem"],
            group=self.data["group"],
            user=self.data["student"],
            author=self.data["professor"],
            content="Comentário IA individual",
            source=GroupComment.SOURCE_AI,
        )

        response = self.client.post(
            reverse("overcode:salvar_avaliacao_llm"),
            data=json.dumps({
                "comment_id": comment.id,
                "helpful": True,
                "correct": False,
                "improve": True,
                "understand": True,
                "contains_code": False,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        evaluation = LLMCommentEvaluation.objects.get(comment=comment)
        self.assertEqual(
            evaluation.target_type,
            LLMCommentEvaluation.TARGET_INDIVIDUAL,
        )
        self.assertEqual(evaluation.user, self.data["student"])

    def test_10_save_ai_evaluation_for_ignored_solution(self):
        comment = GroupComment.objects.create(
            problem=self.data["problem"],
            user=self.data["ignored_student"],
            author=self.data["professor"],
            content="Comentário IA ignorada",
            source=GroupComment.SOURCE_AI,
        )

        response = self.client.post(
            reverse("overcode:salvar_avaliacao_llm"),
            data=json.dumps({
                "comment_id": comment.id,
                "helpful": False,
                "correct": True,
                "improve": True,
                "understand": False,
                "contains_code": True,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        evaluation = LLMCommentEvaluation.objects.get(comment=comment)
        self.assertEqual(
            evaluation.target_type,
            LLMCommentEvaluation.TARGET_IGNORED,
        )
        self.assertEqual(evaluation.user, self.data["ignored_student"])

    def test_11_evaluation_requires_comment_id(self):
        response = self.client.post(
            reverse("overcode:salvar_avaliacao_llm"),
            data=json.dumps({
                "helpful": True,
                "correct": True,
                "improve": True,
                "understand": True,
                "contains_code": False,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "comment_id is required")

    def test_12_evaluation_rejects_manual_comment(self):
        comment = GroupComment.objects.create(
            problem=self.data["problem"],
            group=self.data["group"],
            author=self.data["professor"],
            content="Comentário manual",
            source=GroupComment.SOURCE_MANUAL,
        )

        response = self.client.post(
            reverse("overcode:salvar_avaliacao_llm"),
            data=json.dumps({
                "comment_id": comment.id,
                "helpful": True,
                "correct": True,
                "improve": True,
                "understand": True,
                "contains_code": False,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(LLMCommentEvaluation.objects.filter(comment=comment).exists())

    def test_13_evaluation_rejects_missing_boolean_fields(self):
        comment = GroupComment.objects.create(
            problem=self.data["problem"],
            group=self.data["group"],
            author=self.data["professor"],
            content="Comentário IA",
            source=GroupComment.SOURCE_AI,
        )

        response = self.client.post(
            reverse("overcode:salvar_avaliacao_llm"),
            data=json.dumps({
                "comment_id": comment.id,
                "helpful": True,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid evaluation fields")

    def test_14_professor_cannot_access_other_class_groups(self):
        response = self.client.get(
            reverse(
                "overcode:group_detail",
                args=[
                    self.data["other_turma"].id,
                    self.data["problem"].id,
                    self.data["other_group"].id,
                ],
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_15_delete_comment_removes_llm_evaluation(self):
        comment = GroupComment.objects.create(
            problem=self.data["problem"],
            group=self.data["group"],
            author=self.data["professor"],
            content="Comentário IA",
            source=GroupComment.SOURCE_AI,
        )
        LLMCommentEvaluation.objects.create(
            comment=comment,
            professor=self.data["professor"],
            problem=self.data["problem"],
            turma=self.data["turma"],
            group=self.data["group"],
            target_type=LLMCommentEvaluation.TARGET_REPRESENTATIVE,
            helpful=True,
            correct=True,
            improve=True,
            understand=True,
            contains_code=False,
        )

        response = self.client.get(
            reverse("overcode:deletar_comentario", args=[comment.id]),
            {
                "turma_id": self.data["turma"].id,
                "problem_id": self.data["problem"].id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(GroupComment.objects.filter(id=comment.id).exists())
        self.assertFalse(
            LLMCommentEvaluation.objects.filter(comment_id=comment.id).exists()
        )
