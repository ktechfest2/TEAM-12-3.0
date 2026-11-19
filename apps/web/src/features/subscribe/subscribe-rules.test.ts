import { describe, expect, it } from "vitest";
import { clampMaxPerDay, describeChoice, errorMessage, toggleLanguage } from "./subscribe-rules";

describe("toggleLanguage", () => {
  it("adds in the order picked and removes when picked again", () => {
    const first = toggleLanguage([], "yo");
    const second = toggleLanguage(first, "en");
    expect(second).toEqual(["yo", "en"]);
    expect(toggleLanguage(second, "yo")).toEqual(["en"]);
  });
});

describe("clampMaxPerDay", () => {
  it("keeps the number between 1 and 10", () => {
    expect(clampMaxPerDay(0)).toBe(1);
    expect(clampMaxPerDay(99)).toBe(10);
    expect(clampMaxPerDay(2.6)).toBe(3);
    expect(clampMaxPerDay(Number.NaN)).toBe(3);
  });
});

describe("describeChoice", () => {
  it("says what an instant subscriber will get", () => {
    const text = describeChoice({ mode: "instant", frequency: "daily", maxPerDay: 1 });
    expect(text).toContain("1 text a day at most");
    expect(text).toContain("as soon as");
  });

  it("says what a digest subscriber will get", () => {
    const text = describeChoice({ mode: "digest", frequency: "weekly", maxPerDay: 2 });
    expect(text).toContain("once a week");
    expect(text).toContain("2 texts a day at most");
  });
});

describe("errorMessage", () => {
  it("shows the API's sentence, or the fallback", () => {
    expect(errorMessage({ detail: "Wait a minute." }, "x")).toBe("Wait a minute.");
    expect(errorMessage({ detail: [{ msg: "bad" }] }, "Try again.")).toBe("Try again.");
    expect(errorMessage(undefined, "Try again.")).toBe("Try again.");
  });
});
