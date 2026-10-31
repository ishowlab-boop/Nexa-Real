import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# FIXED ADMIN IDS
# -------------------------
ADMIN_IDS = [1800295558]   # আপনার Telegram numeric ID

# Tokens / API
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN", "")
FISH_AUDIO_API_KEY = os.getenv("VOICE_API_KEY", "")

# Fish Audio
FISH_AUDIO_BASE_URL = os.getenv("FISH_AUDIO_BASE_URL", "https://api.fish.audio")
FISH_AUDIO_BACKEND = os.getenv("FISH_AUDIO_BACKEND", "s2.1-pro")
FISH_AUDIO_MP3_BITRATE = int(os.getenv("FISH_AUDIO_MP3_BITRATE", "128"))
FISH_AUDIO_OPUS_BITRATE = int(os.getenv("FISH_AUDIO_OPUS_BITRATE", "48000"))

# Misc
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "t.me/Ariyanfix")
WEBSITE_URL = os.getenv("WEBSITE_URL", "modelboxbd.com")

DB_PATH = os.getenv("DB_PATH", "file.db")
VOICES_DIR = os.getenv("VOICES_DIR", "voices")

COST_PER_VOICE = 1
REQUIRE_VALIDITY_FOR_TTS = False
MAX_TTS_CHARS = int(os.getenv("MAX_TTS_CHARS", "200"))

DEFAULT_MODELS = [
    {"id": "a5e5bbe15fb6465fb113c1bab4de8b2e", "name": "Marie🤷‍♀️"},
    {"id": "89caeb03934840e791f7d13e9c03b6ef", "name": "Daisy🧕"},
    {"id": "e3fbe8fdb0ea40d8a15d527ab854b8af", "name": "Ayesha🙇‍♀️"},
    {"id": "b8daf8f8981a484abb8cc9520641b5dc", "name": "Anna🤭"},
    {"id": "29913697e157485c941c737314c27819", "name": "Ruby👨‍🏫"},
    {"id": "d75c78da679a4d8480e4bcfb6c60bdc6", "name": "Nora🧚‍♂️"},
    {"id": "d39b35734b49454784d2dbcc17cd45b9", "name": "Denica👰‍♀️"},
    {"id": "c5e4c4c57a084a0f9b5b277d36546ef0", "name": "Even👧"},
    {"id": "2fe69a0850b54119ad97af8246e2f6a0", "name": "Freya🧑‍🦰"},
    {"id": "60de84651feb4ac7a0bbc23c45c089e1", "name": "Gia👩‍🦱"},
    {"id": "e63b6bb69a954375ac20f1e41905494b", "name": "Lacy🙇‍♀️"},
    {"id": "99d3b0d6e12843adb98519581f849a48", "name": "Zoey🧚‍♀️"},
    {"id": "53ca9f8d971a4410a5f9b159c56cd080", "name": "Linda🙂‍↔️"},
    {"id": "3e2a5ae324da43d7b0de0a28182c1b19", "name": "Reina👸"},
    {"id": "2b38957c81a7418699d639c209fde42f", "name": "Maria👄"},
    {"id": "28862959fc35487581579ae5bf578b52", "name": "Gita Hall👩🏼‍🦳"},
]

USE_CONFIG_MODELS_ONLY = True


PLANS = [
    {
        "name": "🥉 Starter Plan",
        "credits": 50,
        "price": "💵 $5",
        "validity_days": 30
    },
    {
        "name": "🥈 Pro Plan",
        "credits": 200,
        "price": "💵 $15",
        "validity_days": 30
    },
    {
        "name": "🥇 Unlimited-Day Plan",
        "credits": 400,
        "price": "💵 $30",
        "validity_days": 30
    },
]


USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "")
PORT = int(os.getenv("PORT", "8000"))
