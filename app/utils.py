from pathlib import Path
import pandas as pd
import cv2
from datetime import datetime
from .config import DATASET_DIR, MODELS_DIR, USERS_CSV, ATTENDANCE_CSV

def ensure_dirs():
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

def speak(engine, text: str):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

def get_cascade():
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    if not cascade_path.exists():
        raise FileNotFoundError("OpenCV haarcascade not found in cv2.data.haarcascades")
    return cv2.CascadeClassifier(str(cascade_path))

def users_df():
    if not USERS_CSV.exists():
        pd.DataFrame(columns=["id","name","sex","department"]).to_csv(USERS_CSV, index=False)
    return pd.read_csv(USERS_CSV, dtype={"id": int, "name": str, "sex": str, "department": str})

def save_users_df(df: pd.DataFrame):
    df.to_csv(USERS_CSV, index=False)

def attendance_df():
    if not ATTENDANCE_CSV.exists():
        pd.DataFrame(columns=["date","time","id","name"]).to_csv(ATTENDANCE_CSV, index=False)
    return pd.read_csv(ATTENDANCE_CSV, dtype={"date": str, "time": str, "id": int, "name": str})

def log_attendance(pid: int, name: str):
    df = attendance_df()
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    # Always append a new row
    df.loc[len(df)] = {"date": date_str, "time": time_str, "id": pid, "name": name}
    df.to_csv(ATTENDANCE_CSV, index=False)
    return True
