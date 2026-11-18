import createClient from "openapi-fetch";
import { env } from "../env";
import type { paths } from "./schema.gen";

/** Typed API client generated from contracts/openapi.json. Run `make contract` after API changes. */
export const api = createClient<paths>({ baseUrl: env.apiBaseUrl });
