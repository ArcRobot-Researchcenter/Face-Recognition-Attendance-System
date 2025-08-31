import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import cm

from .utils import attendance_df

def export_attendance_to_excel(path: str) -> int:
    """
    Export attendance.csv to an Excel file.
    Returns number of rows exported.
    """
    df = attendance_df().copy()
    # sort by date/time then name
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce").dt.time
        df.sort_values(by=["date", "time", "name"], inplace=True)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df["time"] = df["time"].astype(str)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
        ws = writer.sheets["Attendance"]
        # set simple column widths
        widths = {"A": 14, "B": 12, "C": 10, "D": 28}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w

    return len(df)

def export_attendance_to_pdf(path: str, title: str = "Attendance Report") -> int:
    """
    Export attendance.csv to a simple, printable PDF table.
    Returns number of rows exported.
    """
    df = attendance_df().copy()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce").dt.time
        df.sort_values(by=["date", "time", "name"], inplace=True)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df["time"] = df["time"].astype(str)

    data = [["Date", "Time", "ID", "Name"]]
    data += df[["date", "time", "id", "name"]].values.tolist() if not df.empty else []

    # Build PDF
    doc = SimpleDocTemplate(path, pagesize=landscape(A4), leftMargin=1.2*cm, rightMargin=1.2*cm, topMargin=1.0*cm, bottomMargin=1.0*cm)
    styles = getSampleStyleSheet()
    elements = []

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    elements.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    elements.append(Paragraph(f"Generated: {now}", styles["Normal"]))
    elements.append(Spacer(1, 0.4*cm))

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.Color(0.97,0.97,1.0)]),
        ("FONTSIZE", (0,0), (-1,-1), 10),
    ]))

    elements.append(table)
    doc.build(elements)
    return len(data) - 1
