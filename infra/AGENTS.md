# AGENTS.md (infra)

- Infrastructure files describe environments; they never hold secrets. Secret values are `sync: false` in Render and set in each provider's dashboard.
- Keep the production mapping table in `README.md` true. If you add a service, add its generic interface (an env var name) first, then the vendor.
- Local services must match production major versions (Postgres 17, Redis compatible 7+).
- Do not add a vendor SDK to the API to reach infrastructure that has a standard protocol (Postgres, Redis, S3).
- `infra/deploy/` is the self hosted deployment. `clarion.sh` must only act on resources labelled with the compose project `clarion`, must never hold or print secrets other than into the mode 700 state folder, and `destroy` must leave nothing behind. If you add a service or volume, make sure `destroy` removes it and test `up`, `destroy` on a real machine.
