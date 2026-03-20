## What I found

* **Dead-zone ignored**: Used `abs(dx) > 0`, causing unnecessary movement.
* **Snap not applied**: Scene cuts and speaker switches were detected but still smoothed instead of snapping.
* **Uninitialized variables**: `face_x`, `face_y` used before assignment → runtime error.

## What I fixed

* Applied proper dead-zone thresholds (`dz_half_w`, `dz_half_h`).
* Implemented true snapping on scene cuts and speaker switches.
* Fixed variable order for snap logic.
* Implemented `debounce_speaker_ids` using run-length encoding.

## Debouncer design

* Keeps `None` unchanged.
* Replaces short runs with nearest stable speaker (prefer previous).
* Leaves runs unchanged if no stable neighbor exists.

## Tests

* Dead-zone stability (no movement inside zone).
* Instant snap on scene cut and speaker switch.
* Debouncer: flicker removal, edge cases, and `None` handling.

## Improvements

* Clarify handling of frame 0 scene cuts.
* Add end-to-end tests with sample clips.
