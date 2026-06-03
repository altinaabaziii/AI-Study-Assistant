import unittest

from study_tools import (
    detect_language,
    generate_quiz_items,
    is_genai_material,
    summarize_text,
)


GENAI_SAMPLE = """
Generative AI creates new content from prompts. RAG retrieves relevant context
from documents before generating an answer. Embeddings are numeric
representations of text that help vector search find similar meaning.
Prompt engineering gives the model clear instructions and constraints.
Evaluation checks whether answers are useful, correct, safe, and grounded.
"""


class StudyToolsTest(unittest.TestCase):
    def test_detect_language_for_albanian(self):
        self.assertEqual(detect_language("Çfarë është GenAI?"), "sq")

    def test_is_genai_material(self):
        self.assertTrue(is_genai_material(GENAI_SAMPLE))
        self.assertFalse(is_genai_material("This text is only about cooking recipes."))

    def test_summarize_text_returns_summary(self):
        summary = summarize_text(GENAI_SAMPLE)
        self.assertIn("Key concepts:", summary)
        self.assertIn("Generative AI", summary)

    def test_generate_quiz_items_returns_options(self):
        quiz = generate_quiz_items(GENAI_SAMPLE)
        self.assertIsInstance(quiz, list)
        self.assertGreaterEqual(len(quiz), 1)
        self.assertIn("question", quiz[0])
        self.assertIn("answer", quiz[0])
        self.assertEqual(len(quiz[0]["options"]), 4)


if __name__ == "__main__":
    unittest.main()
