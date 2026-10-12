# S2b fleet-event-journal — retrieval record (path moved since access map)

Access map (t_ea0d0e46) cited S2b with sample command:
  grep -c '"tag":"fleet-done"' $HOME/.hermes/bot/peers/events-cobrador.jsonl

At mapping time (2026-10-01) that path existed. As of this run (2026-10-12T23:5xZ)
the journal has MOVED: /home/c03rad0r/.hermes/bot/peers/ no longer contains it; the
live journal for this node is /home/c03rad0r/.hermes/state/fleet-private/events-cobrador.jsonl
(12,796,474 bytes, mtime 2026-10-12). Both paths probed; fleet-private copy live.

Probes executed this run (verbatim outputs in this dir):
- grep -c calib events-cobrador.jsonl             -> 16
- grep -n calib events-cobrador.jsonl             -> events-cobrador-calib-lines.txt (16 lines verbatim)
- grep -c '"tag":"fleet-done"' events-cobrador.jsonl -> 8737
- grep -c 'calibration slot' events-cobrador.jsonl -> 0
- meshcore-board entries among the 16 calib lines -> 0

VERDICT for calibration slots: the 16 'calib' matches are (a) router-quality LLM-judge
CALIBRATION SAMPLES (statistical judge calibration — not instrument calibration), and
(b) unrelated register-map CALIB constants. ZERO entries are instrument-calibration
scheduling events. 'calibration slot' exact phrase: 0 hits. This journal is an
audit log of fleet task events; no calibration-slot create/edit/reschedule/delete/
approve events exist in it.
