import { useState } from "react";
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
    <li className="rounded-md border border-slate-200 p-3">
      <div className="flex items-center justify-between gap-2">
        <h4 className="font-semibold">{name}</h4>
        <span className={saved?.is_approved ? "text-brand" : "text-muted"}>
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
            className="mt-2 w-full rounded-md border border-slate-300 p-2"
          />
          <div className="mt-2 flex flex-wrap gap-2">
            {changed ? (
              <button
                type="button"
                disabled={busy || text.trim() === ""}
                onClick={() => {
                  onDraft(language, text);
                  setEdited(null);
                }}
                className="rounded-md border border-slate-300 px-3 py-1"
              >
                Save {name} edit
              </button>
            ) : null}
            {!saved.is_approved && !changed ? (
              <button
                type="button"
                disabled={busy}
                onClick={() => onApprove(language)}
                className="rounded-md bg-brand px-3 py-1 font-semibold text-white disabled:opacity-60"
              >
                Approve {name}
              </button>
            ) : null}
          </div>
        </>
      ) : (
        <button
          type="button"
          disabled={busy}
          onClick={() => onDraft(language)}
          className="mt-2 rounded-md border border-slate-300 px-3 py-1"
        >
          Draft {name} translation
        </button>
      )}
    </li>
  );
}

export function TranslationsPanel(props: Props) {
  return (
    <section aria-label="Translations" className="space-y-2">
      <h3 className="font-bold">Translations</h3>
      <p className="text-sm text-muted">
        A native speaker must approve each language before the correction can be approved.
      </p>
      <ul className="space-y-2">
        {TARGET_LANGUAGES.map((language) => (
          <TranslationRow key={language} {...props} language={language} />
        ))}
      </ul>
    </section>
  );
}
