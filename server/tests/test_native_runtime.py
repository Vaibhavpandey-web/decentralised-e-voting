"""Deployment smoke check for the native face-recognition model runtime."""
import numpy as np
import pytest

def test_native_face_models_load_and_reject_empty_frame():
    face_recognition = pytest.importorskip('face_recognition')
    cv2 = pytest.importorskip('cv2')
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    assert face_recognition.face_locations(converted, model='hog') == []
