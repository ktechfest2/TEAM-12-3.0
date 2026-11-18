# AGENTS.md (apps)

- Apps talk only through HTTP and `contracts/openapi.json`. The web app never imports API code and the API never serves web assets.
- Keep the Makefile target names identical across apps so `make -C apps/<app> verify` always works.
