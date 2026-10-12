# S9b stackstr-schedule — retrieval record

Access map cited S9b as a 'stackstr-schedule' source with a raw sample. The map's
own deliverable tree is gone, so the exact retrieval command is not re-derivable
from the map; the two candidate stores on this host were probed this run:

1. Hermes kanban board 'stackstr' (~/.hermes/kanban/boards/stackstr/kanban.db, read-only):
   10 tasks, ALL about building the stackstr demo site (publish mirror, daemon E2E,
   web client, hosting, Amethyst interop, demo rehearsal, DEMO.md, dual-push,
   Playwright, PR gate). Zero calibration mentions. Full verbatim dump in
   stackstr-board-dump.txt (10 tasks + 0 relevant events).
2. Nostr calendar kinds (31922/31923/31924/30315) on the local relay: 0 events.

VERDICT: stackstr is a Q&A/threading demo system; it holds no calibration slots and
no audit log of any lab scheduling. NO calibration-slot events.
