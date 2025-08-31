# Simple Face Recognition Attendance System

A single-window Tkinter app with voice prompts (offline, via pyttsx3). Buttons:
- Take Attendance
- Check Attendance
- Check List of Users
- Delete User
- Delete Attendance
- Enroll New User
- Close

## Install
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
python -m app.ui
```

## Data Files
- `app/users.csv`: id,name,sex,department
- `app/attendance.csv`: date,time,id,name (auto-created)
- `app/dataset/<id>_<Name>/*.png`: captured samples
- `app/models/lbph_model.yml`: trained model
