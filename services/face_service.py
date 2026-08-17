import os
import pickle
from typing import Dict, List, Tuple

import cv2
import numpy as np
from flask import current_app


class FaceService:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

    def _faces_dir(self) -> str:
        return current_app.config["FACE_DATA_DIR"]

    def _model_dir(self) -> str:
        return current_app.config["FACE_MODEL_DIR"]

    def _model_path(self) -> str:
        return os.path.join(self._model_dir(), "face_model.yml")

    def _known_faces_path(self) -> str:
        return os.path.join(self._model_dir(), "known_faces.pkl")

    def capture_faces(self, name: str, num_samples: int = 30) -> int:
        cap = cv2.VideoCapture(0)
        count = 0
        if not cap.isOpened():
            return 0
        while count < num_samples:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                count += 1
                face_img = cv2.resize(gray[y : y + h, x : x + w], (200, 200))
                cv2.imwrite(os.path.join(self._faces_dir(), f"{name}_{count}.jpg"), face_img)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{name} {count}/{num_samples}",
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2,
                )
                if count >= num_samples:
                    break
            cv2.putText(
                frame,
                "Capturing faces... Press Q to stop",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            cv2.imshow("Capture Faces", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()
        return count

    def train_model(self) -> Tuple[int, Dict[int, str]]:
        faces: List[np.ndarray] = []
        labels: List[int] = []
        known_faces: Dict[int, str] = {}
        name_to_id: Dict[str, int] = {}

        for filename in os.listdir(self._faces_dir()):
            if not filename.lower().endswith(".jpg"):
                continue
            person_name = filename.rsplit("_", 1)[0]
            if person_name not in name_to_id:
                person_id = len(name_to_id) + 1
                name_to_id[person_name] = person_id
                known_faces[person_id] = person_name
            person_id = name_to_id[person_name]
            img_path = os.path.join(self._faces_dir(), filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            faces.append(img)
            labels.append(person_id)

        if not faces:
            return 0, {}

        self.recognizer.train(faces, np.array(labels))
        self.recognizer.save(self._model_path())
        with open(self._known_faces_path(), "wb") as f:
            pickle.dump(known_faces, f)
        return len(faces), known_faces

    def load_model(self) -> Dict[int, str]:
        self.recognizer.read(self._model_path())
        with open(self._known_faces_path(), "rb") as f:
            return pickle.load(f)

    def detect_from_frame(self, frame, known_faces: Dict[int, str], threshold: int = 100):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        detections = []
        for (x, y, w, h) in faces:
            face_img = cv2.resize(gray[y : y + h, x : x + w], (200, 200))
            person_id, confidence = self.recognizer.predict(face_img)
            if confidence < threshold:
                detections.append((known_faces.get(person_id), float(confidence), (x, y, w, h)))
        return detections
