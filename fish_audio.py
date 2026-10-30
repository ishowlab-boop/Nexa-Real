"""Fish Audio HTTP TTS adapter.

Uses the official /v1/tts request structure: model header, prosody.speed,
and model-specific emotion cues. Returns complete audio in a *single* reply.
"""

from typing import Dict, List, Optional

import requests

from config import (
    DEFAULT_MODELS,
    FISH_AUDIO_API_KEY,
    FISH_AUDIO_BACKEND,
    FISH_AUDIO_BASE_URL,
    FISH_AUDIO_MP3_BITRATE,
    FISH_AUDIO_OPUS_BITRATE,
    USE_CONFIG_MODELS_ONLY,
)

# Style markers are performance directions, not spoken words. They do not
# guarantee the listener will perceive a specific age or emotion. S2.1/S2 use
# flexible [bracket] cues; older S1 uses its fixed (parenthesis) vocabulary.
VOICE_TYPE_TAGS = {
    "sexy": {
        "s1": "(soft tone)",
        "s2": "[warm, intimate, gently expressive tone]",
    },
    "sad": {"s1": "(sad)", "s2": "[sad]"},
    "angry": {"s1": "(angry)", "s2": "[angry]"},
    "sad_young": {
        "s1": "(sad) (soft tone)",
        "s2": "[sad] [gentle, youthful-sounding tone]",
    },
    "relaxed": {"s1": "(relaxed)", "s2": "[relaxed]"},
    "serious": {"s1": "(serious)", "s2": "[serious]"},
    "happy": {"s1": "(happy)", "s2": "[happy]"},
}


def apply_voice_type(text: str, voice_type: str = "normal", backend: str = "s2.1-pro") -> str:
    """Prefix emotion once; never fragment or line-split the submitted speech."""
    text = (text or "").strip()
    if not text:
        return text
    preset = VOICE_TYPE_TAGS.get((voice_type or "normal").strip().lower())
    if not preset:
        return text
    style = "s1" if (backend or "").strip().lower() == "s1" else "s2"
    return f"{preset[style]} {text}"


class FishAudioClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key if api_key is not None else FISH_AUDIO_API_KEY
        self.base_url = (base_url or FISH_AUDIO_BASE_URL).rstrip("/")

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/octet-stream", "Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def list_models(self) -> List[Dict]:
        if USE_CONFIG_MODELS_ONLY:
            return DEFAULT_MODELS
        try:
            resp = requests.get(
                f"{self.base_url}/voices",
                headers=self._headers(),
                timeout=15,
            )
            if resp.ok:
                models = resp.json()
                if isinstance(models, list):
                    return models
                if isinstance(models, dict) and isinstance(models.get("voices"), list):
                    return models["voices"]
        except requests.RequestException:
            pass
        return DEFAULT_MODELS

    def synthesize_text(
        self,
        text: str,
        voice_id: str,
        language: str = "en",  # Fish Audio detects language from input.
        format_: str = "opus",
        mp3_bitrate: Optional[int] = None,
        speed: Optional[float] = None,
        latency: str = "normal",
        voice_type: str = "normal",
    ) -> bytes:
        if not self.api_key:
            raise RuntimeError("VOICE_API_KEY is missing from the hosting environment")
        if not text or not text.strip():
            raise ValueError("Please send some text for the voice")
        if not voice_id:
            raise ValueError("Choose a voice model first")
        if format_ not in ("opus", "mp3", "wav", "pcm"):
            raise ValueError("Unsupported audio format")

        # Keep the text as one natural-flowing utterance. Don't split into many
        # one-sentence TTS requests and stitch them together (audible seams).
        backend = (FISH_AUDIO_BACKEND or "s2.1-pro").strip()
        emotion = (voice_type or "normal").strip().lower() in VOICE_TYPE_TAGS
        spoken_text = apply_voice_type(text, voice_type, backend)
        payload = {
            "text": spoken_text,
            "reference_id": voice_id,
            "format": format_,
            "normalize": not emotion,
            "latency": latency if latency in ("normal", "balanced") else "normal",
            "temperature": 0.7,
        }
        if format_ == "opus":
            payload["opus_bitrate"] = (
                FISH_AUDIO_OPUS_BITRATE
                if FISH_AUDIO_OPUS_BITRATE in (-1000, 24000, 32000, 48000, 64000)
                else 48000
            )
        elif format_ == "mp3":
            bitrate = FISH_AUDIO_MP3_BITRATE if mp3_bitrate is None else mp3_bitrate
            if bitrate in (64, 128, 192):
                payload["mp3_bitrate"] = bitrate

        # IMPORTANT: Speed is inside "prosody"; a top-level "speed" field is
        # not the documented Fish Audio REST API structure.
        if speed is not None:
            speed = float(speed)
            if not 0.5 <= speed <= 2.0:
                raise ValueError("Voice speed must be between 0.5 and 2.0")
            payload["prosody"] = {"speed": speed}

        headers = self._headers()
        # Fish Audio selects the TTS engine through the model *header*.
        headers["model"] = backend
        try:
            with requests.post(
                f"{self.base_url}/v1/tts",
                headers=headers,
                json=payload,
                timeout=(15, 120),
                stream=True,
            ) as response:
                if response.status_code != 200:
                    # Don't expose detailed provider response or credentials to users.
                    raise RuntimeError(f"Fish Audio HTTP {response.status_code}")
                audio = b"".join(chunk for chunk in response.iter_content(8192) if chunk)
        except requests.RequestException as exc:
            raise RuntimeError("Fish Audio connection failed") from exc

        if not audio:
            raise RuntimeError("Fish Audio returned empty audio")
        return audio
