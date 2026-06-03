import unittest
from unittest.mock import patch

from rag_engine import GenAIStudyRAG


class RagEngineTest(unittest.TestCase):
    def test_direct_concept_answer_does_not_wait_for_llm(self):
        engine = GenAIStudyRAG()
        engine.build_index()

        with patch("rag_engine.llm_client.generate_study_answer") as generate_study_answer:
            result = engine.answer_question("what is genai")

        generate_study_answer.assert_not_called()
        self.assertFalse(result["used_llm"])
        self.assertIn("Generative AI", result["answer"])

    def test_english_give_me_question_stays_english(self):
        engine = GenAIStudyRAG()

        self.assertEqual(
            engine.detect_language(
                "Give me a simple real-world example of prompt engineering."
            ),
            "en",
        )

    def test_rag_hallucination_answer_is_fast_and_specific(self):
        engine = GenAIStudyRAG()
        engine.build_index()

        with patch("rag_engine.llm_client.generate_study_answer") as generate_study_answer:
            result = engine.answer_question("How does RAG help reduce hallucinations in a study assistant?")

        generate_study_answer.assert_not_called()
        self.assertFalse(result["used_llm"])
        self.assertIn("retrieved source material", result["answer"])
        self.assertIn("less likely to invent facts", result["answer"])

    def test_prompt_engineering_example_is_fast_and_specific(self):
        engine = GenAIStudyRAG()
        engine.build_index()

        with patch("rag_engine.llm_client.generate_study_answer") as generate_study_answer:
            result = engine.answer_question(
                "Give me a simple real-world example of prompt engineering in a study assistant."
            )

        generate_study_answer.assert_not_called()
        self.assertFalse(result["used_llm"])
        self.assertIn("Summarize this PDF", result["answer"])
        self.assertIn("task, audience, format", result["answer"])

    def test_complex_multi_concept_question_uses_llm(self):
        engine = GenAIStudyRAG()
        engine.build_index()

        with patch("rag_engine.llm_client.generate_study_answer", return_value="LLM workflow answer.") as generate_study_answer:
            result = engine.answer_question(
                "Explain in detail how a GenAI study assistant could combine RAG, prompt engineering, and evaluation in one workflow."
            )

        generate_study_answer.assert_called_once()
        self.assertTrue(result["used_llm"])
        self.assertEqual(result["answer"], "LLM workflow answer.")


if __name__ == "__main__":
    unittest.main()
