# Code Health Scan: Additional Notable Issues

This note captures only the additional issues found in a fresh repo scan that are **not** the same as the already-known architectural concerns in `docs/architecture-review.md`.

The baseline conclusion from the earlier review still stands:

- the core runtime is strong
- the TUI still owns too much runtime/session orchestration
- the large controller/runtime-manager refactor is deferred for now

This document is intentionally narrower. It records only the standout issue and the smaller cleanup opportunities found in the current repo state after the recent cleanup pass.

## Overall verdict

Aside from the already-documented UI/runtime orchestration boundary issue, the repo looks to be in decent shape overall.

Notable signals:

- test suite passed cleanly
- pyright passed cleanly
- only a few lint issues remained

So this is **not** a case where the repo appears to have multiple additional architectural problems lurking elsewhere. The main new thing worth tracking is a state-consistency problem around provider/model transitions, plus a few smaller cleanup items.

## Major issue

### Provider/model transition paths are not transactional

The main additional issue is that some provider/model/session transition flows update app state before it is certain that the replacement provider/runtime state can be constructed successfully.

Relevant files:

- `src/kon/ui/commands.py`
- `src/kon/ui/session_ui.py`

### Where it shows up

#### `src/kon/ui/commands.py::_select_model`

This path updates:

- `self._model`
- `self._model_provider`

before provider recreation is guaranteed to succeed.

If `_create_provider(...)` fails, the UI reports the error, but some selected-model state may already have been changed while the active provider/agent runtime is still using the old provider instance.

#### `src/kon/ui/session_ui.py::_load_session`

This path loads session metadata and updates model/provider-related state while also trying to reconcile the active provider.

If provider recreation fails during session load, the code reports the error, but can still leave partially updated state behind:

- loaded session state may now be active
- selected model/provider values may reflect the resumed session
- the provider instance may still be the old one or only partially reconfigured

### Why this matters

This is not a large-architecture problem, but it is a real correctness risk.

It can produce subtle mismatches between:

- selected model/provider UI state
- active provider config
- agent runtime state
- resumed session metadata

Those failures are harder to reason about than a simple hard error because the app can continue running in a partially updated state.

### Suggested direction

Without doing the large architecture refactor, the safer short-term fix would be to make these transitions more atomic:

1. compute the target model/provider/session state first
2. build or validate the replacement provider first
3. only commit the new state to `self._model`, `self._model_provider`, `self._provider`, `self._session`, and `self._agent` after success
4. otherwise leave the old runtime state untouched

Even a small helper that stages the new state before assignment would reduce the sync-risk significantly.

## Small cleanup opportunities

### 1. `CompactionEntry.first_kept_entry_id` is currently misleading

Relevant file:

- `src/kon/session.py`

`CompactionEntry` stores `first_kept_entry_id`, and comments imply that the compacted view depends on it.

However, `Session.messages` currently reconstructs the compacted view by:

- finding the last compaction entry
- inserting the synthetic summary pair
- including message entries after the compaction entry itself

It does **not** currently use `first_kept_entry_id` to decide what to retain.

This is not a functional bug in current usage because existing callers/tests append compaction entries in a way that still makes the behavior correct. But the data model and implementation intent are slightly out of sync, which makes the field more confusing than helpful right now.

Small fix options:

- actually use `first_kept_entry_id` in `Session.messages`, or
- simplify the field/comment contract if the compaction-entry position is the real source of truth

### 2. System-prompt fallback logic is still duplicated across UI mixins

Relevant files:

- `src/kon/ui/commands.py`
- `src/kon/ui/session_ui.py`

Both files define the same `_resolve_system_prompt(...)` helper:

- use persisted `session.system_prompt` when available
- otherwise rebuild with `build_system_prompt(...)`

This is a small issue, not a major design problem, but it means the recent centralization is still only partial. If the fallback behavior changes again, both copies will need to stay in sync.

Small fix option:

- move the helper to one shared non-duplicated location used by both mixins/app paths

### 3. Lint cleanup remains in a few tool modules

Relevant files:

- `src/kon/tools/find.py`
- `src/kon/tools/grep.py`
- `src/kon/tools/web_fetch.py`

Current lint output shows unused imports of `truncate_text` in these files.

This is only a hygiene issue, but it is a useful signal that a full lint pass likely did not happen after some recent edits.

## Final assessment

The repo looks fine overall.

Aside from the already-known concerns in `docs/architecture-review.md`, the only additional issue that really stands out is the non-transactional provider/model/session transition behavior.

The other findings are small cleanup opportunities rather than signs of deeper architectural trouble.
