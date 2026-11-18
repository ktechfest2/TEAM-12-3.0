# AGENTS.md (infra)

- Infrastructure files describe environments; they never hold secrets. Secret values are `sync: false` in Render and set in each provider's dashboard.
- Keep the production mapping table in `README.md` true. If you add a service, add its generic interface (an env var name) first, then the vendor.
- Local services must match production major versions (Postgres 17, Redis compatible 7+).
- Do not add a vendor SDK to the API to reach infrastructure that has a standard protocol (Postgres, Redis, S3).
