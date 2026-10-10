"""MediaPipe face landmark adapter for legacy and Tasks API installations."""

import os
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from urllib.request import urlopen

import mediapipe as mp


FACE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)


def _face_landmarker_path():
    local_app_data = os.environ.get("LOCALAPPDATA")
    cache_root = Path(local_app_data) if local_app_data else Path.home() / ".cache"
    model_path = cache_root / "DashSentinel" / "face_landmarker.task"
    if model_path.is_file():
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(FACE_LANDMARKER_URL, timeout=30) as response:
        model_bytes = response.read()
    if not model_bytes:
        raise RuntimeError("MediaPipe returned an empty Face Landmarker model.")

    fd, temporary_path = tempfile.mkstemp(
        prefix="face_landmarker_", suffix=".task", dir=model_path.parent
    )
    try:
        with os.fdopen(fd, "wb") as model_file:
            model_file.write(model_bytes)
        os.replace(temporary_path, model_path)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
    return model_path


class FaceMeshAdapter:
    """Expose the legacy FaceMesh.process interface on MediaPipe Tasks builds."""

    def __init__(
        self,
        max_num_faces=3,
        refine_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        self._legacy_mesh = None
        self._landmarker = None
        self._last_timestamp_ms = 0

        if hasattr(mp, "solutions"):
            self._legacy_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=max_num_faces,
                refine_landmarks=refine_landmarks,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )
            return

        model_path = _face_landmarker_path()
        base_options = mp.tasks.BaseOptions(
            model_asset_path=str(model_path),
            delegate=mp.tasks.BaseOptions.Delegate.CPU,
        )
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_faces=max_num_faces,
            min_face_detection_confidence=min_detection_confidence,
            min_face_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self._landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()

    def close(self):
        """Release the underlying MediaPipe graph/task."""
        if self._legacy_mesh is not None:
            self._legacy_mesh.close()
            self._legacy_mesh = None
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None

    def process(self, rgb_frame):
        """Process an RGB frame and return legacy-compatible face landmarks."""
        if self._legacy_mesh is not None:
            return self._legacy_mesh.process(rgb_frame)

        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = max(self._last_timestamp_ms + 1, int(time.monotonic() * 1000))
        self._last_timestamp_ms = timestamp_ms
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        faces = [
            SimpleNamespace(landmark=landmarks)
            for landmarks in result.face_landmarks
        ]
        return SimpleNamespace(multi_face_landmarks=faces)
