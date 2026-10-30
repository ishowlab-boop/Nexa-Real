# RealVoi Female Voice Bot — updated package

This is the complete Python source for Telegram bot `@realvoi_bot`, including the
existing Admin Panel, plans, models, credits, SQLite DB and scheduled maintenance.

## What's improved

- Main menu: **Select Model**, **Plans**, **Usage**, **Voice Speed** and **Voice Type**.
  Previous **Contact Admin** and **Our Website** menu buttons are removed.
- Voice Type settings: **Sexy**, **Sad**, **Angry**, **Sad/Young**, **Relaxed**,
  **Serious**, and **Happy**. The selected style is saved per user in SQLite.
- Natural / slower speaking by default: Natural = **0.90x**, Slow = **0.82x**,
  Normal = **0.96x**, Fast = **1.05x**.
- Fixed Fish Audio API request: speed now goes to **`prosody.speed`** and the
  TTS model is specified in the **`model` HTTP header**.
- One continuous TTS request per message. User text is no longer broken by
  forced newlines after each sentence. Original words are preserved, with
  whitespace normalized only.
- Fish Audio **S2.1 Pro** is used by default with `[emotion]` style cues.
  Older **S1** is still an option via `FISH_AUDIO_BACKEND=s1` and uses `(tag)` cues.
- Uses direct `requests` HTTP instead of the withdrawn `fish-audio-sdk` pin.
- Bot sends audio as OGG/Opus Telegram voice messages. Credits are deducted only
  after successful voice delivery. The admin's existing database and preferences
  are kept during schema upgrades.

> Voice style is a best-effort TTS instruction. Naturalness and emotional
> accuracy depend on the selected voice/model. **Sad/Young** doesn't truly
> change the voice's age, and **Sexy** is represented as warm/intimate delivery.
> No live API voice output has been auditioned by these offline tests.

## Required Railway or server variables

| Variable | Meaning |
| --- | --- |
| `BOT_TOKEN` | Telegram token from BotFather |
| `VOICE_API_KEY` | Fish Audio API key |
| `FISH_AUDIO_BACKEND` | Optional, defaults to `s2.1-pro`; use `s1` if necessary |
| `FISH_AUDIO_BASE_URL` | Optional, defaults to `https://api.fish.audio` |
| `MAX_TTS_CHARS` | Optional, defaults to `200` |
| `USE_WEBHOOK` | `true` for webhook deployments; otherwise polling |
| `WEBHOOK_BASE_URL` | Your public HTTPS URL, for webhook mode |
| `DB_PATH` | Database path (e.g. `/data/file.db`) |
| `VOICES_DIR` | Saved voice location (e.g. `/data/voices`) |

**Do not send your bot token or Fish Audio key in messages or commit them to
source code.** Configure them as secret environment variables. Existing admin
IDs are in `config.py` as in the original project.

**Important:** If you already have a populated database, keep the **existing
`file.db`** and the same volume mount; don't overwrite it with an empty file.

## Deployment

1. Replace your existing application source with this package, keeping your
   current variables and database volume.
2. Set `BOT_TOKEN`, `VOICE_API_KEY`. To use the new S2.1 default, ensure your
   Fish Audio account and voice IDs work with that model.
3. Install dependencies: `pip install -r requirements.txt`.
4. Start via `python main.py` or the included `Procfile`.
5. In Telegram send `/start`, tap **Voice Speed → Natural**, then **Voice Type →
   Sad**, and send a sample phrase to listen to the output.
6. If provider compatibility requires the previous model, set
   `FISH_AUDIO_BACKEND=s1` and redeploy.

The Python code is designed for Python 3.11+. Railway webhook mode requires
HTTPS and `WEBHOOK_BASE_URL` with `USE_WEBHOOK=true`. Using a persistent volume
for DB and audio is strongly recommended. Existing `/admin` remains available.

## Offline regression tests

Tests simulate API payloads and DB migration; they do **not** call Fish Audio,
Telegram, or charge credits.

```
python -m unittest discover -s tests -v
```

Use a real Fish Audio API key and a supported voice model for a final listening
test; the sound cannot be guaranteed solely by source-code checks.
