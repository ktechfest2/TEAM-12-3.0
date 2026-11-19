import { describe, expect, it } from "vitest";
import { parseSse } from "./sse";

describe("parseSse", () => {
  it("reads complete events and keeps the unfinished tail", () => {
    const first = parseSse("event: snapshot\ndata: [1]\n\nevent: deliv");
    expect(first.events).toEqual([{ event: "snapshot", data: "[1]" }]);
    expect(first.rest).toBe("event: deliv");
    const second = parseSse(`${first.rest}ery\ndata: {"a":1}\n\n`);
    expect(second.events).toEqual([{ event: "delivery", data: '{"a":1}' }]);
    expect(second.rest).toBe("");
  });

  it("drops keep alive comments and handles Windows line endings", () => {
    const parsed = parseSse(": keep-alive\n\nevent: done\r\ndata: {}\r\n\r\n");
    expect(parsed.events).toEqual([{ event: "done", data: "{}" }]);
  });

  it("joins multi line data and defaults the event name", () => {
    expect(parseSse("data: a\ndata: b\n\n").events).toEqual([{ event: "message", data: "a\nb" }]);
  });
});
