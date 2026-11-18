"""Gemini provider. The only module allowed to import the Google GenAI SDK."""

import json
from collections.abc import Sequence

from google import genai  # noqa: TID251 - this is the designated adapter
from google.genai import types  # noqa: TID251
from pydantic import BaseModel

from clarion_api.domain.enums import Language, Verdict
from clarion_api.domain.models import SourcePassage, VerdictResult

LANGUAGE_NAMES = {
    Language.ENGLISH: "English",
    Language.YORUBA: "Yoruba (with full tone marks and underdots)",
    Language.HAUSA: "Hausa (with hooked letters such as ɓ, ɗ, ƙ)",
    Language.IGBO: "Igbo (with diacritics)",
    Language.PIDGIN: "Nigerian Pidgin",
}

JUDGE_INSTRUCTIONS = """You check election claims against official passages only.
Return one verdict:
- confirmed: a passage directly supports the claim.
- contradicted: a passage directly contradicts the claim.
- no_official_statement: no passage settles it.
Cite the passage index you relied on, or null. Do not use outside knowledge.
Do not judge opinions, candidates or parties."""


class _JudgeOut(BaseModel):
    verdict: Verdict
    passage_index: int | None
    rationale: str
    confidence: float


class GeminiLanguageModel:
    def __init__(self, *, api_key: str, model: str, embedding_model: str, dimensions: int) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._embedding_model = embedding_model
        self._dimensions = dimensions

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        response = await self._client.aio.models.embed_content(
            model=self._embedding_model,
            contents=[types.Content(parts=[types.Part.from_text(text=t)]) for t in texts],
            config=types.EmbedContentConfig(output_dimensionality=self._dimensions),
        )
        return [list(e.values or []) for e in response.embeddings or []]

    async def judge_claim(self, claim: str, passages: Sequence[SourcePassage]) -> VerdictResult:
        numbered = "\n\n".join(
            f"[{i}] {p.document_title} ({p.publisher}, {p.url})\n{p.text}"
            for i, p in enumerate(passages)
        )
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=f"CLAIM:\n{claim}\n\nOFFICIAL PASSAGES:\n{numbered}",
            config=types.GenerateContentConfig(
                system_instruction=JUDGE_INSTRUCTIONS,
                response_mime_type="application/json",
                response_json_schema=_JudgeOut.model_json_schema(),
                temperature=0.0,
            ),
        )
        out = _JudgeOut.model_validate(json.loads(response.text or "{}"))
        idx = out.passage_index
        passage_id = passages[idx].id if idx is not None and 0 <= idx < len(passages) else None
        return VerdictResult(
            verdict=out.verdict,
            passage_id=passage_id,
            rationale=out.rationale,
            confidence=max(0.0, min(1.0, out.confidence)),
        )

    async def translate(self, text: str, *, target: Language) -> str:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=(
                    f"Translate into {LANGUAGE_NAMES[target]} for a public election notice. "
                    "Keep names, dates, numbers and links exactly. Plain, respectful wording. "
                    "Return only the translation."
                ),
                temperature=0.2,
            ),
        )
        return (response.text or "").strip()
