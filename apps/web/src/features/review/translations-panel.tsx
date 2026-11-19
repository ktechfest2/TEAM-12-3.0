import { useState } from "react";
import { Icon } from "../../components/icons";
import { Button } from "../../components/ui/button";
import { controlClass, SectionTitle } from "../../components/ui/surface";
import {
  type Language,
  languageName,
  localisationFor,
  type Message,
  TARGET_LANGUAGES,
} from "./review-rules";

type Props = {
  message: Message;
  busy: boolean;
  onDraft: (language: Language, text?: string) => void;
  onApprove: (language: Language) => void;
};

function TranslationRow({
  message,
  language,
  busy,
  onDraft,
  onApprove,
}: Props & { language: Language }) {
  const saved = localisationFor(message, language);
  const [edited, setEdited] = useState<string | null>(null);
  const text = edited ?? saved?.text ?? "";
  const changed = edited !== null && edited !== saved?.text;
  const name = languageName[language];

  return (
    <li className="rounded-control border border-line bg-surface p-4">
      <div className="flex items-center justify-between gap-2">
        <h4 className="font-semibold text-brand">{name}</h4>
        <span
          className={`inline-flex items-center gap-1.5 text-sm font-semibold ${
            saved?.is_approved ? "text-confirmed" : "text-muted"
          }`}
        >
          <Icon name={saved?.is_approved ? "checkCircle" : "clock"} size={16} />
          {saved?.is_approved ? `Approved by ${saved.approved_by}` : "Not approved"}
        </span>
      </div>
      {saved ? (
        <>
          <label htmlFor={`translation-${language}`} className="sr-only">
            {name} translation
          </label>
          <textarea
            id={`translation-${language}`}
            value={text}
            onChange={(e) => setEdited(e.target.value)}
            rows={3}
            className={`${controlClass} mt-3`}
          />
          <div className="mt-3 flex flex-wrap gap-2">
            {changed ? (
              <Button
                variant="secondary"
                size="sm"
                disabled={busy || text.trim() === ""}
                onClick={() => {
                  onDraft(language, text);
                  setEdited(null);
                }}
              >
                Save {name} edit
              </Button>
            ) : null}
            {!saved.is_approved && !changed ? (
              <Button size="sm" icon="check" disabled={busy} onClick={() => onApprove(language)}>
                Approve {name}
              </Button>
            ) : null}
          </div>
        </>
      ) : (
        <Button
          variant="secondary"
          size="sm"
          icon="language"
          className="mt-3"
          disabled={busy}
          onClick={() => onDraft(language)}
        >
          Draft {name} translation
        </Button>
      )}
    </li>
  );
}

export function TranslationsPanel(props: Props) {
  return (
    <section aria-label="Translations" className="space-y-3">
      <SectionTitle icon="language">Translations</SectionTitle>
      <p className="text-sm text-muted">
        A native speaker must approve each language before the correction can be approved.
      </p>
      <ul className="grid gap-3 sm:grid-cols-2">
        {TARGET_LANGUAGES.map((language) => (
          <TranslationRow key={language} {...props} language={language} />
        ))}
      </ul>
    </section>
  );
}
