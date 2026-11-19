# 0007. Spitch for Nigerian language speech

- Status: proposed (becomes accepted once native speakers rate the sample clips)
- Date: 2026-11-19
- Deciders: Emmanuel Lafenwa

## Context

Approved corrections need to reach voters as voice notes in Yoruba, Hausa, Igbo and Nigerian Pidgin (T-13). Telegram and WhatsApp play a file as a voice note only when it is OGG Opus, and the voice renderer refuses anything that is not an Ogg container. The speech adapter has been a fake that stores audio which does not play.

## Options considered

1. **9jaLingo**: names all four languages (`ha`, `ig`, `yo`, `pcm`) and is cheap (₦50 per 1,000 characters, about ₦45 per spoken minute). Its `response_format` offers `ogg` but never says the codec is Opus, and its documentation is served from a staging domain.
2. **Spitch**: $0.0014 per second of audio ($0.084 per minute), $1 free credit, plus Yoruba tone marking at $1 per 10,000 words. Its SDK documents an explicit `ogg_opus` output format and named voices for Yoruba, Hausa, Igbo and English. It does not document a Pidgin voice.
3. Self hosted open models (SoroTTS, YarnGPT): all four languages, but we would run GPU hosting ourselves and the commercial licences are unclear.

## Decision

Spitch, called over plain HTTPS from `adapters/speech/spitch.py` (no SDK). The explicit `ogg_opus` format removes the main risk for voice notes. The team already holds a key, and the free credit covers the rating clips. Pidgin uses the English voice with the English language code until a Pidgin voice is confirmed. `SPEECH_VOICES` can name a different voice per language without a code change.

## Consequences

- Real voice notes for Yoruba, Hausa and Igbo, and English-voiced Pidgin, as soon as `SPEECH_PROVIDER=spitch` and `SPEECH_API_KEY` are set.
- Cost runs per second of audio and is billed in USD. Speech has no budget guard yet, unlike the language model (T-10). Watch the Spitch dashboard during pilots.
- To accept this ADR, native speakers rate one clip per language. If a voice fails, change it in `SPEECH_VOICES`. If Spitch fails overall, 9jaLingo is the fallback. Its adapter would need an Opus check on the returned file.
- Endpoint and field names come from the published SDK (`spitch` 1.50.0 on PyPI) because the documentation site renders in the browser only. Re-check them if Spitch publishes a breaking API version.
