"""Drafts translations for review. Drafts are never published until a native
speaker approves them (see domain.rules.ensure_publishable)."""

from collections.abc import Iterable

from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.domain.enums import Language
from clarion_api.domain.models import Localisation, MasterMessage


async def draft_localisations(
    message: MasterMessage, languages: Iterable[Language], *, llm: LanguageModel
) -> tuple[Localisation, ...]:
    drafts: list[Localisation] = []
    for language in languages:
        if language is Language.ENGLISH:
            continue
        text = await llm.translate(message.summary, target=language)
        drafts.append(Localisation(language=language, text=text))
    return tuple(drafts)
