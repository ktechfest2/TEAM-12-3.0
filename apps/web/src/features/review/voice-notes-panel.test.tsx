import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderRenditions } from "./review-api";
import { VoiceNotesPanel } from "./voice-notes-panel";

vi.mock("./review-api", () => ({ renderRenditions: vi.fn() }));

function renderPanel() {
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <VoiceNotesPanel messageId="00000000-0000-0000-0000-0000000000a1" />
    </QueryClientProvider>,
  );
}

afterEach(cleanup);

describe("VoiceNotesPanel", () => {
  it("offers an audio player for each language, the text message and the files", async () => {
    vi.mocked(renderRenditions).mockResolvedValue([
      { language: "yo", format: "sms_text", text: "Ibo ni o wa", media_url: null },
      {
        language: "yo",
        format: "voice_note",
        text: null,
        media_url: "https://m.test/voice-yo.ogg",
      },
      {
        language: "ha",
        format: "voice_note",
        text: null,
        media_url: "https://m.test/voice-ha.ogg",
      },
      { language: "en", format: "social_card", text: null, media_url: "https://m.test/card.png" },
      { language: "en", format: "poster_pdf", text: null, media_url: "https://m.test/poster.pdf" },
    ]);
    renderPanel();
    fireEvent.click(screen.getByRole("button", { name: "Prepare voice notes" }));

    const yoruba = await screen.findByLabelText("Voice note in Yoruba");
    expect(yoruba.getAttribute("src")).toBe("https://m.test/voice-yo.ogg");
    expect(screen.getByLabelText("Voice note in Hausa").getAttribute("src")).toBe(
      "https://m.test/voice-ha.ogg",
    );
    expect(screen.getByText(/Ibo ni o wa/)).toBeTruthy();
    expect(screen.getByRole("link", { name: /Social card/ }).getAttribute("href")).toBe(
      "https://m.test/card.png",
    );
    expect(screen.getByRole("link", { name: /Poster/ }).getAttribute("href")).toBe(
      "https://m.test/poster.pdf",
    );
  });

  it("shows why the audio could not be made and keeps the button to try again", async () => {
    vi.mocked(renderRenditions).mockRejectedValue(new Error("The speech service is not set up."));
    renderPanel();
    fireEvent.click(screen.getByRole("button", { name: "Prepare voice notes" }));
    expect(await screen.findByText("The speech service is not set up.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Prepare voice notes" })).toBeTruthy();
  });
});
