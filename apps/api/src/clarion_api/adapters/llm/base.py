from collections.abc import Sequence
from typing import Protocol

from clarion_api.domain.enums import Language
from clarion_api.domain.models import SourcePassage, VerdictResult


class LanguageModel(Protocol):
    async def embed(self, texts: Sequence[str]) -> list[list[float]]: ...

    async def judge_claim(self, claim: str, passages: Sequence[SourcePassage]) -> VerdictResult: ...

    async def translate(self, text: str, *, target: Language) -> str: ...
