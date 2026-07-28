import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from acoustic_ai import (
    DEFAULT_SUGGESTED_QUESTIONS,
    MAXIMUM_CHARACTERS,
    MAXIMUM_MESSAGES,
    AcousticAIError,
    ask_acoustic_ai,
    build_conversation,
    validate_question,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class AcousticAIClientTests(unittest.TestCase):
    def test_short_question_is_rejected_before_a_request(self):
        self.assertIn("at least four words", validate_question("RT60 help please"))
        self.assertIsNone(validate_question("How can I treat flutter echo?"))

    def test_conversation_keeps_only_a_valid_recent_window(self):
        history = [
            {"role": "assistant" if index % 2 else "user", "content": "x" * 250}
            for index in range(50)
        ]
        question = "How can I treat flutter echo?"

        conversation = build_conversation(history, question)

        self.assertLessEqual(len(conversation), MAXIMUM_MESSAGES)
        self.assertLessEqual(
            sum(len(message["content"]) for message in conversation), MAXIMUM_CHARACTERS
        )
        self.assertEqual(conversation[-1], {"role": "user", "content": question})
        self.assertNotEqual(conversation[0]["role"], "assistant")

    @patch("acoustic_ai.urlopen")
    def test_api_reply_uses_documented_fallback_suggestions(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(
            {"model": "google/gemini-2.5-flash", "reply": "A useful answer."}
        )

        response = ask_acoustic_ai([{"role": "user", "content": "How can I reduce flutter echo?"}])

        self.assertEqual(response.reply, "A useful answer.")
        self.assertEqual(response.suggested_questions, DEFAULT_SUGGESTED_QUESTIONS)
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            json.loads(request.data.decode("utf-8")),
            {"messages": [{"role": "user", "content": "How can I reduce flutter echo?"}]},
        )
        self.assertEqual(request.get_header("User-agent"), "AcousticDesignAssistant/1.0")

    @patch("acoustic_ai.urlopen")
    def test_rate_limit_returns_a_friendly_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError("https://example.test", 429, "Too Many Requests", None, None)

        with self.assertRaisesRegex(AcousticAIError, "busy"):
            ask_acoustic_ai([{"role": "user", "content": "How can I reduce flutter echo?"}])


if __name__ == "__main__":
    unittest.main()