# S8 fork-results-md — METHOD note + retrieval record

Access map (t_ea0d0e46) cited S8 as a dangling git blob in ~/repos/meshcore:
  command: git -C ~/repos/meshcore show d7ae93fa:examples/passive_mapper/bench/RESULTS.md
  observed at mapping time: blob 1641 B, kind=commit.

~/repos/meshcore is gone on this host (2026-10-12). Retrieved instead from the bot
remote where the same commit object d7ae93fa is the tip of branch feat/passive-mapper
(git ls-remote felixfelix-bot/MeshCore refs/heads/feat/passive-mapper ==
d7ae93fa1d0f71fa704d59c801351c28c3d9020a):

  cd /tmp && git clone --filter=blob:none --no-checkout --depth 1 --branch feat/passive-mapper \
    https://github.com/felixfelix-bot/MeshCore.git s8probe
  git -C /tmp/s8probe cat-file -p d7ae93fa:examples/passive_mapper/bench/RESULTS.md \
    > raw/08-fork-results-md/RESULTS.md

Captured file: RESULTS.md (34 lines, 1641 B) — byte-identical size to the map's blob.

## Calibration-slot relevance — NONE (this is a CERTIFICATE/DATA record source)

RESULTS.md is a calibration CERTIFICATE/data table ("passive_mapper calibration
records (per module)"), one row per calibrated module with k/T0/blob_hex — exactly the
"resulting certificate/data record" the task says to note SEPARATELY, not a scheduling
event. Its single row reads:

  | _not yet measured_ | SkyMapper Board A (LR2021) | | | | | | | 10 | | | pending: needs the freezer/dry-ice sweep, see the card |

i.e. NO calibration slot has ever been scheduled/completed through this record (row
never filled; no date, no operator, no k/T0). Zero create/edit/reschedule/delete/
approve events on any calibration slot exist in this source.

Noted per task rule "note certificate records separately if the same log exposes them":
this source exposes ONLY certificate records (and one empty placeholder), no audit log
of edits (git history of the file = the only edit trail; commit d7ae93fa message:
"docs(passive_mapper): refsweep contract no longer cites a nonexistent benchtx card").