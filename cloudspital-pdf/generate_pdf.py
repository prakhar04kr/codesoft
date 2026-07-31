#!/usr/bin/env python3
"""Generate Cloudspital Health Kiosk Management Platform interview PDF."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable, Flowable,
)

TEAL = HexColor("#0B6E6E")
TEAL_DARK = HexColor("#084F4F")
TEAL_LIGHT = HexColor("#E6F4F4")
ACCENT = HexColor("#C45C26")
SLATE = HexColor("#1A2B2B")
MUTED = HexColor("#4A5C5C")
LINE = HexColor("#C5D6D6")
SOFT_BG = HexColor("#F3F8F8")
WHITE = white
CARD_BORDER = HexColor("#B8D0D0")
ONLINE_BG = HexColor("#E8F7E8")
OFFLINE_BG = HexColor("#FCEEEE")
CHALLENGE_BG = HexColor("#FFF5F0")

PAGE_W, PAGE_H = A4
MARGIN = 14 * mm


class ArchitectureDiagram(Flowable):
    """Compact 2-row architecture flow with connecting arrows."""

    def __init__(self, width):
        Flowable.__init__(self)
        self.box_w = width
        self.row1 = [
            ("Patient", TEAL),
            ("Health Kiosk", TEAL_DARK),
            ("Cloud API", HexColor("#0A7A7A")),
            ("Cloudspital Backend", TEAL_DARK),
        ]
        self.row2 = [
            ("MySQL", HexColor("#0D5C5C")),
            ("Admin Dashboard", TEAL),
            ("Hospital Admin / Doctor", ACCENT),
        ]
        self.row_h = 24
        self._height = self.row_h * 2 + 28  # gap + connector

    def wrap(self, availWidth, availHeight):
        self.width = min(self.box_w, availWidth)
        self.height = self._height
        return self.width, self.height

    def _draw_row(self, c, nodes, y, left_to_right=True):
        n = len(nodes)
        gap = 18
        total_gap = gap * (n - 1)
        box_w = (self.width - total_gap) / n
        positions = []
        for i, (label, color) in enumerate(nodes):
            idx = i if left_to_right else (n - 1 - i)
            x = idx * (box_w + gap) if left_to_right else (n - 1 - i) * (box_w + gap)
            # For right-to-left we still want visual order of nodes as listed L→R
            x = i * (box_w + gap)
            c.setFillColor(color)
            c.roundRect(x, y, box_w, self.row_h, 4, fill=1, stroke=0)
            c.setFillColor(WHITE)
            # Fit font
            font = "Helvetica-Bold"
            size = 8
            while size > 6 and c.stringWidth(label, font, size) > box_w - 6:
                size -= 0.5
            c.setFont(font, size)
            tw = c.stringWidth(label, font, size)
            c.drawString(x + (box_w - tw) / 2, y + (self.row_h - size) / 2 + 0.5, label)
            positions.append((x + box_w / 2, x, box_w))
            # arrow between boxes
            if i < n - 1:
                ax1 = x + box_w + 2
                ax2 = x + box_w + gap - 2
                mid_y = y + self.row_h / 2
                c.setStrokeColor(MUTED)
                c.setFillColor(MUTED)
                c.setLineWidth(1.2)
                c.line(ax1, mid_y, ax2 - 4, mid_y)
                path = c.beginPath()
                path.moveTo(ax2, mid_y)
                path.lineTo(ax2 - 5, mid_y + 3.2)
                path.lineTo(ax2 - 5, mid_y - 3.2)
                path.close()
                c.drawPath(path, fill=1, stroke=0)
        return positions

    def draw(self):
        c = self.canv
        y1 = self.height - self.row_h - 2
        y2 = 2
        pos1 = self._draw_row(c, self.row1, y1, True)
        pos2 = self._draw_row(c, self.row2, y2, True)

        # Connector from last of row1 down then left to first of row2 area
        # Actually flow continues: Backend → MySQL (first of row2)
        # Draw from center of last row1 box down to center of first row2 box
        x_from = pos1[-1][0]
        x_to = pos2[0][0]
        c.setStrokeColor(MUTED)
        c.setFillColor(MUTED)
        c.setLineWidth(1.2)
        # vertical from bottom of row1
        top = y1
        bot = y2 + self.row_h
        mid_y = (top + bot) / 2
        # down from Backend
        c.line(x_from, top, x_from, mid_y)
        # horizontal to MySQL x
        c.line(x_from, mid_y, x_to, mid_y)
        # down into MySQL
        c.line(x_to, mid_y, x_to, bot + 5)
        path = c.beginPath()
        path.moveTo(x_to, bot)
        path.lineTo(x_to - 3.5, bot + 5.5)
        path.lineTo(x_to + 3.5, bot + 5.5)
        path.close()
        c.drawPath(path, fill=1, stroke=0)


class WorkflowDiagram(Flowable):
    """Wrapped chip workflow."""

    def __init__(self, width, steps):
        Flowable.__init__(self)
        self.box_w = width
        self.steps = steps
        self.chip_h = 16
        self.v_gap = 6
        self._height = 60  # updated in wrap

    def wrap(self, availWidth, availHeight):
        self.width = min(self.box_w, availWidth)
        # simulate layout
        from reportlab.pdfbase.pdfmetrics import stringWidth
        pad, arrow_w = 6, 11
        x, rows = 0, 1
        for step in self.steps:
            tw = stringWidth(step, "Helvetica", 7) + pad * 2
            if x + tw > self.width and x > 0:
                rows += 1
                x = 0
            x += tw + arrow_w
        self.height = rows * (self.chip_h + self.v_gap) + 2
        return self.width, self.height

    def draw(self):
        c = self.canv
        pad, arrow_w = 6, 11
        x = 0
        y = self.height - self.chip_h
        for i, step in enumerate(self.steps):
            c.setFont("Helvetica", 7)
            tw = c.stringWidth(step, "Helvetica", 7)
            chip_w = tw + pad * 2
            if x + chip_w > self.width and x > 0:
                x = 0
                y -= self.chip_h + self.v_gap
            c.setFillColor(TEAL_LIGHT)
            c.setStrokeColor(TEAL)
            c.setLineWidth(0.7)
            c.roundRect(x, y, chip_w, self.chip_h, 3, fill=1, stroke=1)
            c.setFillColor(TEAL_DARK)
            c.drawString(x + pad, y + 4.5, step)
            x += chip_w
            if i < len(self.steps) - 1:
                if x + arrow_w + 30 > self.width:
                    x = 0
                    y -= self.chip_h + self.v_gap
                else:
                    mid_y = y + self.chip_h / 2
                    c.setStrokeColor(MUTED)
                    c.setFillColor(MUTED)
                    c.setLineWidth(1)
                    c.line(x + 1, mid_y, x + arrow_w - 3, mid_y)
                    path = c.beginPath()
                    path.moveTo(x + arrow_w - 1, mid_y)
                    path.lineTo(x + arrow_w - 5, mid_y + 2.8)
                    path.lineTo(x + arrow_w - 5, mid_y - 2.8)
                    path.close()
                    c.drawPath(path, fill=1, stroke=0)
                    x += arrow_w


class SectionHeader(Flowable):
    def __init__(self, number, title, width):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.box_w = width
        self._h = 18

    def wrap(self, availWidth, availHeight):
        self.width = min(self.box_w, availWidth)
        self.height = self._h
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(TEAL)
        c.circle(8, 8, 7.5, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        num = str(self.number)
        nw = c.stringWidth(num, "Helvetica-Bold", 8)
        c.drawString(8 - nw / 2, 5.5, num)
        c.setFillColor(SLATE)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(22, 5, self.title)
        c.setStrokeColor(TEAL)
        c.setLineWidth(1.2)
        c.line(22, 1, self.width, 1)


class ColoredBox(Flowable):
    def __init__(self, text, width, styles, bg=None, accent=None):
        Flowable.__init__(self)
        self.text = text
        self.box_w = width
        self.styles = styles
        self.bg = bg or TEAL_LIGHT
        self.accent = accent or TEAL
        self._para = None

    def wrap(self, availWidth, availHeight):
        self.width = min(self.box_w, availWidth)
        self._para = Paragraph(self.text, self.styles["BoxText"])
        pw, ph = self._para.wrap(self.width - 14, availHeight)
        self.height = ph + 10
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.setStrokeColor(CARD_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(0, 0, self.width, self.height, 3, fill=1, stroke=1)
        c.setFillColor(self.accent)
        c.rect(0, 0, 3.5, self.height, fill=1, stroke=0)
        self._para.drawOn(c, 9, 5)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="DocTitle", fontName="Helvetica-Bold", fontSize=16,
        leading=19, textColor=TEAL_DARK, alignment=TA_CENTER, spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="DocSubtitle", fontName="Helvetica", fontSize=9,
        leading=11, textColor=MUTED, alignment=TA_CENTER, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="H2", fontName="Helvetica-Bold", fontSize=11,
        leading=13, textColor=TEAL_DARK, spaceBefore=5, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="H3", fontName="Helvetica-Bold", fontSize=9,
        leading=11, textColor=SLATE, spaceBefore=3, spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="Body", fontName="Helvetica", fontSize=8,
        leading=10.5, textColor=SLATE, alignment=TA_JUSTIFY, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="BodyTight", fontName="Helvetica", fontSize=8,
        leading=10, textColor=SLATE, spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="BulletText", fontName="Helvetica", fontSize=8,
        leading=10, textColor=SLATE, leftIndent=2,
    ))
    styles.add(ParagraphStyle(
        name="BoxText", fontName="Helvetica-Oblique", fontSize=8,
        leading=10.5, textColor=SLATE,
    ))
    styles.add(ParagraphStyle(
        name="QLabel", fontName="Helvetica-Bold", fontSize=8,
        leading=10, textColor=ACCENT, spaceBefore=2, spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="AText", fontName="Helvetica", fontSize=8,
        leading=10.5, textColor=SLATE, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="SmallCenter", fontName="Helvetica", fontSize=7,
        leading=8.5, textColor=MUTED, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="TableCell", fontName="Helvetica", fontSize=7,
        leading=9, textColor=SLATE,
    ))
    styles.add(ParagraphStyle(
        name="TableHeader", fontName="Helvetica-Bold", fontSize=7,
        leading=9, textColor=WHITE,
    ))
    styles.add(ParagraphStyle(
        name="Chip", fontName="Helvetica", fontSize=6.5,
        leading=8, textColor=TEAL_DARK, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="Note", fontName="Helvetica-Oblique", fontSize=7.5,
        leading=9.5, textColor=MUTED, spaceAfter=2,
    ))
    return styles


def bullet_table(items, styles, cols=2, width=PAGE_W - 2 * MARGIN):
    cells = [Paragraph(f"•  {item}", styles["BulletText"]) for item in items]
    while len(cells) % cols:
        cells.append(Paragraph("", styles["BulletText"]))
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    col_w = width / cols
    t = Table(rows, colWidths=[col_w] * cols)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 0.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5),
    ]))
    return t


def chip_row(items, styles, width):
    paras = [Paragraph(i, styles["Chip"]) for i in items]
    n = len(items)
    # split into 2 rows if many
    if n > 5:
        mid = (n + 1) // 2
        rows_items = [items[:mid], items[mid:]]
        tables = []
        for row in rows_items:
            ps = [Paragraph(i, styles["Chip"]) for i in row]
            cw = width / len(row)
            t = Table([ps], colWidths=[cw] * len(row))
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), TEAL_LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.5, TEAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, CARD_BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]))
            tables.append(t)
        outer = Table([[t] for t in tables], colWidths=[width])
        outer.setStyle(TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        return outer
    col_w = width / n
    t = Table([paras], colWidths=[col_w] * n)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TEAL_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, TEAL),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, CARD_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def module_block(num, title, items, styles, width, note=None):
    parts = [SectionHeader(num, title, width), Spacer(1, 2),
             bullet_table(items, styles, cols=2 if len(items) > 3 else 1, width=width)]
    if note:
        parts.append(Paragraph(note, styles["Note"]))
    parts.append(Spacer(1, 3))
    return KeepTogether(parts)


def add_page_decorations(canv, doc):
    canv.saveState()
    canv.setFillColor(TEAL)
    canv.rect(0, PAGE_H - 5, PAGE_W, 5, fill=1, stroke=0)
    canv.setFillColor(TEAL_DARK)
    canv.rect(0, 0, PAGE_W, 12, fill=1, stroke=0)
    canv.setFillColor(WHITE)
    canv.setFont("Helvetica", 6.5)
    canv.drawString(MARGIN, 3.5, "Cloudspital — Health Kiosk Management Platform")
    canv.drawRightString(PAGE_W - MARGIN, 3.5, f"Page {doc.page}")
    canv.restoreState()


def build_pdf(path):
    styles = build_styles()
    content_w = PAGE_W - 2 * MARGIN

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=11 * mm, bottomMargin=10 * mm,
        title="Cloudspital Health Kiosk Management Platform",
        author="Junior Software Developer Intern — Interview Notes",
    )

    story = []

    # Title
    story.append(Paragraph("Cloudspital Health Kiosk Management Platform", styles["DocTitle"]))
    story.append(Paragraph(
        "Interview Project Notes  ·  Junior Software Developer Intern",
        styles["DocSubtitle"],
    ))
    story.append(HRFlowable(width="100%", thickness=1.1, color=TEAL, spaceBefore=1, spaceAfter=4))

    # Overview
    story.append(Paragraph("Project Overview", styles["H2"]))
    story.append(Paragraph(
        "A web-based SaaS dashboard used by hospitals and administrators to monitor "
        "Cloudspital’s deployed health kiosks across different locations. The dashboard "
        "aligns with Cloudspital’s Health Kiosk and telemedicine offerings.",
        styles["Body"],
    ))
    story.append(Paragraph("The dashboard allows hospitals to:", styles["BodyTight"]))
    story.append(bullet_table([
        "Register health kiosks", "Monitor kiosk status",
        "View patient screening reports", "Schedule telemedicine consultations",
        "Manage doctors", "Track device health",
        "View analytics", "Manage hospital users",
    ], styles, cols=2, width=content_w))
    story.append(Spacer(1, 3))

    # Architecture
    story.append(Paragraph("Simple Architecture", styles["H2"]))
    story.append(Paragraph(
        "Data flows from the patient at the kiosk through the cloud stack to hospital staff:",
        styles["BodyTight"],
    ))
    story.append(Spacer(1, 2))
    story.append(ArchitectureDiagram(content_w))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Patient → Health Kiosk → Cloud API → Cloudspital Backend → MySQL → Admin Dashboard → Hospital Admin / Doctor",
        styles["SmallCenter"],
    ))
    story.append(Spacer(1, 3))

    # Modules
    story.append(Paragraph("Modules", styles["H2"]))
    story.append(module_block(1, "Authentication", [
        "Admin Login", "Doctor Login", "Hospital Login",
        "JWT Authentication", "Role Based Access",
    ], styles, content_w))
    story.append(module_block(2, "Health Kiosk Dashboard", [
        "Online kiosks", "Offline kiosks", "Battery status",
        "Internet connectivity", "Last sync", "Location",
    ], styles, content_w))
    story.append(module_block(3, "Patient Reports", [
        "Health screening history", "BMI", "Blood Pressure",
        "Temperature", "Pulse", "SpO2",
        "Blood Sugar (where available)", "Download PDF",
    ], styles, content_w,
        note="These are consistent with the company’s health screening capabilities."))
    story.append(module_block(4, "Telemedicine", [
        "Patient books consultation", "Doctor receives notification",
        "Doctor opens report", "Starts video consultation",
        "Prescription generated",
    ], styles, content_w,
        note="Cloudspital highlights integrated telemedicine as one of its core solutions."))
    story.append(module_block(5, "Analytics Dashboard", [
        "Total Patients", "Daily Screenings", "High Risk Patients",
        "Most Common Diseases", "Kiosk Usage", "Monthly Reports",
    ], styles, content_w))

    # Role
    story.append(Paragraph("Your Role", styles["H2"]))
    story.append(Paragraph(
        "Instead of saying “I built the whole platform,” use a realistic intern framing:",
        styles["BodyTight"],
    ))
    story.append(ColoredBox(
        "“I worked on frontend features and API integration for the Health Kiosk Management "
        "Dashboard. My mentor assigned modules, and I implemented UI components, integrated "
        "REST APIs, fixed bugs, improved responsiveness, and participated in testing.”",
        content_w, styles,
    ))
    story.append(Spacer(1, 4))

    # Workflow
    story.append(Paragraph("Daily Workflow", styles["H2"]))
    story.append(WorkflowDiagram(content_w, [
        "Standup Meeting", "Receive Jira Task", "Understand Requirement",
        "Design Discussion", "Coding", "API Integration", "Testing",
        "Pull Request", "Code Review", "Merge", "QA Testing",
    ]))
    story.append(Spacer(1, 4))

    # Example Feature (kept together to avoid orphan heading)
    fields = [
        Paragraph("<b>Screen Fields</b>", styles["H3"]),
        Paragraph("•  Device ID", styles["BulletText"]),
        Paragraph("•  Location", styles["BulletText"]),
        Paragraph("•  Internet Status", styles["BulletText"]),
        Paragraph("•  Battery", styles["BulletText"]),
        Paragraph("•  Last Updated", styles["BulletText"]),
        Paragraph("•  Temperature", styles["BulletText"]),
        Paragraph("•  Firmware Version", styles["BulletText"]),
    ]
    left_inner = Table([[p] for p in fields], colWidths=[content_w * 0.36])
    left_inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, CARD_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    hdr = [
        Paragraph("<b>Hospital / Kiosk</b>", styles["TableHeader"]),
        Paragraph("<b>Status</b>", styles["TableHeader"]),
        Paragraph("<b>Battery / Sync</b>", styles["TableHeader"]),
    ]
    row1 = [
        Paragraph("Patna AIIMS", styles["TableCell"]),
        Paragraph("Online", styles["TableCell"]),
        Paragraph("98% · 2 minutes ago", styles["TableCell"]),
    ]
    row2 = [
        Paragraph("Railway Hospital", styles["TableCell"]),
        Paragraph("Offline", styles["TableCell"]),
        Paragraph("Last Sync 10 min ago", styles["TableCell"]),
    ]
    dash = Table(
        [hdr, row1, row2],
        colWidths=[content_w * 0.22, content_w * 0.14, content_w * 0.24],
    )
    dash.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("BACKGROUND", (0, 1), (-1, 1), ONLINE_BG),
        ("BACKGROUND", (0, 2), (-1, 2), OFFLINE_BG),
        ("BOX", (0, 0), (-1, -1), 0.55, TEAL),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, CARD_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    right_block = Table([
        [Paragraph("<b>Dashboard Shows</b>", styles["H3"])],
        [dash],
    ], colWidths=[content_w * 0.62])
    right_block.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    feat = Table([[left_inner, right_block]], colWidths=[content_w * 0.38, content_w * 0.62])
    feat.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    api_text = (
        '<font face="Courier" size="7" color="#084F4F">'
        "GET /api/kiosks<br/>"
        '[{"id":12, "name":"AIIMS Patna", "status":"Online", "battery":95}]'
        "</font>"
    )
    api_tbl = Table([[Paragraph(api_text, styles["BodyTight"])]], colWidths=[content_w])
    api_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, CARD_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    story.append(KeepTogether([
        Paragraph("Example Feature — Kiosk Status Screen", styles["H2"]),
        feat,
        Spacer(1, 3),
        Paragraph("Example API", styles["H3"]),
        api_tbl,
        Spacer(1, 3),
        Paragraph("Database Tables", styles["H3"]),
        chip_row([
            "Hospitals", "Doctors", "Patients", "Kiosks", "Appointments",
            "HealthReports", "Users", "Notifications", "AuditLogs",
        ], styles, content_w),
        Spacer(1, 4),
    ]))

    # Bug & Challenge together
    story.append(Paragraph("Real Bug Story", styles["H2"]))
    story.append(Paragraph("Q: Tell me about one bug.", styles["QLabel"]))
    story.append(ColoredBox(
        "“The dashboard wasn’t updating kiosk status correctly because the frontend cached older "
        "API responses. I fixed it by refreshing the data after every successful API request and "
        "displaying the last synchronization time so users knew how recent the information was.”",
        content_w, styles,
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Biggest Challenge", styles["H2"]))
    story.append(Paragraph("Q: Biggest challenge?", styles["QLabel"]))
    story.append(ColoredBox(
        "“One dashboard became slow because hundreds of kiosks were displayed at once. We "
        "introduced pagination and server-side filtering so users could search by hospital or "
        "location instead of loading everything at once.”",
        content_w, styles, bg=CHALLENGE_BG, accent=ACCENT,
    ))
    story.append(Spacer(1, 4))

    # Learned
    story.append(Paragraph("What You Learned", styles["H2"]))
    story.append(bullet_table([
        "REST API Integration", "Git Workflow",
        "Responsive Design", "Debugging",
        "Component Reusability", "Professional Development Workflow",
        "Code Reviews", "Healthcare Domain Knowledge",
    ], styles, cols=2, width=content_w))
    story.append(Spacer(1, 3))

    # Q&A
    story.append(Paragraph("If Interviewer Asks", styles["H2"]))
    story.append(Paragraph("What exactly is Cloudspital?", styles["QLabel"]))
    story.append(Paragraph(
        "“Cloudspital is a MedTech company focused on digital healthcare automation. It develops "
        "health kiosks, telemedicine solutions, AI-assisted screening systems, and connected "
        "healthcare platforms that help hospitals and healthcare providers deliver services more efficiently.”",
        styles["AText"],
    ))
    story.append(Paragraph("What is the Health Kiosk?", styles["QLabel"]))
    story.append(Paragraph(
        "“It’s a point-of-care device that performs health screening, supports telemedicine, and "
        "uploads patient data to a cloud platform where doctors can review reports and conduct "
        "remote consultations.”",
        styles["AText"],
    ))
    story.append(Paragraph("Why is it SaaS?", styles["QLabel"]))
    story.append(Paragraph(
        "“Because hospitals access the platform through a web application without installing "
        "software locally. Cloudspital manages the application centrally, and multiple "
        "organizations can use the same platform with isolated data.”",
        styles["AText"],
    ))
    story.append(Spacer(1, 2))

    story.append(Paragraph("Technology Choices", styles["H3"]))
    tech_data = [
        [
            Paragraph("<b>Why React?</b>", styles["TableHeader"]),
            Paragraph("<b>Why Node.js?</b>", styles["TableHeader"]),
            Paragraph("<b>Why MySQL?</b>", styles["TableHeader"]),
        ],
        [
            Paragraph(
                "• Reusable Components<br/>• Fast UI<br/>• Easy API Integration<br/>• Good State Management",
                styles["TableCell"],
            ),
            Paragraph(
                "• Asynchronous APIs<br/>• Fast Development<br/>• JavaScript across frontend and backend<br/>• Easy REST API Development",
                styles["TableCell"],
            ),
            Paragraph(
                "• Structured healthcare data<br/>• Relationships between hospitals, patients, doctors, appointments, and reports<br/>• Reliable transactions",
                styles["TableCell"],
            ),
        ],
    ]
    tech = Table(tech_data, colWidths=[content_w / 3] * 3)
    tech.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("BACKGROUND", (0, 1), (-1, 1), TEAL_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.55, TEAL),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, CARD_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tech)

    doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
    print(f"Wrote {path}")


if __name__ == "__main__":
    import shutil
    out = "/opt/cursor/artifacts/Cloudspital_Health_Kiosk_Management_Platform.pdf"
    build_pdf(out)
    shutil.copy(out, "/workspace/cloudspital-pdf/Cloudspital_Health_Kiosk_Management_Platform.pdf")
    print("Done.")
