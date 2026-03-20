"""Tests for speaker ID debouncing."""

from src.debouncer import debounce_speaker_ids


class TestDebounceSpeakerIds:
    def test_empty_input(self):
        assert debounce_speaker_ids([]) == []

    def test_keeps_stable_runs(self):
        ids = [0] * 20 + [1] * 20
        assert debounce_speaker_ids(ids, min_hold_frames=10) == ids

    def test_replaces_short_middle_flicker_with_previous_stable(self):
        ids = [0] * 50 + [1] * 3 + [0] * 50
        result = debounce_speaker_ids(ids, min_hold_frames=10)
        assert result == [0] * 103

    def test_replaces_short_initial_run_with_next_stable(self):
        ids = [1] * 3 + [0] * 20
        result = debounce_speaker_ids(ids, min_hold_frames=10)
        assert result == [0] * 23

    def test_none_segments_are_never_modified(self):
        ids = [None] * 10 + [0] * 50
        result = debounce_speaker_ids(ids, min_hold_frames=15)
        assert result == ids

    def test_short_run_without_stable_neighbor_is_left_unchanged(self):
        ids = [1] * 3
        result = debounce_speaker_ids(ids, min_hold_frames=10)
        assert result == ids