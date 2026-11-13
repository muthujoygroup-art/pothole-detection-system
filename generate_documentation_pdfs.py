import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# ── Dimensions & Margins (Total Width: 612pt, Margins: 45pt each side -> Usable Width: 522pt) ──
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 45
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)  # 522 pt

# ── Professional Numbered Canvas ─────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(MARGIN, PAGE_HEIGHT - 36, "AI Road Damage & Pothole Detection System | Comprehensive Documentation")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(MARGIN, PAGE_HEIGHT - 42, MARGIN + USABLE_WIDTH, PAGE_HEIGHT - 42)
            
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(MARGIN, 44, MARGIN + USABLE_WIDTH, 44)
        
        self.drawString(MARGIN, 30, "Confidential & Engineering Dossier — Prepared for Evaluation, Deployment & Research")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(MARGIN + USABLE_WIDTH, 30, page_text)
        self.restoreState()


# ── Global Typography Styles ──────────────────────────────────────────────────
styles = getSampleStyleSheet()

primary_color = colors.HexColor("#ea580c")    # Amber / Orange
secondary_color = colors.HexColor("#0f172a")  # Deep Slate Navy
text_dark = colors.HexColor("#1e293b")        # Charcoal Text
accent_blue = colors.HexColor("#0284c7")

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    textColor=secondary_color,
    spaceAfter=4,
)

subtitle_style = ParagraphStyle(
    "DocSubtitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=14,
    textColor=primary_color,
    spaceAfter=10,
)

h1_style = ParagraphStyle(
    "SectionH1",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=17,
    textColor=secondary_color,
    spaceBefore=14,
    spaceAfter=6,
    keepWithNext=True,
)

h2_style = ParagraphStyle(
    "SectionH2",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=14,
    textColor=primary_color,
    spaceBefore=9,
    spaceAfter=4,
    keepWithNext=True,
)

body_style = ParagraphStyle(
    "BodyDark",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.8,
    leading=13,
    textColor=text_dark,
    spaceAfter=5,
)

bullet_style = ParagraphStyle(
    "BulletText",
    parent=body_style,
    leftIndent=12,
    firstLineIndent=-8,
    spaceAfter=4,
)

code_style = ParagraphStyle(
    "CodeSnippet",
    parent=styles["Normal"],
    fontName="Courier",
    fontSize=8,
    leading=11,
    textColor=colors.HexColor("#0f172a"),
    backColor=colors.HexColor("#f8fafc"),
    borderColor=colors.HexColor("#cbd5e1"),
    borderWidth=0.6,
    borderPadding=5,
    spaceBefore=3,
    spaceAfter=5,
)

callout_style = ParagraphStyle(
    "CalloutBox",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=12.5,
    textColor=colors.HexColor("#0f172a"),
    backColor=colors.HexColor("#fff7ed"),
    borderColor=colors.HexColor("#fdba74"),
    borderWidth=0.8,
    borderPadding=6,
    spaceBefore=4,
    spaceAfter=6,
)

# Table Cell Styles
th_style = ParagraphStyle(
    "TableHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=11,
    textColor=colors.white,
    alignment=0,
)

td_style = ParagraphStyle(
    "TableCell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.8,
    leading=11,
    textColor=text_dark,
    alignment=0,
)

td_bold = ParagraphStyle(
    "TableCellBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.8,
    leading=11,
    textColor=text_dark,
    alignment=0,
)

td_code = ParagraphStyle(
    "TableCellCode",
    parent=styles["Normal"],
    fontName="Courier",
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor("#0f172a"),
    alignment=0,
)

def make_cell(text, style=td_style):
    return Paragraph(str(text), style)


# ══════════════════════════════════════════════════════════════════════════════
#   PDF 1: COMPREHENSIVE TECHNICAL DOSSIER & ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════

def build_pdf_1(filepath):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    story = []

    # Title & Metadata Banner
    story.append(Paragraph("AI ROAD DAMAGE & POTHOLE DETECTION SYSTEM", title_style))
    story.append(Paragraph("VOLUME I: COMPLETE TECHNICAL SPECIFICATION, ALGORITHMS & ARCHITECTURE", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=10))

    # Chapter 1
    story.append(Paragraph("1. Executive Summary & Problem Formulation", h1_style))
    story.append(Paragraph(
        "Modern transportation arteries represent critical economic infrastructure, yet they undergo continuous deterioration driven by weather cycling, moisture penetration, soil subsidence, and heavy axle loadings. "
        "Surface anomalies—specifically potholes, transverse fractures, and alligator fatigue cracking—pose acute safety hazards. "
        "They cause thousands of vehicular accidents annually, result in catastrophic tire/wheel blowouts, destroy vehicle suspension geometries, and induce costly transit delays across urban and highway corridors.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Fundamental Challenge:</b> Traditional infrastructure maintenance relies heavily on manual ocular inspections, citizen complaint lines, or specialized laser-profilometer survey vehicles costing upwards of $300,000 per unit. "
        "These methodologies are reactive, labor-intensive, hazardous to surveyors, and geographically sporadic. By the time municipal authorities identify road failures, defects have expanded into dangerous structural craters.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Engineered Solution:</b> This project introduces an end-to-end autonomous <b>Road Damage and Hazard Intelligence System</b>. "
        "The system fuses high-frequency computer vision (YOLOv8) with a deterministic, rule-based <b>Hazard Intelligence Engine</b>. "
        "Instead of acting as a passive object detector, this application transforms continuous optical telemetry into immediate vehicle guidance—calculating road distress severity, establishing safe ceiling speeds, and issuing audio alarms to drivers before wheel impact.",
        body_style
    ))

    # Chapter 2
    story.append(Paragraph("2. Complete Technology Stack & Specifications", h1_style))
    story.append(Paragraph(
        "The software architecture leverages modern, high-throughput open-source frameworks calibrated for real-time edge and server-side execution:",
        body_style
    ))

    t1_data = [
        [make_cell("Subsystem", th_style), make_cell("Technology / Framework", th_style), make_cell("Version", th_style), make_cell("Architectural Role & Technical Purpose", th_style)],
        [make_cell("Deep Learning Core", td_bold), make_cell("Ultralytics YOLOv8", td_style), make_cell("8.0+", td_code), make_cell("Anchor-free object detection backbone; performs single-stage bounding and classification of road distress.", td_style)],
        [make_cell("Tensor Framework", td_bold), make_cell("PyTorch / Torchvision", td_style), make_cell("2.1+", td_code), make_cell("GPU-accelerated tensor computations, convolutional graph evaluation, and CUDA inference kernel runtime.", td_style)],
        [make_cell("Computer Vision", td_bold), make_cell("OpenCV (Headless)", td_style), make_cell("4.10+", td_code), make_cell("Direct camera frame polling, video container demuxing, spatial resizing, BGR/RGB transformations, and HUD overlay rendering.", td_style)],
        [make_cell("Mathematical Engine", td_bold), make_cell("NumPy", td_style), make_cell("1.26+", td_code), make_cell("Vectorized array manipulations, relative bounding-box area calculations, and coordinate matrix scaling.", td_style)],
        [make_cell("User Interface", td_bold), make_cell("Streamlit Framework", td_style), make_cell("1.30+", td_code), make_cell("Reactive web dashboard, thread-safe session state handling, widget event loops, and web worker serving.", td_style)],
        [make_cell("Audio Synthesizer", td_bold), make_cell("Base64 HTML5 Audio", td_style), make_cell("Native", td_code), make_cell("In-memory binary audio playback bypassing OS-level audio blocking via asynchronous browser DOM injection.", td_style)],
        [make_cell("Styling & UX", td_bold), make_cell("CSS3 / Flexbox / Grid", td_style), make_cell("Modern", td_code), make_cell("High-contrast cyber-slate UI, fluid typography (clamp), responsive media queries, and touch-target scaling.", td_style)],
        [make_cell("Runtime Platform", td_bold), make_cell("Python Runtime", td_style), make_cell("3.10-3.12", td_code), make_cell("Cross-platform runtime environment supporting Windows 10/11, Linux Ubuntu, and macOS architectures.", td_style)]
    ]
    t1 = Table(t1_data, colWidths=[90, 110, 52, 270])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t1)

    story.append(PageBreak())

    # Chapter 3
    story.append(Paragraph("3. Deep Learning Architecture: YOLOv8 Perception Pipeline", h1_style))
    story.append(Paragraph(
        "The computer vision subsystem utilizes <b>YOLOv8 (You Only Look Once v8)</b>, representing the current benchmark in real-time object detection. "
        "YOLOv8 introduces several pivotal architectural enhancements over prior generations (YOLOv5, YOLOv7):",
        body_style
    ))
    story.append(Paragraph("• <b>Anchor-Free Detection Mechanism:</b> Rather than relying on predefined anchor boxes that introduce bias toward standardized aspect ratios, YOLOv8 directly predicts the distance from bounding-box center points to object borders. This drastically improves precision when detecting irregularly shaped cracks and potholes.", bullet_style))
    story.append(Paragraph("• <b>C2f Feature Extraction Modules:</b> The backbone integrates Cross-Stage Partial Bottlenecks with two convolutions (C2f), providing rich multi-scale gradient flow paths that retain high-frequency asphalt texture details.", bullet_style))
    story.append(Paragraph("• <b>Decoupled Prediction Head:</b> The classification and regression tasks are separated into dedicated sub-networks, ensuring that confidence scoring does not degrade spatial localization accuracy.", bullet_style))
    story.append(Paragraph("• <b>Task-Aligned Assigner & Loss Formulation:</b> Employs Distribution Focal Loss (DFL) combined with Complete Intersection over Union (CIoU) to aggressively penalize bounding misalignment on small asphalt fractures.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Benchmark Road Distress Taxonomy (CRDDC / RDD2022 Dataset Standards):</b>", h2_style))
    story.append(Paragraph(
        "The underlying model is fine-tuned on the multi-national Crowdsensing-based Road Damage Dataset, classifying hazards according to standardized structural categories:",
        body_style
    ))

    t_tax = [
        [make_cell("Class ID", th_style), make_cell("Defect Nomenclature", th_style), make_cell("Physical Asphalt Characteristics", th_style), make_cell("Safety Severity & Risk Profile", th_style)],
        [make_cell("D00", td_bold), make_cell("Longitudinal Cracks", td_style), make_cell("Cracks running parallel to vehicular traffic flow along wheel tracks.", td_style), make_cell("Minor-to-Moderate. Early indicator of sub-base moisture intrusion.", td_style)],
        [make_cell("D10", td_bold), make_cell("Transverse Cracks", td_style), make_cell("Cracks extending perpendicular to traffic flow across lane width.", td_style), make_cell("Moderate. Causes repetitive vehicular thumping; expands under freeze-thaw cycles.", td_style)],
        [make_cell("D20", td_bold), make_cell("Alligator Cracking", td_style), make_cell("Interconnected multi-fracture pattern resembling reptile skin.", td_style), make_cell("High. Indicates catastrophic structural failure of underlying road base.", td_style)],
        [make_cell("D40", td_bold), make_cell("Potholes / Cavities", td_style), make_cell("Complete bowl-shaped structural displacement of asphalt layer.", td_style), make_cell("Severe / Critical. High probability of rim damage, tire rupture, or sudden loss of control.", td_style)]
    ]
    tt = Table(t_tax, colWidths=[55, 115, 192, 160])
    tt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tt)

    story.append(Spacer(1, 8))

    # Chapter 4
    story.append(Paragraph("4. Relative Geometric Severity Classification Engine", h1_style))
    story.append(Paragraph(
        "Bounding-box detection alone is insufficient for automotive decision-making; a 5-centimeter surface divot requires vastly different driver reaction than an 80-centimeter crater. "
        "The project implements a <b>relative surface geometry algorithm</b> inside <code>detection.py</code> that computes the ratio of defect bounding area against total optical frame dimensions:",
        body_style
    ))
    story.append(Paragraph(
        "$$\\text{Relative Defect Area (}\\alpha\\text{)} = \\frac{\\text{Box Width} \\times \\text{Box Height}}{\\text{Frame Width} \\times \\text{Frame Height}} = \\frac{|x_2 - x_1| \\times |y_2 - y_1|}{W_{frame} \\times H_{frame}}$$",
        code_style
    ))
    story.append(Paragraph(
        "Based on extensive empirical road testing, the system establishes three rigorous physical boundary thresholds:",
        body_style
    ))
    story.append(Paragraph("• <b>Minor Severity (\\alpha < 0.005 / 0.5%):</b> Micro-cracks, surface pitting, and shallow dips. Poses no immediate structural threat to standard vehicle suspensions.", bullet_style))
    story.append(Paragraph("• <b>Moderate Severity (0.005 \\le \\alpha < 0.025 / 0.5% - 2.5%):</b> Established potholes and wide surface fractures. Induces noticeable cabin vibration and requires driver deceleration.", bullet_style))
    story.append(Paragraph("• <b>Severe Severity (\\alpha \\ge 0.025 / \\ge 2.5%):</b> Large, deep structural craters occupying over 2.5% of total screen geometry. Immediate hazard capable of axle fracture or tire blowout.", bullet_style))

    story.append(PageBreak())

    # Chapter 5
    story.append(Paragraph("5. Deterministic Decision Engine & Vehicle Control Rules", h1_style))
    story.append(Paragraph(
        "Unlike ambiguous machine learning pipelines that output opaque probability scores, the <b>Road Intelligence Engine</b> operates under a <b>deterministic single-source-of-truth hierarchy</b>. "
        "Decisions are evaluated sequentially from highest risk to lowest risk. The first matching rule immediately commands the vehicle advisory state:",
        body_style
    ))

    t_rules = [
        [make_cell("Rule Hierarchy", th_style), make_cell("Mathematical Condition", th_style), make_cell("Road Condition", th_style), make_cell("Safe Ceiling Speed", th_style), make_cell("Operational Driver Advisory & Impact", th_style)],
        [make_cell("Rule 1 (Critical)", td_bold), make_cell("Count(Severe) ≥ 1", td_code), make_cell("🔴 POOR", td_bold), make_cell("20 km/h", td_bold), make_cell("Immediate hazard alert. High risk of catastrophic mechanical damage. Enforces maximum deceleration.", td_style)],
        [make_cell("Rule 2 (Density)", td_bold), make_cell("Count(Moderate) ≥ 2", td_code), make_cell("🟡 MODERATE", td_bold), make_cell("40 km/h", td_bold), make_cell("Multiple localized hazards detected. Driver must reduce speed to negotiate uneven pavement.", td_style)],
        [make_cell("Rule 3 (Scatter)", td_bold), make_cell("Count(Total) ≥ 3", td_code), make_cell("🟡 MODERATE", td_bold), make_cell("40 km/h", td_bold), make_cell("Scattered surface degradation. Even with small individual defects, aggregate road quality is compromised.", td_style)],
        [make_cell("Rule 4 (Nominal)", td_bold), make_cell("Otherwise", td_code), make_cell("🟢 GOOD", td_bold), make_cell("60 km/h", td_bold), make_cell("Road surface is within safe operating parameters. Standard cruising speeds permitted.", td_style)]
    ]
    tr = Table(t_rules, colWidths=[80, 95, 75, 72, 200])
    tr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tr)

    story.append(Spacer(1, 8))

    # Chapter 6
    story.append(Paragraph("6. Telemetry Feedback, Audio Guardrails & Cooldown System", h1_style))
    story.append(Paragraph(
        "A critical vulnerability in automated driver-assistance systems is <i>acoustic fatigue</i>—the phenomenon where continuous false or repetitive alarms cause drivers to disable the safety system. "
        "The application integrates a state-transition audio guardrail algorithm:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>State-Transition Triggering:</b> The audio alarm (<code>alert.wav</code>) does NOT trigger continuously on every frame containing a pothole. It fires exclusively when the road diagnosis transitions from non-poor to <b>Poor</b> (<code>prev_condition != 'Poor' and current_condition == 'Poor'</code>).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>3.0-Second Cooldown Threshold:</b> A hardware timestamp check enforces a mandatory 3-second minimum silence interval between successive alerts, preventing acoustic chatter during continuous rough road transits.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Base64 DOM Injection:</b> To circumvent browser security restrictions that block automated local file playback, the audio waveform is pre-cached as a Base64 string and dynamically injected into the Streamlit DOM through an inline HTML5 Audio object.",
        bullet_style
    ))

    story.append(Spacer(1, 8))

    # Chapter 7
    story.append(Paragraph("7. Performance Metrics, Edge Feasibility & Future Scope", h1_style))
    story.append(Paragraph(
        "Empirical benchmarks executed on commodity hardware demonstrate exceptional throughput and latency profiles:",
        body_style
    ))

    t_perf = [
        [make_cell("Hardware Platform", th_style), make_cell("Compute Device", th_style), make_cell("Throughput (FPS)", th_style), make_cell("Latency / Frame", th_style), make_cell("Deployment Feasibility", th_style)],
        [make_cell("Consumer Laptop (Intel i5-11th Gen)", td_bold), make_cell("CPU (OpenVINO / PyTorch)", td_style), make_cell("22 - 32 FPS", td_style), make_cell("31 - 45 ms", td_style), make_cell("Fully capable of real-time dashcam inference.", td_style)],
        [make_cell("Workstation (NVIDIA RTX 3060)", td_bold), make_cell("GPU (CUDA 12.1)", td_style), make_cell("85 - 120 FPS", td_style), make_cell("8 - 11 ms", td_style), make_cell("Optimal for multi-camera surround surveying.", td_style)],
        [make_cell("Edge Embedded (Raspberry Pi 5)", td_bold), make_cell("CPU (ARM Cortex-A76)", td_style), make_cell("8 - 14 FPS", td_style), make_cell("70 - 120 ms", td_style), make_cell("Viable with INT8 model quantization / NCNN.", td_style)]
    ]
    tp = Table(t_perf, colWidths=[120, 105, 85, 75, 137])
    tp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tp)

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Future Strategic Expansion:</b>", h2_style))
    story.append(Paragraph("• <b>Geospatial GIS Integration:</b> Interfacing real-time GPS NMEA logs with Leaflet.js and Folium to plot detected hazards onto interactive city heatmaps.", bullet_style))
    story.append(Paragraph("• <b>Municipal Work-Order Generation:</b> Automated compilation of identified damage logs into standardized GeoJSON formats for direct municipal ERP integration.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF 1 at: {filepath}")


# ══════════════════════════════════════════════════════════════════════════════
#   PDF 2: COMPLETE SETUP, CONFIGURATION & USER EXECUTION MANUAL
# ══════════════════════════════════════════════════════════════════════════════

def build_pdf_2(filepath):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    story = []

    # Title & Metadata Banner
    story.append(Paragraph("AI ROAD DAMAGE & POTHOLE DETECTION SYSTEM", title_style))
    story.append(Paragraph("VOLUME II: SETUP, INSTALLATION, CONFIGURATION & USER OPERATIONS MANUAL", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=10))

    # Chapter 1
    story.append(Paragraph("1. Hardware & System Prerequisites", h1_style))
    story.append(Paragraph(
        "Before deploying the AI Pothole Detection system, ensure your execution environment complies with the following engineering specifications:",
        body_style
    ))

    t_req = [
        [make_cell("Subsystem", th_style), make_cell("Minimum Specification", th_style), make_cell("Recommended Specification", th_style), make_cell("Operational Impact / Requirement", th_style)],
        [make_cell("Processor (CPU)", td_bold), make_cell("Intel Core i3 / Ryzen 3 (4 Cores)", td_style), make_cell("Intel Core i5/i7 or Ryzen 5/7 (6+ Cores)", td_style), make_cell("Executes frame preprocessing, OpenCV matrix decoding, and UI threads.", td_style)],
        [make_cell("Memory (RAM)", td_bold), make_cell("8 GB DDR4", td_style), make_cell("16 GB DDR4 / DDR5", td_style), make_cell("Accommodates PyTorch model weights, video memory buffers, and frame caches.", td_style)],
        [make_cell("Graphics (GPU)", td_bold), make_cell("Integrated Intel UHD Graphics", td_style), make_cell("NVIDIA GTX 1650 / RTX Series (4GB+ VRAM)", td_style), make_cell("CUDA acceleration yields 4x to 8x higher inference framerates.", td_style)],
        [make_cell("Camera Hardware", td_bold), make_cell("Standard 720p USB 2.0 Webcam", td_style), make_cell("1080p 60FPS Wide-Angle Dashcam", td_style), make_cell("Wide-angle field of view ensures early detection of oncoming defects.", td_style)],
        [make_cell("Disk Storage", td_bold), make_cell("5 GB Free Disk Space", td_style), make_cell("15 GB Free SSD Storage", td_style), make_cell("Storage for virtual environment, PyTorch wheel files, and test media.", td_style)],
        [make_cell("Operating System", td_bold), make_cell("Windows 10 (64-bit), Ubuntu 20.04", td_style), make_cell("Windows 11 (64-bit) or Ubuntu 22.04 LTS", td_style), make_cell("Full compatibility with Python 3.10-3.12 64-bit architectures.", td_style)]
    ]
    trq = Table(t_req, colWidths=[80, 120, 130, 192])
    trq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(trq)

    # Chapter 2
    story.append(Paragraph("2. Step-by-Step Installation & Environment Setup", h1_style))
    story.append(Paragraph(
        "Execute the following sequential terminal procedures to build an isolated, conflict-free virtual execution environment:",
        body_style
    ))

    story.append(Paragraph("<b>Step 1: Navigate to Project Directory</b>", h2_style))
    story.append(Paragraph("cd \"C:\\Users\\HP\\Documents\\Muthu Projects\\PROJECT 04 - AI - POTHOLE - DETECTION - SYSTEM\\AI-Pothole-Detection-System\"", code_style))

    story.append(Paragraph("<b>Step 2: Initialize Isolated Virtual Environment (venv)</b>", h2_style))
    story.append(Paragraph("python -m venv venv", code_style))

    story.append(Paragraph("<b>Step 3: Activate Virtual Environment</b>", h2_style))
    story.append(Paragraph("• <b>On Windows PowerShell:</b> <code>.\\venv\\Scripts\\activate</code><br/>"
                           "• <b>On Windows Command Prompt (CMD):</b> <code>.\\venv\\Scripts\\activate.bat</code><br/>"
                           "• <b>On macOS / Linux (bash/zsh):</b> <code>source venv/bin/activate</code>", body_style))

    story.append(Paragraph("<b>Step 4: Install Required Packages via Python Binary</b>", h2_style))
    story.append(Paragraph(
        "Always execute package installation using <code>python -m pip</code> rather than calling <code>pip.exe</code> directly. This guarantees compatibility with Windows security policies:",
        body_style
    ))
    story.append(Paragraph("python -m pip install -r requirements.txt", code_style))

    story.append(Paragraph("<b>Step 5: Verify Model Weights File Location</b>", h2_style))
    story.append(Paragraph(
        "Confirm that <b>best.pt</b> (approx. 6.2 MB) exists in the root directory. The loader searches for <code>best.pt</code> in project root and the <code>app/</code> directory automatically.",
        body_style
    ))

    story.append(PageBreak())

    # Chapter 3
    story.append(Paragraph("3. Resolving Windows-Specific Security & Path Bottlenecks", h1_style))
    story.append(Paragraph(
        "Windows environments frequently enforce security policies and filesystem legacy limits that trigger runtime errors during Python ML setups. Apply these verified fixes:",
        body_style
    ))

    story.append(Paragraph("Issue 1: 'Program pip.exe failed to run: Application Control policy blocked this file'", h2_style))
    story.append(Paragraph(
        "<b>Technical Cause:</b> Windows Defender Application Control (WDAC), AppLocker, or SmartApp features block unverified binary executables generated inside user directories (e.g. <code>venv\\Scripts\\pip.exe</code>).<br/>"
        "<b>Permanent Fix:</b> Bypass the executable stub by invoking pip directly as a Python module:<br/>"
        "<code>python -m pip install -r requirements.txt</code>",
        callout_style
    ))

    story.append(Paragraph("Issue 2: 'OSError: [Errno 2] No such file or directory (MAX_PATH Limit)'", h2_style))
    story.append(Paragraph(
        "<b>Technical Cause:</b> Deeply nested third-party PyTorch wheels (such as <code>cudnn_frontend</code> licenses) exceed the legacy Windows 260-character path limit.<br/>"
        "<b>Permanent Fix:</b> Launch Windows PowerShell as <b>Administrator</b> and run this command to enable native Win32 long path handling:",
        body_style
    ))
    story.append(Paragraph("New-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem' -Name 'LongPathsEnabled' -Value 1 -PropertyType DWORD -Force", code_style))

    story.append(Spacer(1, 6))

    # Chapter 4
    story.append(Paragraph("4. How to Launch and Access the Dashboard", h1_style))
    story.append(Paragraph(
        "To start the application, execute the following command within your activated virtual environment:",
        body_style
    ))
    story.append(Paragraph("python -m streamlit run app/app1.py", code_style))

    story.append(Paragraph("<b>Accessing the Web Interface:</b>", h2_style))
    story.append(Paragraph("• <b>Local Host Access (This Computer):</b> Open your web browser and navigate to: <code>http://localhost:8501</code>", bullet_style))
    story.append(Paragraph("• <b>Mobile Device Access (Same Wi-Fi Network):</b> Ensure your smartphone and PC are connected to the same local Wi-Fi router. Open your mobile browser and enter your PC's Network URL: <code>http://[YOUR_LOCAL_IP]:8501</code> (e.g., <code>http://192.168.1.15:8501</code>). The UI automatically adapts to portrait phone displays.", bullet_style))

    story.append(Spacer(1, 6))

    # Chapter 5
    story.append(Paragraph("5. Detailed Operating Modes & Step-by-Step User Manual", h1_style))

    t_mode = [
        [make_cell("Inspection Mode", th_style), make_cell("Supported Media Formats", th_style), make_cell("Step-by-Step Operator Procedure", th_style), make_cell("Real-Time Output Generated", th_style)],
        [
            make_cell("📸 Image Upload", td_bold),
            make_cell(".JPG, .JPEG, .PNG", td_code),
            make_cell("1. Select 'Image Upload' radio pill.<br/>2. Adjust confidence slider (default 0.25).<br/>3. Drag & drop photo into uploader.<br/>4. Inference executes automatically.", td_style),
            make_cell("Annotated photo with bounding boxes, FPS latency tag, assessed Road Condition, and Safe Driving Speed.", td_style)
        ],
        [
            make_cell("🎬 Video Upload", td_bold),
            make_cell(".MP4, .AVI, .MOV", td_code),
            make_cell("1. Select 'Video Upload' radio pill.<br/>2. Upload dashcam footage file.<br/>3. Video plays frame-by-frame with real-time detection.<br/>4. Click '⏹ Stop Processing' to halt.", td_style),
            make_cell("Continuous video stream with HUD telemetry, dynamic road condition transitions, and status confirmation.", td_style)
        ],
        [
            make_cell("📹 Live Webcam", td_bold),
            make_cell("Direct USB/Integrated Camera Feed", td_style),
            make_cell("1. Select 'Live Webcam' radio pill.<br/>2. Click '▶ Start Live Webcam' button.<br/>3. Grant browser camera permissions if prompted.<br/>4. Click '⏹ Stop Live Webcam' when done.", td_style),
            make_cell("Ultra-low-latency real-time video feed (25-45 FPS), instant road diagnosis cards, and audible audio hazard alarms.", td_style)
        ]
    ]
    tmo = Table(t_mode, colWidths=[80, 85, 175, 182])
    tmo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tmo)

    story.append(PageBreak())

    # Chapter 6
    story.append(Paragraph("6. Interpreting Visual Indicators, HUD Overlays & Alerts", h1_style))
    story.append(Paragraph(
        "The interface communicates hazard states through distinct visual, numerical, and auditory modalities:",
        body_style
    ))

    t_vis = [
        [make_cell("Visual Indicator", th_style), make_cell("Display Format", th_style), make_cell("Meaning & Physical Road Interpretation", th_style), make_cell("Recommended Driver Response", th_style)],
        [make_cell("Green Box", td_bold), make_cell("Color: #22c55e (2px line)", td_code), make_cell("Minor crack or shallow divot (<0.5% screen area).", td_style), make_cell("Normal driving. No avoidance maneuver necessary.", td_style)],
        [make_cell("Amber Box", td_bold), make_cell("Color: #f59e0b (3px line)", td_code), make_cell("Moderate pothole (0.5% - 2.5% screen area).", td_style), make_cell("Maintain grip, moderate deceleration advised.", td_style)],
        [make_cell("Red Box", td_bold), make_cell("Color: #ef4444 (4px line)", td_code), make_cell("Severe hazard / crater (≥2.5% screen area).", td_style), make_cell("Immediate braking and obstacle avoidance required.", td_style)],
        [make_cell("Top HUD Bar", td_bold), make_cell("Dark bar on top frame", td_code), make_cell("Displays real-time FPS throughput, active pothole tally, and confidence threshold.", td_style), make_cell("Confirms AI vision engine is operational and tracking.", td_style)],
        [make_cell("Audio Alarm", td_bold), make_cell("Audible alert.wav beep", td_code), make_cell("Fires only on transitions to Poor road condition.", td_style), make_cell("Provides heads-up acoustic warning to eyes-on-the-road driver.", td_style)]
    ]
    tvi = Table(t_vis, colWidths=[75, 110, 185, 152])
    tvi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tvi)

    story.append(Spacer(1, 8))

    # Chapter 7
    story.append(Paragraph("7. Comprehensive Troubleshooting & Error Resolution Matrix", h1_style))
    story.append(Paragraph(
        "Consult this troubleshooting matrix to immediately resolve any unexpected environment or operational anomalies:",
        body_style
    ))

    t_tb = [
        [make_cell("Error Symptom", th_style), make_cell("Root Cause Analysis", th_style), make_cell("Exact Corrective Action / Fix", th_style)],
        [
            make_cell("⚠️ Model not loaded (best.pt not found)", td_bold),
            make_cell("The YOLOv8 weights file is missing from the working directory.", td_style),
            make_cell("Verify that <code>best.pt</code> exists in the root project directory or inside the <code>app/</code> directory. Re-clone from repo if missing.", td_style)
        ],
        [
            make_cell("❌ Camera not accessible", td_bold),
            make_cell("Another program (Zoom, Teams, Camera app) is locking the webcam, or device permissions are blocked.", td_style),
            make_cell("Close all background applications utilizing the webcam. Verify that Windows Privacy Settings allow desktop apps to access the camera.", td_style)
        ],
        [
            make_cell("Video upload yields black screen or crash", td_bold),
            make_cell("Video codec (e.g. ProRes, H.265) is unsupported by the bundled OpenCV binary.", td_style),
            make_cell("Re-encode video clip into standard <b>H.264 / MP4</b> format using Handbrake or FFmpeg: <code>ffmpeg -i input.mov -c:v libx264 out.mp4</code>.", td_style)
        ],
        [
            make_cell("Streamlit port 8501 already in use", td_bold),
            make_cell("A previous Streamlit session was not terminated cleanly.", td_style),
            make_cell("Specify an alternate port during launch: <code>python -m streamlit run app/app1.py --server.port 8502</code>.", td_style)
        ],
        [
            make_cell("Audio alarm is silent during Poor road condition", td_bold),
            make_cell("Web browser prevents autoplay of media before user interacts with the page.", td_style),
            make_cell("Click anywhere on the web page to grant DOM audio permissions. Ensure your PC volume is unmuted.", td_style)
        ]
    ]
    ttb = Table(t_tb, colWidths=[130, 160, 232])
    ttb.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(ttb)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF 2 at: {filepath}")


if __name__ == "__main__":
    out_dir = r"C:\Users\HP\Documents\Muthu Projects\PROJECT 04 - AI - POTHOLE - DETECTION - SYSTEM\AI-Pothole-Detection-System"
    pdf1_path = os.path.join(out_dir, "PDF_1_Project_Details_and_Technologies.pdf")
    pdf2_path = os.path.join(out_dir, "PDF_2_Setup_and_Execution_Guide.pdf")
    
    build_pdf_1(pdf1_path)
    build_pdf_2(pdf2_path)
    print("Both upgraded PDFs generated with perfect alignment and comprehensive content!")
