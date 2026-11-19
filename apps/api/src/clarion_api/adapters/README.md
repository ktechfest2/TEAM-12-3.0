# adapters

The vendor boundary.

| Area | Protocol | Fake | Real |
| --- | --- | --- | --- |
| `llm` | `LanguageModel` (embed, judge_claim, translate) | `FakeLanguageModel` | `GeminiLanguageModel` |
| `speech` | `SpeechSynthesizer` | `FakeSpeechSynthesizer` | `SpitchSpeechSynthesizer` (OGG Opus; voices in `SPEECH_VOICES`) |
| `channels` | `Channel` (send_text) | `ConsoleChannel` | `TelegramChannel`; others T-14 |
| `storage` | `ObjectStore` | `LocalObjectStore` | S3 adapter T-05 |

Each area's `__init__.py` has a `build_*` factory that reads settings.
