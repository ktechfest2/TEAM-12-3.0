# data

`seed_sources.json`: demo official passages. Each paraphrases an INEC statement as reported by the linked outlet. Check every passage against its source before a public demo, and prefer direct INEC text.

Load more passages with `make -C apps/api seed-sources FILE=passages.json` (same JSON shape as `seed_sources.json`). A passage is identified by its URL and text, so reloading skips duplicates. Set `REPOSITORY_BACKEND=sql` to persist them in Postgres.
