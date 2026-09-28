# pywebguard — AI assistant context

A Python security middleware library for web apps — IP filtering, rate limiting, user-agent
filtering, penetration-attempt detection, auto IP-banning, CORS, and pluggable storage/logging
backends. Supports FastAPI (async) and Flask (sync). Published to PyPI as `pywebguard`.

**Read this whole file before touching security-relevant code here** — several of the library's
advertised features have real, confirmed gaps between what the README promises and what the code
does (see "Known issues" below). Don't assume a feature works because it's documented.

## Layout

- `pywebguard/core/` — `base.py` (`Guard`/`AsyncGuard`, the orchestrator), `config.py` (pydantic v2
  models), `constants.py` (penetration-detection pattern list)
- `pywebguard/filters/` — `ip_filter.py`, `user_agent.py`
- `pywebguard/limiters/` — `rate_limit.py`
- `pywebguard/security/` — `penetration.py`, `cors.py`
- `pywebguard/storage/` — `memory.py`, `_redis.py`, `_sqlite.py`, `_tinydb.py`, `_mongodb.py`,
  `_postgresql.py` (underscore-prefixed = not re-exported from the top-level package — see #31)
- `pywebguard/logging/` — `logger.py`, `backends/{_meilisearch,_elasticsearch,_mongodb}.py`
  (only Meilisearch is actually wired up — see #24)
- `pywebguard/frameworks/` — `_fastapi.py`, `_flask.py` (two independent implementations, not a
  shared code path — Flask uses `Guard.check_request()`, FastAPI hand-rolls its own checks in
  `dispatch()`, which is why they've drifted out of sync)
- `pywebguard/utils/` — `ip.py` (`get_real_ip()` — proxy-header-aware IP extraction), `request.py`
- `pywebguard/cli.py` — `init`/`interactive`/`validate`/`test`/`ban`/`status` commands (1022 lines,
  the largest and least-tested module — several Redis code paths are broken, see #23)
- `tests/` — one file per module, 4500+ lines total. **Zero coverage on `pywebguard/logging/`.**
- `docs/` and `docs_site/` (mkdocs-material) — two separate, drifting doc trees; neither is fully
  wired into CI (see #30). Don't trust either blindly against the actual code.

## Commands

```bash
pip install -e .
pip install -r requirements.txt   # installs everything: all frameworks, all storage, all dev tools

pytest tests/              # 193 tests
black --check .            # formatting (CI checks this — see below on the version pin)
```

## Conventions

- **Formatting**: Black, pinned to `26.5.1` exactly in `requirements/dev.txt` and `setup.py`'s
  `dev` extra, and in CI (`.github/workflows/pipeline.yaml`). **Don't loosen this pin** — this repo
  already broke once from an unpinned `black>=25.1.0` combined with a CI step that installed its
  own floating, unpinned Black version, causing CI to fail on files nobody had touched. If Black
  needs upgrading, do it deliberately (reformat + bump the pin together, one PR), not by accident.
- **Commit types** (`contribution.md`): `feat`, `fix`, `hotfix`, `refactor`, `docs`, `style`,
  `test`, `chore`, `perf`, `ci`, `build`.
- **Branch naming**: `feature/your-feature-name` per `contribution.md` — align the branch's
  implied type with the PR title's type for consistency.
- **Releases — NOT release-please.** Unlike some of our other repos, this one uses a **custom**
  auto-tag-bump script embedded directly in `.github/workflows/pipeline.yaml`: on push to `main`,
  it sniffs recent commit messages against `MINOR_WORDS`/`MAJOR_WORDS`/`PATCH_WORDS` lists, bumps a
  git tag accordingly (defaulting to patch if nothing matches — so `hotfix:`/`refactor:`/etc. all
  silently default to a patch bump, which is probably fine but worth knowing), cuts a GitHub
  Release, and publishes to PyPI via `twine`. This works today; migrating it to actual
  `release-please` (like the other repos) is a real, separate piece of work someone should
  deliberately choose to do — don't assume it's already release-please-based.
- **Dependencies**: Dependabot now handles `pip` + `github-actions` weekly — don't open PRs that
  just bump a dependency.
- **Tests required**: every change needs a test. For a bug fix, the test must fail before the fix
  and pass after — never claim a bug exists without a reproducing test.
- **No AI attribution.** Never add a `Co-Authored-By: Claude …` trailer to a commit, never add
  "Generated with Claude Code" (or any mention of Claude/Anthropic/an AI tool) to a commit message
  or PR description, and never include a `claude.ai/code/session_…` link.

## Known issues (filed, several security-relevant — read before working near these areas)

A full audit was done and 13 issues filed (#19–#31), one already fixed (#19). Highlights, since
these are exactly the areas most likely to bite you if you don't already know about them:

- **`FastAPIGuard` re-implements security checks from scratch** in `dispatch()` instead of calling
  the shared `Guard.check_request()` that Flask uses — this is *why* Flask and FastAPI keep
  drifting apart (IP filter was missing entirely, #19, fixed; `X-Forwarded-For` is still ignored,
  #25, open). If you're touching FastAPI security behavior, check whether Flask already does it
  correctly and whether the fix belongs in the shared `Guard` class instead of duplicated logic.
- **`Guard`'s auto-storage-creation is broken for Redis/SQLite/TinyDB** (#22) — passes constructor
  kwargs those classes don't accept. Don't assume `GuardConfig(storage=StorageConfig(type="redis"))`
  actually works without testing it first.
- **The CLI's Redis commands reference nonexistent config attributes** (#23) — `config.storage.url`/
  `prefix` are the real fields, not `redis_url`/`redis_prefix`.
- **Elasticsearch/MongoDB logging backends are fully written but commented out** (#24) — don't
  assume "the code exists" means "the feature works." Check `logging/backends/__init__.py`'s actual
  imports.
- **Penetration-detection patterns cause false positives** on ordinary requests (#20) — a previous
  attempt to fix this was reverted same-day with no recorded discussion; understand why before
  re-attempting the same trim.
- See the full issue list on GitHub for the rest (#26–#31): nonexistent pip extras advertised in
  docs, a CORS config that allows a browser-rejected combination by default, a hardcoded wrong
  `__version__`, a broken Code-of-Conduct link (fixed alongside this file), and unpublished/drifting
  docs.

## Issue-based backlog (no agent-backlog.md here — same pattern as doctoc)

GitHub Issues is the backlog, not a markdown file. Labels: `bug` / `documentation` / `enhancement`
(existing GitHub defaults) plus `security`, `priority:critical` / `high` / `medium` / `low`, and
**`agent-ready`** — only issues with this label are well-scoped enough for an automated routine to
pick up unattended; everything else needs human judgment first (security-sensitive tuning, API
design decisions, policy calls like the Elasticsearch/MongoDB finish-or-remove question).

If you're an automated routine working this repo: query open issues filtered to `agent-ready`,
implement exactly what the issue describes, open a PR with `Closes #N` so merging closes it
automatically — don't close it yourself before the fix actually merges.
