# REPORT — t_bb4bbf91: Extract full conversion inventory from parser contract

## Deliverable (what the implementer should open)

- Artifact: **`contract_conversion_inventory.md`** (Markdown, single file)
- Path in repo (branch `worker-base/t_bb4bbf91`, commit `c4499c19`):
  **`/home/c03rad0r/worktrees/t_bb4bbf91/contract_conversion_inventory.md`**
  — repo-relative: `contract_conversion_inventory.md` (repo root).
- Format: Markdown, exactly two content sections as required:
  **`## Conversions`** (9 entries) and **`## Gaps`** (9 gaps, G1–G9).
- Also shipped in the same commit: a verbatim copy of the contract at
  `bench/atcut-fit/CAL-CLI-SPEC.md` (so the citations are resolvable without
  another host) plus the generator and checker scripts
  (`bench/atcut-fit/gen_inventory.py`, `bench/atcut-fit/check_inventory.py`).
- Pushed to remote `bot` (github.com/felixfelix-bot/MeshCore), branch
  `worker-base/t_bb4bbf91`; remote tip verified == `c4499c19` via
  `git ls-remote` after push (observed output above in session).

## The contract that was inventoried

- File: `bench/atcut-fit/CAL-CLI-SPEC.md` — 242 lines, 13450 bytes,
  git blob `378e30311600113ebf32f61979adb5ffb25eb56b`.
- It is the parser contract for the serial `cal <k> <T0>` command, pinned to
  firmware felixfelix-bot/MeshCore `feat/passive-mapper` @
  `3fdfbc8e120e13d7543fe224c380e27533e720aa`.
- Discovery path (the "supplied with this task" artifact): the file does not
  exist on this host; every plausible local location was swept (repo trees,
  all git branches of meshcore-fork-fix, kanban attachments, session DBs,
  fleet queue state — details in the Method section). It was located on fleet
  node dq05 at `/home/c03rad0r/repos/meshcore/bench/atcut-fit/CAL-CLI-SPEC.md`
  (that node's local `meshcore` repo main, commit `2075f921`), fetched via
  scp, and hash-verified: sha1 blob `378e30311600113ebf32f61979adb5ffb25eb56b`
  matches the dq05 git blob and the working-tree copy byte-for-byte.
- A prior offloaded run of this same card (run 1041 on dq05, commit `87658144`)
  had already produced an inventory of the same contract; its writeback never
  reached the board (card still `triage`, all runs blocked
  `fleet-offload:cobrador`). This run re-derived the inventory independently
  from the contract bytes (the generator never sees the prior artifact) and
  the two agree: 9 conversions, 9 gaps. The prior artifact was used only as a
  post-hoc cross-check, not as a source.

## Inventory contents (summary)

Conversions (each entry: suggested snake_case name, direction(s), units,
exact factor/offset, int-vs-float semantics, verbatim file:line citations):

1. `parsearg_to_f32` — decimal ASCII -> IEEE-754 float32
   (`v = v*10 + digit`; `v += digit * scale; scale *= 0.1f`; atof-style,
   `-0` -> 0x80000000; no NaN; +inf possible) — CAL-CLI-SPEC.md:59-63, 67-68,
   118-120, 74-76, 92-93.
2. `parsed_f32_pass_through` — float32 -> float32, "NO scaling, multiplier,
   or fixed-point is applied anywhere" — :110-114.
3. `temp_to_offset_ppm` — degC -> ppm, `offset_ppm = -k*(T-T0)^2`
   (explicit negation) — :99-101, :104.
4. `ppm_to_hz` — ppm -> Hz, `offset_hz = ppm * freq_MHz` — :102-103.
5. `clamp_offset_ppm_300` — clamp to ±300 ppm — :92-95.
6. `format_k_t0_echo` — float32 -> decimal strings, `%.6g` for k / `%.2f`
   for T0, display only — :30, :32-33, :121-127, :128-129, :188-191.
7. `pack_cal_blob` — float32 pair -> 15-byte LE blob and bit-identical
   reverse (memcpy, native LE; magic 0x5343; version byte 0) — :133-137,
   :139-149, :151-157, :159-165.
8. `k_to_milliunits_display` — float32 k -> milli-units (×1000), `%d.%03d`,
   display only — :167-170.
9. `t0_to_centidegrees_display` — float32 T0 -> centi-degrees (×100),
   `%d.%02d`, display only — :167-170.

Plus 3 documented items deliberately NOT counted as conversions (semantic
gate `k >= 0.0f` :105-109; |T_die − T0| ≤ 60 °C validity band :198-203;
thermal EMA seed `_temp_ema = T0` :155-157).

Gaps (never to be implemented): G1 raw counts <-> ppm (grep-verified absent
from the contract); G2 Hz -> ppm inverse; G3 offset_ppm -> temp inverse;
G4 initial fraction-scale constant; G5 value/source of freq_MHz; G6
boot-display integer-split rounding rule; G7 ±300 ppm clamp ordering vs
ppm->Hz; G8 inverse of the display scalings; G9 die-temp EMA recurrence.

## Acceptance-criteria mapping

- "Every conversion in the contract appears exactly once, with a verbatim
  file:line citation and copied source text" — 9 entries, each cited with
  blockquoted verbatim source text spliced from the contract bytes; the
  checker confirms 25/25 citation blocks byte-identical to
  bench/atcut-fit/CAL-CLI-SPEC.md at the cited line ranges, exit 0.
- "No conversion is invented; anything not documented lives in ## Gaps" —
  every entry's factor/semantics are quoted directly; inverse/absent
  directions are in Gaps G1-G9; the 3 documented non-conversions are
  explicitly excluded with citations.
- "Numeric factors and int-vs-float semantics are transcribed exactly, not
  normalized or rounded" — factors are quoted as printed (×1000, ×100,
  ±300, `%.6g`/`%.2f`, `v*10`, `scale *= 0.1f`, `-k*(T-T0)^2`,
  `ppm * freq_MHz`, 15-byte layout incl. magic `43 53`); the -0.0f /
  0x80000000 / no-NaN / +inf semantics are quoted; unicode °C² and − are
  preserved as printed.
- "Artifact path and format are stated explicitly" — see the Deliverable
  section at the top of this report.

## Verification evidence (observed)

- `python3 check_inventory.py` output:
  `contract sha1 blob: 378e30311600113ebf32f61979adb5ffb25eb56b
  pinned-match=True`
  `citation blocks byte-verified OK: 25   FAILED: 0`
  `entry headings: [parsearg_to_f32, parsed_f32_pass_through,
  temp_to_offset_ppm, ppm_to_hz, clamp_offset_ppm_300, format_k_t0_echo,
  pack_cal_blob, k_to_milliunits_display, t0_to_centidegrees_display]`
  `gaps: [9 names] (9 total)` — exit 0.
- `git push bot worker-base/t_bb4bbf91` -> `* [new branch]
  worker-base/t_bb4bbf91 -> worker-base/t_bb4bbf91`;
  `git ls-remote bot worker-base/t_bb4bbf91` -> `c4499c19b84c...` == HEAD.

## Method (how the contract was found — full audit trail)

1. Repo `meshcore-fork-fix` working tree swept: no `contracts/` dir, no
   parser.md anywhere; `git ls-tree` across all 13 local/remote refs: zero
   `contracts/` paths. HEAD tree has no contract file.
2. Kanban board `meshcore` (card t_bb4bbf91, status triage, assignee
   worker-base): card body = this task verbatim; no attachments
   (task_attachments has 15 rows, none for this card); no parent links
   (task_links empty for this id); all 3 runs 0s scheduled/blocked, never
   executed.
3. Sibling cards established the pipeline: t_d6484f25/t_8f776e31
   ("Document/Re-derive `cal <k> <T0>` parser contract...") -> deliverable
   `notes/cal-parser-contract.md` in workspace
   `/home/c03rad0r/worktrees/t_e1408991` (which contains only an unrelated
   insertion-loss file); those cards are archived-stale, never ran.
4. Filesystem sweeps: `/home/c03rad0r` maxdepth 6-7 for `*contract*`,
   `parser.md`, `notes/cal-parser*` — no hits in any repo/worktree.
5. Session DBs (worker-base state.db, recover_work copies) grepped for
   `contracts/parser`, `cal-parser` — only this session's own messages.
6. Fleet queue state (`fleet_queue_state.json`) shows the card as a
   fleet-task claimed by actor `dq05` -> SSH'd to fleet node dq05; found
   the contract in that node's `repos/meshcore` bench directory and the
   prior run's inventory + commit `87658144` (local-only, unpushed).
7. Pulled the contract via scp; hash-verified locally; read all 242 lines;
   generated the inventory with a citation splicer; byte-verified.

## Honesty notes

- The contract artifact was NOT supplied in this repo or workspace on this
  host; it existed only on fleet node dq05. The copy in this commit is
  byte-identical (sha1-verified) to the contract tracked in that node's
  `meshcore` repo main (commit `2075f921`, blob `378e3031...`).
- The prior run-1041 inventory on dq05 and this run agree (9 + 9). This
  run's artifact was generated before consulting the prior one, from the
  contract bytes only.
- Nothing was invented: every numeric factor in the inventory is inside a
  verbatim citation block or states "NOT stated in the contract" and points
  at a Gap.
- The dq05 local commits (`2075f921` contract, `87658144` prior inventory)
  remain unpushed on that node — outside this task's scope; noted here so
  the manager can reconcile if desired.