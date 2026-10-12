# S10 nostr-strfry-relay — retrieval record

Access map sample command: nak req -k 9 -l 3 ws://127.0.0.1:7780
Relay live this run (strfry on 127.0.0.1:7780; nak connect ok).

Full sweep: nak req -k 9 -l 50000 ws://127.0.0.1:7780 -> server returns at most
500 events per REQ (LIMIT honored at 500; captured file = kind9-events-500-cap.txt,
500 lines). Also probed calendar kinds 31922/31923/31924 and 30315 -> 0 events.

grep -icE 'calib' over the 500 events: 0 hits. 'calibration slot': 0 hits.
All 500 kind-9 events are hermes-relay-bridge fleet-witness/fleet-alert messages
(pubkey 4ae5fe8e137daa8a3b669cb1dcd4fc54fea7b13c57d311c9a01dd672dca27a6f, h=hermes-mgr).

VERDICT: no calibration-slot scheduling events. The relay is a fleet-telemetry audit
log; it holds no lab calibration-slot records.
