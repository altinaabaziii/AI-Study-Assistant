import json
import os
import unittest
from unittest.mock import patch

from llm_client import build_study_prompt, generate_study_answer


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class LlmClientTest(unittest.TestCase):
    def test_build_prompt_includes_sources_and_language(self):
        prompt = build_study_prompt(
            "Cfare eshte RAG?",
            [{"source": "notes.txt", "text": "RAG retrieves relevant context."}],
            "sq",
        )

        self.assertIn("Pergjigju ne shqip", prompt)
        self.assertIn("notes.txt", prompt)
        self.assertIn("RAG retrieves relevant context.", prompt)
        self.assertIn("Use your general Generative AI knowledge", prompt)
        self.assertIn("clear numbered points", prompt)
        self.assertNotIn("material is not enough", prompt)

    def test_generate_study_answer_uses_ollama_response(self):
        with patch("urllib.request.urlopen", return_value=FakeResponse({"message": {"content": " RAG uses context. "}})) as urlopen:
            answer = generate_study_answer(
                "What is RAG?",
                [{"source": "notes.txt", "text": "RAG retrieves context."}],
                "en",
            )

        self.assertEqual(answer, "RAG uses context.")
        self.assertEqual(urlopen.call_count, 1)

    def test_stream_study_answer_yields_tokens(self):
        from llm_client import stream_study_answer

        class FakeStreamResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def __iter__(self):
                lines = [
                    {"message": {"content": "RAG "}, "done": False},
                    {"message": {"content": "works."}, "done": False},
                    {"message": {"content": ""}, "done": True},
                ]
                for line in lines:
                    yield json.dumps(line).encode("utf-8")

        with patch("urllib.request.urlopen", return_value=FakeStreamResponse()):
            tokens = list(stream_study_answer("What is RAG?", [], "en"))

        self.assertEqual(tokens, ["RAG ", "works."])

    def test_generate_study_answer_allows_no_sources(self):
        with patch("urllib.request.urlopen", return_value=FakeResponse({"message": {"content": " RAG reduces hallucinations by grounding answers. "}})) as urlopen:
            answer = generate_study_answer("How does RAG reduce hallucinations?", [], "en")

        self.assertEqual(answer, "RAG reduces hallucinations by grounding answers.")
        self.assertEqual(urlopen.call_count, 1)

    def test_generate_study_answer_can_be_disabled(self):
        with patch.dict(os.environ, {"DISABLE_LOCAL_LLM": "1"}):
            answer = generate_study_answer(
                "What is RAG?",
                [{"source": "notes.txt", "text": "RAG retrieves context."}],
                "en",
            )

        self.assertIsNone(answer)


if __name__ == "__main__":
    unittest.main()
