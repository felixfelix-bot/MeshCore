# PROGRESS — t_bb4bbf91: Extract full conversion inventory from parser contract

Format: finding -> status -> files touched.

- [x] Contract located: `bench/atcut-fit/CAL-CLI-SPEC.md` (242 lines, git blob
      `378e30311600113ebf32f61979adb5ffb25eb56b`), pinned to firmware
      felixfelix-bot/MeshCore `feat/passive-mapper` @ `3fdfbc8e`. The file was
      absent on this host; pulled verbatim from fleet node dq05
      (`/home/c03rad0r/repos/meshcore/bench/atcut-fit/CAL-CLI-SPEC.md`), whose
      local `meshcore` repo main has it at the same blob (commit `2075f921`;
      prior offload run 1041 inventoried it in commit `87658144`, never pushed,
      card never written back). Status: DONE, blob hash verified locally.
      Files: bench/atcut-fit/CAL-CLI-SPEC.md (copied verbatim).
- [x] Contract read top to bottom (all 242 lines, both halves via read_file).
      9 conversions + 3 documented non-conversions identified. Status: DONE.
- [x] Inventory generated programmatically (citation splicer, never hand-typed
      quotes): `contract_conversion_inventory.md` at worktree root with
      `## Conversions` (9 entries, each with suggested snake_case name,
      directions, units, exact factor/offset, int-vs-float semantics, verbatim
      file:line citations) and `## Gaps` (9 gaps G1-G9, never to be
      implemented). Status: DONE. Files: contract_conversion_inventory.md.
- [x] Byte-exact verification: checker re-extracts all 25 citation blocks and
      byte-compares against the contract source; re-hashes the contract copy
      against the pinned blob. Result: 25/25 OK, blob match, exit 0.
      Status: DONE. Files: check scripts in worktree (gen + check), run
      evidence in REPORT.md.
- [x] Commit + push (bot remote) of deliverable + evidence: commit `c4499c1`
      (inventory + contract copy + scripts + PROGRESS), commit `1000230`
      (REPORT.md). Branch `worker-base/t_bb4bbf91` pushed to remote `bot`
      (felixfelix-bot/MeshCore); remote tip verified == local HEAD via
      `git ls-remote` after each push (observed). Status: DONE.
- [x] REPORT.md written (deliverable path/format, inventory summary,
      acceptance-criteria mapping, verification evidence, method/audit trail,
      honesty notes). Status: DONE.