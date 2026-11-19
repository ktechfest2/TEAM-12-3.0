import { useState } from "react";
import { Button } from "../../components/ui/button";
import { type Language, languageName } from "../review/review-rules";
import { voiceNoteUrl } from "./correction";

type Props = { messageId: string; language: Language };

/** Nothing is downloaded until the voter asks: one press loads and plays that language. */
export function ListenControl({ messageId, language }: Props) {
  const [state, setState] = useState<"idle" | "playing" | "failed">("idle");
  const name = languageName[language];

  if (state === "failed") {
    return (
      <p role="status" className="text-sm text-muted">
        Audio is not available right now.
      </p>
    );
  }
  if (state === "idle") {
    return (
      <Button
        size="sm"
        variant="secondary"
        icon="volume"
        aria-label={`Listen in ${name}`}
        onClick={() => setState("playing")}
      >
        Listen
      </Button>
    );
  }
  return (
    // biome-ignore lint/a11y/useMediaCaption: the same words are printed on the page
    <audio
      controls
      autoPlay
      src={voiceNoteUrl(messageId, language)}
      aria-label={`Voice note in ${name}`}
      onError={() => setState("failed")}
      className="h-11 w-full max-w-sm"
    />
  );
}
