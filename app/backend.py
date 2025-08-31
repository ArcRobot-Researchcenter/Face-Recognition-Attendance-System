import cv2, numpy as np
import time
from pathlib import Path
from .config import (
    DATASET_DIR, MODELS_DIR, MIN_FACE_SIZE, CAMERA_INDEX,
    FRAME_WIDTH, FRAME_HEIGHT, LBPH_RADIUS, LBPH_NEIGHBORS,
    LBPH_GRID_X, LBPH_GRID_Y, THRESHOLD
)
from .utils import get_cascade, users_df, log_attendance

# ---------- helpers ----------

def clean_name(s):
    """Normalize a name string and decide if it's usable."""
    try:
        s = str(s).strip()
    except Exception:
        return "", False
    if not s:
        return "", False
    if s.isnumeric():   # '0', '123' shouldn't be used as a name
        return "", False
    return s, True

def fallback_name_from_dataset(label: int):
    """Find the first dataset folder starting with '<label>_' and extract the name part."""
    try:
        for d in DATASET_DIR.glob(f"{label}_*"):
            if d.is_dir():
                raw = d.name.split("_", 1)[1] if "_" in d.name else d.name
                # turn underscores into spaces: Alex_Raji -> Alex Raji
                name = raw.replace("_", " ").strip()
                name, ok = clean_name(name)
                if ok:
                    return name
    except Exception:
        pass
    return ""  # no fallback

def resolve_name(label: int, id_to_name: dict):
    """
    Resolve a human-readable name for 'label':
    1) from users.csv mapping (id_to_name),
    2) fallback to dataset folder name,
    3) return "" if neither works.
    """
    name_csv = id_to_name.get(label, "")
    name_csv, ok = clean_name(name_csv)
    if ok:
        return name_csv, "csv"
    # fallback
    name_ds = fallback_name_from_dataset(label)
    if name_ds:
        return name_ds, "dataset"
    return "", "none"

def write_trained_labels_file(label_set):
    """Save which IDs were used to train, for verification."""
    try:
        out = MODELS_DIR / "trained_labels.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write("Trained IDs (from users.csv): " + ", ".join(str(x) for x in sorted(label_set)) + "\n")
    except Exception as e:
        print(f"[WARN] Could not write trained_labels.txt: {e}")

# ---------- enrollment capture ----------

def capture_samples(person_id: int, name: str, num_samples: int = 60):
    person_dir = DATASET_DIR / f"{person_id}_{name.strip().replace(' ', '_')}"
    person_dir.mkdir(parents=True, exist_ok=True)

    face_cascade = get_cascade()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=5, minSize=MIN_FACE_SIZE
        )

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))
            count += 1
            cv2.imwrite(str(person_dir / f"{count:04d}.png"), face)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"{count}/{num_samples}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("Capturing - Press q to stop", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if count >= num_samples:
            break

    cap.release()
    cv2.destroyAllWindows()
    return count

# ---------- training ----------

def train_model():
    """
    Train LBPH recognizer from DATASET_DIR, but only for IDs present in users.csv.
    Writes the trained ID set to models/trained_labels.txt.
    """
    udf = users_df()
    valid_ids = set(int(v) for v in udf["id"].dropna().tolist())
    if not valid_ids:
        print("[ERROR] users.csv has no IDs. Add a user first.")
        return False, 0

    images, labels = [], []
    used_labels = set()

    for person_dir in DATASET_DIR.iterdir():
        if not person_dir.is_dir():
            continue
        # Expect folder like "180_Alex_Raji"
        try:
            label = int(str(person_dir.name).split("_", 1)[0])
        except Exception:
            print(f"[WARN] Skipping folder (cannot parse ID): {person_dir.name}")
            continue

        if label not in valid_ids:
            print(f"[WARN] Skipping folder not in users.csv: {person_dir.name}")
            continue

        for img_path in person_dir.glob("*.png"):
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(img)
            labels.append(label)
            used_labels.add(label)

    if not images:
        print("[ERROR] No training images found after filtering to users.csv IDs.")
        return False, 0

    print(f"[INFO] Training on IDs: {sorted(used_labels)}  (total images: {len(images)})")
    write_trained_labels_file(used_labels)

    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=LBPH_RADIUS, neighbors=LBPH_NEIGHBORS,
        grid_x=LBPH_GRID_X, grid_y=LBPH_GRID_Y
    )
    recognizer.train(images, np.array(labels, dtype=np.int32))
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / "lbph_model.yml"
    recognizer.save(str(model_path))
    print(f"[INFO] Model saved to {model_path}")
    return True, len(images)

# ---------- recognition ----------

def take_attendance():
    """
    Run recognition. Shows predicted label+confidence even when treated as Unknown.
    Holds ~2s after detection so you can read the overlay.
    """
    model_path = MODELS_DIR / "lbph_model.yml"
    if not model_path.exists():
        return "no_model"

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(model_path))

    face_cascade = get_cascade()
    udf = users_df()
    # Build id -> raw name map from users.csv
    id_to_name = {int(r.id): r.name for _, r in udf.iterrows()}
    print(f"[INFO] Known user IDs from users.csv: {sorted(id_to_name.keys())}")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    detected = None  # ("known"/"unknown", name, confidence, id)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=5, minSize=MIN_FACE_SIZE
        )

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))

            label, confidence = recognizer.predict(face)
            print(f"[DEBUG] predicted label={label}, confidence={confidence:.1f}, threshold={THRESHOLD}")

            # Try to resolve a usable name (csv -> dataset fallback)
            resolved_name, source = resolve_name(label, id_to_name)

            if confidence <= THRESHOLD and resolved_name:
                tag = f"{resolved_name} ({confidence:.1f})"
                clr = (0, 255, 0)
                log_attendance(label, resolved_name)
                print(f"[INFO] Recognized ID {label} as '{resolved_name}' via {source}")
                detected = ("known", resolved_name, confidence, label)
            else:
                reason = []
                if confidence > THRESHOLD:
                    reason.append("confidence too high")
                if not resolved_name:
                    # show what we found in csv (if anything) to aid debugging
                    raw = id_to_name.get(label, "")
                    reason.append(f"name missing/invalid (csv='{raw}')")
                rtxt = "; ".join(reason) if reason else "no match"
                tag = f"Unknown (id:{label}, {confidence:.1f})"
                clr = (0, 0, 255)
                print(f"[INFO] Treating as Unknown: {rtxt}")
                detected = ("unknown", None, None, None)

            cv2.rectangle(frame, (x, y), (x+w, y+h), clr, 2)
            cv2.putText(frame, tag, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, clr, 2)

        cv2.imshow("Take Attendance - Press q to finish", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if detected is not None:
            time.sleep(2.0)
            break

    cap.release()
    cv2.destroyAllWindows()
    return detected
