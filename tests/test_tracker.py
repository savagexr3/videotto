"""Basic tests for the face tracking module."""

from src.tracker import track_face_crop

def make_bbox(cx, cy=180, w=40, h=40):
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

def expand_compressed(compressed):
    frames = []
    for x, y, count in compressed:
        frames.extend([(x, y)] * count)
    return frames

class TestTrackFaceCropBasics:
    """Basic sanity tests for track_face_crop."""

    def test_empty_input(self):
        """Empty bbox list returns empty output."""
        compressed, scene_cuts = track_face_crop([])
        assert compressed == []
        assert scene_cuts == []

    def test_single_frame_with_face(self):
        """One frame with a face returns one crop position."""
        # Face centered at (320, 180) in a 640x360 frame
        bboxes = [(300, 160, 340, 200)]
        compressed, scene_cuts = track_face_crop(bboxes, video_width=640, video_height=360)

        assert len(compressed) == 1
        assert compressed[0][2] == 1  # frame count
        assert compressed[0][0] > 0   # valid x coordinate
        assert compressed[0][1] > 0   # valid y coordinate
        assert scene_cuts == []

    def test_no_face_before_first_detection(self):
        """Frames with None bbox before first face return (-1, -1) sentinel."""
        bboxes = [None, None, None, (300, 160, 340, 200), (300, 160, 340, 200)]
        compressed, scene_cuts = track_face_crop(bboxes, video_width=640, video_height=360)

        # First segment should be the no-face sentinel
        assert compressed[0][0] == -1
        assert compressed[0][1] == -1
        assert compressed[0][2] == 3  # 3 no-face frames

class TestTrackFaceCropRegression:
    def test_deadzone_holds_for_small_motion_inside_deadzone(self):
        bboxes = [make_bbox(320), make_bbox(325), make_bbox(328)]
        compressed, _ = track_face_crop(
            bboxes,
            video_width=640,
            video_height=360,
            deadzone_ratio=0.10,
            smoothing=0.25,
            pixel_tolerance=0,
            min_speaker_hold_frames=0,
        )

        frames = expand_compressed(compressed)
        assert frames[0] == frames[1] == frames[2]

    def test_scene_boundary_snaps_instantly(self):
        bboxes = [make_bbox(320), make_bbox(500)]
        compressed, scene_cuts = track_face_crop(
            bboxes,
            video_width=640,
            video_height=360,
            face_scenes=[(1, 10)],
            pixel_tolerance=0,
            min_speaker_hold_frames=0,
        )

        frames = expand_compressed(compressed)
        assert scene_cuts == [1]
        assert frames[1][0] == 500

    def test_speaker_switch_snaps_instantly(self):
        bboxes = [make_bbox(320), make_bbox(500)]
        compressed, scene_cuts = track_face_crop(
            bboxes,
            video_width=640,
            video_height=360,
            speaker_track_ids=[0, 1],
            pixel_tolerance=0,
            min_speaker_hold_frames=0,
        )

        frames = expand_compressed(compressed)
        assert scene_cuts == [1]
        assert frames[1][0] == 500