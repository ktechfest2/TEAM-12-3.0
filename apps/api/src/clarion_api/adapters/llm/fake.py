"""Deterministic offline model for tests and keyless development.

Embeddings are hashed bags of words, so similar wording gives similar vectors.
The judge contradicts a claim when a top passage shares enough words and
contains a negation cue, which is enough to exercise every code path.
"""

import hashlib
import math
import re
from collections.abc import Sequence

from clarion_api.domain.enums import Language, Verdict
from clarion_api.domain.models import SourcePassage, VerdictResult

_WORD = re.compile(r"[\w']+", re.UNICODE)
_NEGATION_CUES = ("fake", "not issued", "false", "never", "did not", "has not")


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _WORD.findall(text)]


class FakeLanguageModel:
    def __init__(self, dimensions: int = 768) -> None:
        self.dimensions = dimensions

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        for tok in _tokens(text):
            idx = int(hashlib.blake2b(tok.encode(), digest_size=4).hexdigest(), 16)
            vec[idx % self.dimensions] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    async def judge_claim(self, claim: str, passages: Sequence[SourcePassage]) -> VerdictResult:
        claim_words = set(_tokens(claim))
        best = max(passages, key=lambda p: len(claim_words & set(_tokens(p.text))))
        overlap = len(claim_words & set(_tokens(best.text))) / max(len(claim_words), 1)
        if overlap < 0.2:
            return VerdictResult(
                verdict=Verdict.NO_OFFICIAL_STATEMENT,
                passage_id=None,
                rationale="fake: no passage overlaps the claim",
                confidence=0.9,
            )
        negated = any(cue in best.text.lower() for cue in _NEGATION_CUES)
        return VerdictResult(
            verdict=Verdict.CONTRADICTED if negated else Verdict.CONFIRMED,
            passage_id=best.id,
            rationale=f"fake: matched '{best.document_title}'",
            confidence=min(1.0, 0.5 + overlap),
        )

    async def translate(self, text: str, *, target: Language) -> str:
        return f"[{target.value}] {text}"
