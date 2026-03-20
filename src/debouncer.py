"""
Speaker ID debouncing for stable camera tracking.

Removes rapid speaker-ID bounces that cause jarring crop window snaps.
"""


def debounce_speaker_ids(speaker_track_ids, min_hold_frames=15):
    """
    Remove rapid speaker-ID bounces shorter than min_hold_frames.

    Speaker detection sometimes flickers the active-speaker label during
    crosstalk or brief classification uncertainty, producing 1-10 frame
    segments that cause jarring rapid-fire crop snaps. This pre-filter
    replaces those short segments with the surrounding stable speaker ID
    so the downstream dead-zone tracker never sees them.

    Algorithm:
      1. Run-length encode the raw IDs into (track_id, start, length) runs.
      2. For any run shorter than min_hold_frames, replace it with the
         previous stable run's ID (or the next stable run if it's the first).
      3. Expand back to a per-frame list.

    Args:
        speaker_track_ids: Per-frame list of speaker IDs (int or None).
            None means no speaker detected at that frame.
        min_hold_frames: Minimum frames a speaker must hold to be "stable".

    Returns:
        Same-length list with short flicker runs replaced by nearest stable ID.
        None segments are never modified.
    """
    if not speaker_track_ids:
        return []

    if min_hold_frames <= 1:
        return list(speaker_track_ids)

    # Run-length encode
    runs = []
    start = 0
    current_id = speaker_track_ids[0]

    for i in range(1, len(speaker_track_ids)):
        if speaker_track_ids[i] != current_id:
            runs.append([current_id, start, i - start])
            current_id = speaker_track_ids[i]
            start = i
    runs.append([current_id, start, len(speaker_track_ids) - start])

    debounced_runs = [run[:] for run in runs]

    for i, (track_id, _start, length) in enumerate(runs):
        if track_id is None or length >= min_hold_frames:
            continue

        replacement_id = None

        # Prefer previous stable non-None run
        for j in range(i - 1, -1, -1):
            prev_id, _prev_start, prev_len = debounced_runs[j]
            if prev_id is not None and prev_len >= min_hold_frames:
                replacement_id = prev_id
                break

        # If none before, use next stable non-None run
        if replacement_id is None:
            for j in range(i + 1, len(runs)):
                next_id, _next_start, next_len = runs[j]
                if next_id is not None and next_len >= min_hold_frames:
                    replacement_id = next_id
                    break

        if replacement_id is not None:
            debounced_runs[i][0] = replacement_id

    # Expand back to per-frame IDs
    result = []
    for track_id, _start, length in debounced_runs:
        result.extend([track_id] * length)

    return result