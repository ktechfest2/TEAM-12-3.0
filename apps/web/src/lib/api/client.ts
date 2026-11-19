import createClient from "openapi-fetch";
import { getSession } from "../auth/session";
import { env } from "../env";
import type { paths } from "./schema.gen";

/** Typed API client generated from contracts/openapi.json. Run `make contract` after API changes. */
export const api = createClient<paths>({ baseUrl: env.apiBaseUrl });

// Attach the reviewer token, when there is one, to every request.
api.use({
  onRequest({ request }) {
    const session = getSession();
    if (session) request.headers.set("Authorization", `Bearer ${session.token}`);
    return request;
  },
});
