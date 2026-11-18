/** The only place the web app reads environment values. Vite exposes VITE_ names only. */
export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
} as const;
