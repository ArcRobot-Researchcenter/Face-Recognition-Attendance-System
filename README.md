
# 📌 Face Recognition Attendance System

### 👤 Developed by **ArcRobot Research Center**

## 📖 Overview

The **Face Recognition Attendance System** is a Python-based desktop application designed to automate student/staff attendance using real-time face recognition.
It combines **computer vision (OpenCV)** with a simple and intuitive **Tkinter GUI**, ensuring attendance is seamless, accurate, and paperless.

## 📽️ Watch YouTube Demo

[![Watch the video](https://img.youtube.com/vi/sLOEOvR0ZFs/0.jpg)](https://www.youtube.com/watch?v=sLOEOvR0ZFs)
https://youtu.be/sLOEOvR0ZFs?si=0ZX5vPxe2lAkNWBV


## Download Full Project with VENV (virtual environment)** 
https://drive.google.com/file/d/1jhPZ4AyZ6sPm8xPa7iWAQ9d6HpgwhX7j/view?usp=drive_link

## ✨ Features

* 🎥 **Take Attendance**: Detects and recognizes registered users via webcam.
* 📝 **Enroll New User**: Add user details (ID, Name, Sex, Department) and capture face samples.
* 🏋️ **Train Model**: Train the LBPH recognizer with the captured faces.
* ✅ **Check Attendance**: View records with Date, Time, ID, and Name.
* 👥 **Check List of Users**: View all registered users.
* ❌ **Delete User / Delete Attendance**: Manage user records and attendance logs.
* 📤 **Export Attendance**: Export logs to **Excel (.xlsx)** or **PDF (.pdf)** for reporting.
* 🔊 **Voice Feedback**: Built-in TTS to guide actions (using pyttsx3).
* 📌 **Project Info Section**: Displays group members and supervisor info on the home page.

---

## 🛠️ Tech Stack

* **Python 3.9+**
* **OpenCV** (face detection & recognition)
* **Tkinter + ttkbootstrap** (GUI)
* **pyttsx3** (Text-to-Speech)
* **Pandas** (data handling)
* **OpenPyXL** (Excel export)
* **ReportLab** (PDF export)

---

## 📂 Project Structure

```
face_recognition_attendance/
│
├── app/
│   ├── backend.py        # Face capture, training, recognition
│   ├── ui.py             # Main GUI
│   ├── utils.py          # Utilities (logging, CSV handling, TTS)
│   ├── config.py         # Configurations
│   ├── exporter.py       # Export to Excel & PDF
│   ├── dataset/          # Captured face images
│   ├── models/           # Trained model files
│   └── users.csv         # User records
│
├── requirements.txt      # Dependencies
└── README.md             # Project description
```

## 🚀 Installation & Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/ArcRobot-Researchcenter/face_recognition_attendance.git
   cd face_recognition_attendance
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   python -m app.ui
   ```

---

## 📤 Exported Reports

* **Excel**: Easy to analyze attendance data in tabular form.
* **PDF**: Printable reports for official submission.


## 📌 Future Improvements

* Date & User filters for export
* Cloud storage integration (Google Drive/Sheets)
* Web dashboard

---

## 📜 License

This project is open-source under the MIT License.
