"""Offline regression tests. No API keys, Telegram calls or Fish Audio charges."""
import importlib
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# pyTelegramBotAPI is installed by requirements.txt in production. These stubs
# allow the text helper functions to be tested offline without installing it.
if "telebot" not in sys.modules:
    fake_telebot = types.ModuleType("telebot")
    fake_types = types.ModuleType("telebot.types")
    fake_telebot.types = fake_types
    fake_telebot.TeleBot = type("TeleBot", (), {})
    for name in ("Message", "CallbackQuery", "ReplyKeyboardMarkup", "InlineKeyboardMarkup", "KeyboardButton", "InlineKeyboardButton"):
        setattr(fake_types, name, type(name, (), {}))
    sys.modules["telebot"] = fake_telebot
    sys.modules["telebot.types"] = fake_types

import db
import fish_audio
import user_panel


class MockHTTPResponse:
    status_code = 200
    def __init__(self, body=b"OggS-audio"):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def iter_content(self, size):
        yield self.body


class VoiceEngineTests(unittest.TestCase):
    def test_natural_text_keeps_one_connected_utterance(self):
        self.assertEqual(
            user_panel.humanize_text("Hello!  How are you?\nI am fine."),
            "Hello! How are you? I am fine.",
        )
        self.assertEqual(
            user_panel.humanize_text("তুমি আমাকে ছেড়ে গেলে কেন?  আমি খুব কষ্ট পেয়েছি।"),
            "তুমি আমাকে ছেড়ে গেলে কেন? আমি খুব কষ্ট পেয়েছি।",
        )

    def test_natural_is_slower_than_normal_and_default(self):
        self.assertEqual(user_panel.speed_to_value("natural"), 0.90)
        self.assertEqual(user_panel.speed_to_value("slow"), 0.82)
        self.assertLess(user_panel.speed_to_value("natural"), user_panel.speed_to_value("normal"))
        self.assertLess(user_panel.speed_to_value("slow"), user_panel.speed_to_value("natural"))

    def test_all_seven_moods_add_one_tag_not_one_per_sentence(self):
        sentence = "Hi there. I missed you. How are you?"
        for mood in user_panel.VOICE_TYPES:
            spoken = fish_audio.apply_voice_type(sentence, mood, "s2.1-pro")
            self.assertEqual(spoken.count(sentence), 1)
            self.assertEqual(spoken.count("["), 2 if mood == "sad_young" else 1)
            self.assertNotIn("\n", spoken)

    def test_legacy_s1_tag_format(self):
        spoken = fish_audio.apply_voice_type("Hello there.", "sad", "s1")
        self.assertEqual(spoken, "(sad) Hello there.")

    def test_actual_http_speed_model_and_emotion(self):
        client = fish_audio.FishAudioClient(api_key="test-key")
        with patch.object(fish_audio.requests, "post", return_value=MockHTTPResponse()) as post:
            result = client.synthesize_text(
                "I will be okay. Please stay.",
                "voice-123", speed=0.90, voice_type="sad", format_="opus"
            )
        self.assertTrue(result.startswith(b"OggS"))
        kwargs = post.call_args.kwargs
        self.assertEqual(kwargs["json"]["prosody"], {"speed": 0.90})
        self.assertNotIn("speed", kwargs["json"])
        self.assertEqual(kwargs["headers"]["model"], fish_audio.FISH_AUDIO_BACKEND)
        self.assertTrue(kwargs["json"]["text"].startswith("[sad] "))
        self.assertIn("Please stay.", kwargs["json"]["text"])
        self.assertEqual(kwargs["json"]["format"], "opus")
        self.assertFalse(kwargs["json"]["normalize"])

    def test_bad_speed_rejected_without_network(self):
        with patch.object(fish_audio.requests, "post") as post:
            with self.assertRaises(ValueError):
                fish_audio.FishAudioClient(api_key="test-key").synthesize_text(
                    "Hello", "voice", speed=0.25
                )
            post.assert_not_called()

    def test_existing_database_migration_keeps_credits(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "old.sqlite")
            con = sqlite3.connect(path)
            con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, credits INTEGER, created_at TEXT)")
            con.execute("INSERT INTO users (id,username,credits) VALUES (42,'demo',33)")
            con.commit()
            con.close()
            # Old DB here is intentionally minimal; real historical tables have
            # additional columns needed by update_user_fields.
            database = db.Database(path)
            user = database.get_user(42)
            self.assertEqual(user["credits"], 33)
            self.assertEqual(user["voice_type"], "normal")
            self.assertIn("tts_speed", user)
            database.conn.close()


if __name__ == "__main__":
    unittest.main()
