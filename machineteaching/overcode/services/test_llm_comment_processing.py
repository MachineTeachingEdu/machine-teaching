import unittest

from .llm_comment_processing import (
    FAILED_IMPROVEMENT_BULLET,
    NO_STRENGTHS_BULLET,
    SKIPPED_IMPROVEMENT_BULLET,
    correctness_conflict_fallback,
    prepare_response,
)


class RequiredFeedbackSectionsTests(unittest.TestCase):
    def test_filtered_strengths_keep_heading_without_inventing_praise(self):
        response = (
            "### Pontos fortes\n"
            "- A função é simples e eficiente.\n\n"
            "### Melhorias\n"
            "- Não foram identificados problemas lógicos relevantes na solução."
        )

        result = prepare_response(response, grading_status="passed")

        self.assertTrue(result.startswith(f"### Pontos fortes\n{NO_STRENGTHS_BULLET}"))
        self.assertIn("\n\n### Melhorias\n", result)
        self.assertNotIn("eficiente", result)

    def test_correctness_fallback_keeps_both_sections(self):
        for status, improvement in (
            ("failed", FAILED_IMPROVEMENT_BULLET),
            ("skipped", SKIPPED_IMPROVEMENT_BULLET),
        ):
            with self.subTest(status=status):
                result = correctness_conflict_fallback(status)
                self.assertEqual(
                    result,
                    f"### Pontos fortes\n{NO_STRENGTHS_BULLET}\n\n"
                    f"### Melhorias\n{improvement}",
                )

    def test_partial_stream_does_not_insert_default_sections(self):
        result = prepare_response(
            "### Pontos fortes\n- A função é simples e eficiente.",
            grading_status="passed",
            ensure_default=False,
        )

        self.assertEqual(result, "")

    def test_complete_feedback_remains_unchanged(self):
        response = (
            "### Pontos fortes\n"
            "- A comparação considera os elementos vizinhos.\n\n"
            "### Melhorias\n"
            "- Não foram identificados problemas lógicos relevantes na solução."
        )

        self.assertEqual(prepare_response(response, grading_status="passed"), response)


if __name__ == "__main__":
    unittest.main()
