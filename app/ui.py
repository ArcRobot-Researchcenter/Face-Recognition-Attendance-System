import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser, threading, time
import pyttsx3
import pandas as pd
from ttkbootstrap import Style
from app.config import USERS_CSV, ATTENDANCE_CSV
from app.utils import ensure_dirs, users_df, save_users_df, attendance_df, speak
from app.backend import capture_samples, train_model, take_attendance
from app.exporter import export_attendance_to_excel, export_attendance_to_pdf

APP_TITLE = "FACE RECOGNITION ATTENDANCE SYSTEM"
URL = "https://academicprojectworld.com/"

# ----- Project info content -----
PROJECT_INFO = (
    "GROUP MEMBER / MATRIC NUMBER\n"
    "1. ADEDEJI QUDUS — 2330110068\n"
    "2. ANJORIN OLUWATOBI DANIEL — 2330110012\n"
    "3. ADEJIMI SAMUEL AYOMIDE — 2330110003\n\n"
    "SUPERVISOR\n"
    "MRS MORADEYO"
)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x640")
        self.resizable(False, False)
        self.style = Style(theme="flatly")
        ensure_dirs()

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 175)
        self.after(300, lambda: speak(self.engine, f"Welcome to {APP_TITLE}"))

        self.build_home()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def header(self, parent, text):
        lbl = ttk.Label(parent, text=text, font=("Segoe UI", 18, "bold"))
        lbl.pack(pady=10)

    def footer(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(side="bottom", fill="x", pady=8)
        dev = ttk.Label(frm, text="Developed by Raji / ARC ROBOTIC LTD", cursor="hand2", foreground="#0d6efd")
        dev.pack(side="left", padx=12)
        dev.bind("<Button-1>", lambda e: webbrowser.open(URL))
        ttk.Button(frm, text="Close", command=self.destroy).pack(side="right", padx=12)

    def build_home(self):
        self.clear()
        wrap = ttk.Frame(self, padding=20)
        wrap.pack(fill="both", expand=True)

        self.header(wrap, APP_TITLE)

        grid = ttk.Frame(wrap)
        grid.pack(pady=14)

        btns = [
            ("Take Attendance", self.on_take_attendance),
            ("Check Attendance", self.on_check_attendance),
            ("Check List of Users", self.on_check_users),
            ("Delete User", self.on_delete_user),
            ("Delete Attendance", self.on_delete_attendance),
            ("Enroll New User", self.on_enroll_user),
            ("Export Attendance", self.on_export_menu),
        ]

        for i, (text, cmd) in enumerate(btns):
            b = ttk.Button(grid, text=text, width=28, command=cmd)
            b.grid(row=i // 2, column=i % 2, padx=15, pady=10, sticky="ew")

        # ----- Project info box on home -----
        info_frame = ttk.LabelFrame(wrap, text="Project Info")
        info_frame.pack(fill="x", pady=12)
        lbl = ttk.Label(info_frame, text=PROJECT_INFO, justify="left", font=("Consolas", 10))
        lbl.pack(anchor="w", padx=10, pady=8)

        self.footer(wrap)

    # -------- Actions --------
    def on_take_attendance(self):
        speak(self.engine, "Taking attendance. Camera opening.")
        result = take_attendance()
        if result == "no_model":
            messagebox.showwarning("No Model", "No trained model found. Please enroll and train first.")
            speak(self.engine, "No trained model found. Please enroll and train first.")
            return
        state, name, conf, pid = result
        if state == "known":
            speak(self.engine, "Attendance taken successfully.")
            messagebox.showinfo("Success", f"Attendance recorded for {name}.")
        else:
            speak(self.engine, "Unknown user.")
            messagebox.showwarning("Unknown", "Unknown user. Please enroll.")
        self.build_home()

    def on_check_attendance(self):
        self.clear()
        wrap = ttk.Frame(self, padding=12)
        wrap.pack(fill="both", expand=True)
        self.header(wrap, "Attendance Records")
        df = attendance_df()

        tree = ttk.Treeview(wrap, columns=("date","time","id","name"), show="headings", height=18)
        for c, w in zip(("date","time","id","name"), (120, 120, 80, 420)):
            tree.heading(c, text=c.title())
            tree.column(c, width=w, anchor="center")
        for _, r in df.iterrows():
            tree.insert("", "end", values=(r["date"], r["time"], int(r["id"]), str(r["name"])))
        tree.pack(fill="both", expand=True, pady=10)

        # Export buttons here too
        btn_row = ttk.Frame(wrap)
        btn_row.pack(pady=6)
        ttk.Button(btn_row, text="Export to Excel (.xlsx)", command=self.export_excel).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Export to PDF (.pdf)", command=self.export_pdf).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Back", command=self.build_home).pack(side="left", padx=12)

        self.footer(wrap)

    def on_check_users(self):
        self.clear()
        wrap = ttk.Frame(self, padding=12)
        wrap.pack(fill="both", expand=True)
        self.header(wrap, "Registered Users")
        df = users_df()

        tree = ttk.Treeview(wrap, columns=("id","name","sex","department"), show="headings", height=18)
        for c, w in zip(("id","name","sex","department"), (80, 300, 120, 300)):
            tree.heading(c, text=c.title())
            tree.column(c, width=w, anchor="center")
        for _, r in df.iterrows():
            tree.insert("", "end", values=(int(r["id"]), r["name"], r.get("sex",""), r.get("department","")))
        tree.pack(fill="both", expand=True, pady=10)
        ttk.Button(wrap, text="Back", command=self.build_home).pack(pady=6)
        self.footer(wrap)

    def on_delete_user(self):
        speak(self.engine, "Are you sure you want to delete a user account?")
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete a user account?"):
            return
        self.clear()
        wrap = ttk.Frame(self, padding=12)
        wrap.pack(fill="both", expand=True)
        self.header(wrap, "Delete User")

        df = users_df()

        tree = ttk.Treeview(wrap, columns=("id","name","sex","department"), show="headings", height=16)
        for c, w in zip(("id","name","sex","department"), (80, 300, 120, 300)):
            tree.heading(c, text=c.title()); tree.column(c, width=w, anchor="center")
        for _, r in df.iterrows():
            tree.insert("", "end", values=(int(r["id"]), r["name"], r.get("sex",""), r.get("department","")))
        tree.pack(fill="both", expand=True, pady=10)

        def do_delete():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Info", "Select a user to delete."); return
            item = tree.item(sel[0])["values"]
            pid = int(item[0]); name = str(item[1])
            # remove from users.csv
            df2 = df[df["id"] != pid]
            save_users_df(df2)
            # remove dataset folder
            from app.config import DATASET_DIR
            import shutil
            for d in DATASET_DIR.glob(f"{pid}_*"):
                if d.is_dir():
                    shutil.rmtree(d, ignore_errors=True)
            speak(self.engine, "User deleted successfully.")
            messagebox.showinfo("Deleted", f"Deleted user: {name} (ID {pid})")
            self.build_home()

        ttk.Button(wrap, text="Delete Selected User", command=do_delete).pack(pady=6)
        ttk.Button(wrap, text="Back", command=self.build_home).pack(pady=6)
        self.footer(wrap)

    def on_delete_attendance(self):
        self.clear()
        wrap = ttk.Frame(self, padding=12)
        wrap.pack(fill="both", expand=True)
        self.header(wrap, "Delete Attendance")

        att = attendance_df()

        tree = ttk.Treeview(wrap, columns=("date","time","id","name"), show="headings", height=16)
        for c, w in zip(("date","time","id","name"), (120,120,80,420)):
            tree.heading(c, text=c.title()); tree.column(c, width=w, anchor="center")
        for _, r in att.iterrows():
            tree.insert("", "end", values=(r["date"], r["time"], int(r["id"]), r["name"]))
        tree.pack(fill="both", expand=True, pady=10)

        def do_delete_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Info", "Select at least one record to delete."); return
            rows = [tree.item(s)["values"] for s in sel]
            df = attendance_df()
            for date, time_str, pid, name in rows:
                df = df[~((df["date"]==date) & (df["time"]==time_str) & (df["id"]==int(pid)))]
            df.to_csv(ATTENDANCE_CSV, index=False)
            speak(self.engine, "Attendance deleted successfully.")
            messagebox.showinfo("Deleted", "Selected attendance record(s) deleted.")
            self.on_delete_attendance()

        ttk.Button(wrap, text="Delete Selected", command=do_delete_selected).pack(pady=6)
        ttk.Button(wrap, text="Back", command=self.build_home).pack(pady=6)
        self.footer(wrap)

    def on_enroll_user(self):
        self.clear()
        wrap = ttk.Frame(self, padding=12)
        wrap.pack(fill="both", expand=True)
        self.header(wrap, "Enroll New User")

        frm = ttk.Frame(wrap); frm.pack(pady=10)

        ttk.Label(frm, text="User ID:").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        e_id = ttk.Entry(frm, width=25); e_id.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(frm, text="Name:").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        e_name = ttk.Entry(frm, width=25); e_name.grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(frm, text="Sex:").grid(row=2, column=0, sticky="e", padx=8, pady=6)
        e_sex = ttk.Combobox(frm, values=["Male","Female","Other"], width=22); e_sex.grid(row=2, column=1, padx=8, pady=6)

        ttk.Label(frm, text="Department:").grid(row=3, column=0, sticky="e", padx=8, pady=6)
        e_dept = ttk.Entry(frm, width=25); e_dept.grid(row=3, column=1, padx=8, pady=6)

        info = ttk.Label(wrap, text="After clicking Enroll User, the camera will open to capture images.")
        info.pack(pady=6)

        def enroll():
            try:
                pid = int(e_id.get().strip())
                name = e_name.get().strip()
            except Exception:
                messagebox.showerror("Error", "Enter a valid integer ID and Name")
                return
            sex = (e_sex.get() or "").strip()
            dept = e_dept.get().strip()

            if not name or name.isnumeric():
                messagebox.showerror("Error", "Name is required and cannot be only numbers.")
                return

            df = users_df()
            if (df["id"] == pid).any():
                df.loc[df["id"]==pid, ["name","sex","department"]] = [name, sex, dept]
            else:
                df.loc[len(df)] = {"id": pid, "name": name, "sex": sex, "department": dept}
            save_users_df(df)
            speak(self.engine, "Starting enrollment. Look at the camera.")
            count = capture_samples(pid, name, num_samples=60)
            messagebox.showinfo("Captured", f"Captured {count} images for {name}.")
            speak(self.engine, "Training model. Please wait.")
            self.show_training_and_train()

        ttk.Button(wrap, text="Enroll User", command=enroll).pack(pady=6)
        ttk.Button(wrap, text="Back", command=self.build_home).pack(pady=6)
        self.footer(wrap)

    def show_training_and_train(self):
        dlg = tk.Toplevel(self)
        dlg.title("Training Model")
        dlg.geometry("420x160")
        ttk.Label(dlg, text="Training model, please wait...", font=("Segoe UI", 12)).pack(pady=12)
        pb = ttk.Progressbar(dlg, mode="indeterminate", length=300)
        pb.pack(pady=8)
        pb.start(10)

        def work():
            ok, n = train_model()
            time.sleep(1.0)
            pb.stop()
            dlg.destroy()
            if ok:
                speak(self.engine, "Model trained successfully.")
                messagebox.showinfo("Success", f"Model trained successfully with {n} images.")
            else:
                speak(self.engine, "Training failed. No images found.")
                messagebox.showerror("Error", "No training images found. Please enroll a user first.")
            self.build_home()

        threading.Thread(target=work, daemon=True).start()

    # ----- Export actions (home-level) -----
    def on_export_menu(self):
        # quick chooser window
        dlg = tk.Toplevel(self)
        dlg.title("Export Attendance")
        dlg.geometry("360x140")
        ttk.Label(dlg, text="Choose export format:", font=("Segoe UI", 11, "bold")).pack(pady=10)
        row = ttk.Frame(dlg); row.pack(pady=6)
        ttk.Button(row, text="Export to Excel (.xlsx)", command=lambda: [dlg.destroy(), self.export_excel()]).pack(side="left", padx=6)
        ttk.Button(row, text="Export to PDF (.pdf)", command=lambda: [dlg.destroy(), self.export_pdf()]).pack(side="left", padx=6)

    def export_excel(self):
        df = attendance_df()
        if df.empty:
            messagebox.showinfo("No Data", "No attendance to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            title="Save Attendance as Excel"
        )
        if not path:
            return
        try:
            n = export_attendance_to_excel(path)
            speak(self.engine, "Export completed.")
            messagebox.showinfo("Exported", f"Saved {n} rows to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

    def export_pdf(self):
        df = attendance_df()
        if df.empty:
            messagebox.showinfo("No Data", "No attendance to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title="Save Attendance as PDF"
        )
        if not path:
            return
        try:
            n = export_attendance_to_pdf(path, title="Attendance Report")
            speak(self.engine, "Export completed.")
            messagebox.showinfo("Exported", f"Saved {n} rows to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

if __name__ == "__main__":
    App().mainloop()
