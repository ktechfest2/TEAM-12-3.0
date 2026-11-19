import { useMutation } from "@tanstack/react-query";
import { Icon } from "../../components/icons";
import { Button } from "../../components/ui/button";
import { Notice } from "../../components/ui/surface";
import { renderRenditions } from "./review-api";
import { languageName, type Rendition } from "./review-rules";

type Media = { language: Rendition["language"]; url: string };

function mediaOf(items: readonly Rendition[], format: Rendition["format"]): Media[] {
  return items.flatMap((item) =>
    item.format === format && item.media_url
      ? [{ language: item.language, url: item.media_url }]
      : [],
  );
}

/** Lets a reviewer hear each language as the voter will, and fetch the card and poster, before sending. */
export function VoiceNotesPanel({ messageId }: { messageId: string }) {
  const render = useMutation({ mutationFn: () => renderRenditions(messageId) });
  const items = render.data ?? [];
  const voices = mediaOf(items, "voice_note");
  const files = [
    ...mediaOf(items, "social_card").map((file) => ({ ...file, label: "Social card (PNG)" })),
    ...mediaOf(items, "poster_pdf").map((file) => ({ ...file, label: "Poster (PDF)" })),
  ];
  const smsFor = (language: Rendition["language"]) =>
    items.find((item) => item.format === "sms_text" && item.language === language)?.text;

  return (
    <section aria-label="Voice notes" className="space-y-3">
      <h4 className="flex items-center gap-2 text-sm font-bold">
        <Icon name="volume" size={18} className="text-brand" />
        Voice notes and shareable files
      </h4>
      <p className="text-sm text-muted">
        Voters who cannot read, or have little data, get the same approved words as audio. Listen to
        each language before you send.
      </p>

      {render.data ? null : (
        <Button
          variant="secondary"
          icon="volume"
          disabled={render.isPending}
          onClick={() => render.mutate()}
        >
          {render.isPending ? "Preparing audio..." : "Prepare voice notes"}
        </Button>
      )}
      {render.error ? <Notice tone="error">{render.error.message}</Notice> : null}

      {voices.length > 0 ? (
        <ul className="space-y-3">
          {voices.map((voice) => (
            <li
              key={voice.language}
              className="rounded-control border border-brand-200 bg-white p-3"
            >
              <p className="text-sm font-semibold">{languageName[voice.language]}</p>
              {/* biome-ignore lint/a11y/useMediaCaption: the same words are printed below as the text message */}
              <audio
                controls
                preload="none"
                src={voice.url}
                aria-label={`Voice note in ${languageName[voice.language]}`}
                className="mt-2 w-full"
              />
              {smsFor(voice.language) ? (
                <p className="mt-2 text-xs text-muted">Text message: {smsFor(voice.language)}</p>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}

      {files.length > 0 ? (
        <ul className="flex flex-wrap gap-2">
          {files.map((file) => (
            <li key={file.url}>
              <a
                href={file.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex min-h-10 items-center gap-2 rounded-control border border-line-strong bg-white px-3 text-sm font-semibold text-brand hover:bg-brand-50"
              >
                <Icon name="download" size={16} />
                {file.label}
              </a>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
