import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { api } from "../../lib/api/client";
import {
  clampMaxPerDay,
  DEFAULT_MAX_PER_DAY,
  describeChoice,
  errorMessage,
  FREQUENCY_OPTIONS,
  type Frequency,
  LANGUAGE_OPTIONS,
  type Language,
  type Mode,
  toggleLanguage,
} from "./subscribe-rules";

type Step = "details" | "code" | "subscribed" | "removed";

export function SubscribeForm() {
  const [step, setStep] = useState<Step>("details");
  const [removing, setRemoving] = useState(false);
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [languages, setLanguages] = useState<Language[]>(["en"]);
  const [mode, setMode] = useState<Mode>("instant");
  const [frequency, setFrequency] = useState<Frequency>("daily");
  const [maxPerDay, setMaxPerDay] = useState(DEFAULT_MAX_PER_DAY);

  const requestCode = useMutation({
    mutationFn: async () => {
      const { error } = removing
        ? await api.POST("/subscriptions/unsubscribe", { body: { phone } })
        : await api.POST("/subscriptions", {
            body: {
              phone,
              languages,
              mode,
              digest_frequency: frequency,
              max_per_day: maxPerDay,
            },
          });
      if (error) throw new Error(errorMessage(error, "Could not send a code. Check the number."));
    },
    onSuccess: () => setStep("code"),
  });

  const confirm = useMutation({
    mutationFn: async () => {
      const { data, error } = await api.POST("/subscriptions/confirm", {
        body: { phone, code: code.trim() },
      });
      if (error || !data) throw new Error(errorMessage(error, "That code did not work."));
      return data;
    },
    onSuccess: (data) => setStep(data.status === "removed" ? "removed" : "subscribed"),
  });

  const sendCode = (event: FormEvent) => {
    event.preventDefault();
    requestCode.mutate();
  };
  const checkCode = (event: FormEvent) => {
    event.preventDefault();
    confirm.mutate();
  };

  if (step === "subscribed") {
    return (
      <div role="status" className="space-y-3">
        <h2 className="text-xl font-bold">You are subscribed</h2>
        <p className="text-secondary">{describeChoice({ mode, frequency, maxPerDay })}</p>
        <p className="text-sm text-muted">
          To change this, fill the form in again with the same number. To stop, use "Stop texts"
          below.
        </p>
      </div>
    );
  }

  if (step === "removed") {
    return (
      <div role="status" className="space-y-3">
        <h2 className="text-xl font-bold">Your number has been removed</h2>
        <p className="text-secondary">You will not get any more texts from Clarion.</p>
      </div>
    );
  }

  if (step === "code") {
    return (
      <form onSubmit={checkCode} className="space-y-4">
        <h2 className="text-xl font-bold">Enter the code we texted you</h2>
        <p className="text-secondary">
          We sent a 6 digit code to {phone}. It works for 10 minutes. Nothing is saved until you
          enter it.
        </p>
        <div>
          <label htmlFor="code" className="mb-1 block font-semibold">
            Code
          </label>
          <Input
            id="code"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            inputMode="numeric"
            autoComplete="one-time-code"
            maxLength={8}
            required
          />
        </div>
        <div className="flex flex-wrap gap-3">
          <Button type="submit" disabled={confirm.isPending}>
            {confirm.isPending ? "Checking..." : removing ? "Remove my number" : "Confirm"}
          </Button>
          <Button type="button" variant="quiet" onClick={() => setStep("details")}>
            Back
          </Button>
        </div>
        {confirm.error ? <p role="alert">{confirm.error.message}</p> : null}
      </form>
    );
  }

  return (
    <form onSubmit={sendCode} className="space-y-6">
      <div>
        <label htmlFor="phone" className="mb-1 block font-semibold">
          Phone number
        </label>
        <Input
          id="phone"
          type="tel"
          value={phone}
          onChange={(event) => setPhone(event.target.value)}
          placeholder="0803 123 4567 or +234 803 123 4567"
          autoComplete="tel"
          required
        />
      </div>

      {removing ? (
        <p className="text-secondary">
          We will text a code to this number so only its owner can stop the messages.
        </p>
      ) : (
        <>
          <fieldset>
            <legend className="mb-1 font-semibold">Languages</legend>
            <p className="mb-2 text-sm text-muted">
              Pick the ones you read. If a correction is not ready in your first choice, we try the
              next.
            </p>
            <div className="flex flex-wrap gap-2">
              {LANGUAGE_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className="flex min-h-11 items-center gap-2 rounded-control border border-border bg-surface px-3"
                >
                  <input
                    type="checkbox"
                    checked={languages.includes(option.value)}
                    onChange={() =>
                      setLanguages((current) => toggleLanguage(current, option.value))
                    }
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset>
            <legend className="mb-1 font-semibold">How often</legend>
            <div className="grid gap-2">
              <label className="flex min-h-11 items-center gap-2">
                <input
                  type="radio"
                  name="mode"
                  checked={mode === "instant"}
                  onChange={() => setMode("instant")}
                />
                Right away, each time a correction goes out
              </label>
              <label className="flex min-h-11 items-center gap-2">
                <input
                  type="radio"
                  name="mode"
                  checked={mode === "digest"}
                  onChange={() => setMode("digest")}
                />
                One bundled text
              </label>
            </div>
            {mode === "digest" ? (
              <div className="mt-2">
                <label htmlFor="frequency" className="mb-1 block text-sm font-semibold">
                  Send the bundle
                </label>
                <select
                  id="frequency"
                  value={frequency}
                  onChange={(event) => setFrequency(event.target.value as Frequency)}
                  className="min-h-11 w-full rounded-control border border-border bg-surface px-3"
                >
                  {FREQUENCY_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            ) : null}
          </fieldset>

          <div>
            <label htmlFor="max" className="mb-1 block font-semibold">
              Most texts per day
            </label>
            <Input
              id="max"
              type="number"
              min={1}
              max={10}
              value={maxPerDay}
              onChange={(event) => setMaxPerDay(clampMaxPerDay(Number(event.target.value)))}
            />
            <p className="mt-1 text-sm text-muted">
              Never more than this, even if many corrections go out. Extra ones wait for the next
              day.
            </p>
          </div>

          <p className="rounded-control bg-canvas p-3 text-sm text-secondary">
            You will get: {describeChoice({ mode, frequency, maxPerDay })}
          </p>
        </>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <Button
          type="submit"
          disabled={requestCode.isPending || (!removing && languages.length === 0)}
        >
          {requestCode.isPending ? "Sending code..." : "Text me a code"}
        </Button>
        <button
          type="button"
          className="text-sm text-secondary underline"
          onClick={() => setRemoving((current) => !current)}
        >
          {removing ? "Back to subscribing" : "Stop texts"}
        </button>
      </div>
      {requestCode.error ? <p role="alert">{requestCode.error.message}</p> : null}
    </form>
  );
}
