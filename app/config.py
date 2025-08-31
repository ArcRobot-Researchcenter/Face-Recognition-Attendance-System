from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
MODELS_DIR = BASE_DIR / "models"
USERS_CSV = BASE_DIR / "users.csv"
ATTENDANCE_CSV = BASE_DIR / "attendance.csv"

# Camera / detection
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
MIN_FACE_SIZE = (60, 60)

# LBPH parameters
LBPH_RADIUS = 1
LBPH_NEIGHBORS = 8
LBPH_GRID_X = 8
LBPH_GRID_Y = 8
THRESHOLD = 90.0   # LBPH confidence: lower is better
