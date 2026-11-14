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
            self.drawString(MARGIN, PAGE_HEIGHT - 36, "AI Road Damage & Pothole Detection System | Official Technical Documentation")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(MARGIN, PAGE_HEIGHT - 42, MARGIN + USABLE_WIDTH, PAGE_HEIGHT - 42)
            
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(MARGIN, 44, MARGIN + USABLE_WIDTH, 44)
        
        self.drawString(MARGIN, 30, "AI-Powered Pothole Detection & Road Hazard Intelligence System | Engineering Dossier")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(MARGIN + USABLE_WIDTH, 30, page_text)
        self.restoreState()


# ── Global Typography Styles ──────────────────────────────────────────────────
styles = getSampleStyleSheet()

primary_color = colors.HexColor("#ea580c")    # Amber / Orange
secondary_color = colors.HexColor("#0f172a")  # Deep Slate Navy
text_dark = colors.HexColor("#1e293b")        # Charcoal Text
accent_blue = colors.HexColor("#0284c7")
accent_green = colors.HexColor("#16a34a")

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
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
    spaceAfter=8,
)

h1_style = ParagraphStyle(
    "SectionH1",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=secondary_color,
    spaceBefore=12,
    spaceAfter=5,
    keepWithNext=True,
)

h2_style = ParagraphStyle(
    "SectionH2",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=13,
    textColor=primary_color,
    spaceBefore=8,
    spaceAfter=3,
    keepWithNext=True,
)

body_style = ParagraphStyle(
    "BodyDark",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=12.5,
    textColor=text_dark,
    spaceAfter=5,
)

bullet_style = ParagraphStyle(
    "BulletText",
    parent=body_style,
    leftIndent=12,
    firstLineIndent=-8,
    spaceAfter=3,
)

code_style = ParagraphStyle(
    "CodeSnippet",
    parent=styles["Normal"],
    fontName="Courier",
    fontSize=7.8,
    leading=10.5,
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
    fontSize=8.2,
    leading=12,
    textColor=colors.HexColor("#0f172a"),
    backColor=colors.HexColor("#fff7ed"),
    borderColor=colors.HexColor("#fdba74"),
    borderWidth=0.8,
    borderPadding=6,
    spaceBefore=4,
    spaceAfter=5,
)

# Table Cell Styles
th_style = ParagraphStyle(
    "TableHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.8,
    leading=10.5,
    textColor=colors.white,
    alignment=0,
)

td_style = ParagraphStyle(
    "TableCell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=10.5,
    textColor=text_dark,
    alignment=0,
)

td_bold = ParagraphStyle(
    "TableCellBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=10.5,
    textColor=text_dark,
    alignment=0,
)

td_code = ParagraphStyle(
    "TableCellCode",
    parent=styles["Normal"],
    fontName="Courier",
    fontSize=7.2,
    leading=9.5,
    textColor=colors.HexColor("#0f172a"),
    alignment=0,
)

def make_cell(text, style=td_style):
    return Paragraph(str(text), style)


# ══════════════════════════════════════════════════════════════════════════════
#   PDF 1: COMPLETE PROJECT STRUCTURE, TECHNOLOGIES & SYSTEM ARCHITECTURE
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
    story.append(Paragraph("TECHNICAL DOSSIER: COMPLETE SYSTEM ARCHITECTURE, TECHNOLOGIES & PROJECT STRUCTURE", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=8))

    # Chapter 1
    story.append(Paragraph("1. Executive Summary & Why This Project Matters", h1_style))
    story.append(Paragraph(
        "Modern surface transportation networks form the bedrock of economic productivity. However, roadway surfaces are subjected to continuous degradation driven by climatic thermal cycles, rain water infiltration, heavy commercial vehicle axle loading, and sub-grade soil subsidence. "
        "Asphalt failures—principally potholes, longitudinal fractures, and severe alligator fatigue cracking—present severe hazards to motorists and public safety worldwide.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Real-World Crisis:</b> According to global transportation safety statistics, potholes cause tens of thousands of vehicular accidents annually, lead to catastrophic tire blowouts, crack vehicle alloy rims, ruin suspension assemblies, and trigger severe traffic bottlenecks. In two-wheelers, unexpected potholes are a primary cause of fatal collisions.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Failure of Traditional Inspection Methods:</b> Municipal authorities traditionally depend on manual ocular road surveys, citizen complaints, or costly laser-profilometer scanning trucks (costing upwards of $300,000 per vehicle). "
        "These legacy approaches are slow, reactive, labor-intensive, hazardous to surveyors, and leave rural or secondary roads uninspected for years.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The AI Solution:</b> This project delivers an automated, edge-capable <b>Real-Time Road Hazard Intelligence System</b>. "
        "By fusing state-of-the-art computer vision (YOLOv8) with WebRTC peer-to-peer camera streaming and a deterministic decision engine, the system detects, classifies, and evaluates potholes live. It translates optical detections into instant driving guidance—assessing road condition, prescribing safe ceiling speeds, and delivering audio alerts.",
        body_style
    ))

    # Chapter 2
    story.append(Paragraph("2. Technologies Used & Architectural Justification", h1_style))
    story.append(Paragraph(
        "Every library and framework in this application was selected to optimize inference framerates, minimize latency, and enable zero-install browser accessibility:",
        body_style
    ))

    t1_data = [
        [make_cell("Technology / Framework", th_style), make_cell("Version", th_style), make_cell("Role in System Architecture", th_style), make_cell("Why Chosen over Alternatives", th_style)],
        [
            make_cell("Ultralytics YOLOv8", td_bold),
            make_cell("8.0+", td_code),
            make_cell("Core Deep Learning object detection backbone for pothole localization.", td_style),
            make_cell("Anchor-free architecture with C2f feature extractors provides superior mAP and speed on irregular asphalt contours compared to YOLOv5 or SSD.", td_style)
        ],
        [
            make_cell("PyTorch / Torchvision", td_bold),
            make_cell("2.1+", td_code),
            make_cell("Tensor computation backend & neural network inference runtime.", td_style),
            make_cell("Industry standard ML engine with native CUDA GPU acceleration and optimized CPU kernels via OpenVINO / MKL.", td_style)
        ],
        [
            make_cell("Streamlit Community Framework", td_bold),
            make_cell("1.30+", td_code),
            make_cell("Reactive web presentation layer and control panel.", td_style),
            make_cell("Eliminates complex React/Node.js stacks; provides fast, clean Python-only reactive dashboarding with built-in cloud deployment support.", td_style)
        ],
        [
            make_cell("Streamlit-WebRTC (aiortc + av)", td_bold),
            make_cell("0.47+", td_code),
            make_cell("WebRTC peer-to-peer real-time video streaming engine.", td_style),
            make_cell("Bypasses HTTP overhead; streams live browser camera feed directly to Python worker threads at 30 FPS without script reloading.", td_style)
        ],
        [
            make_cell("OpenCV (opencv-python-headless)", td_bold),
            make_cell("4.10+", td_code),
            make_cell("Image matrix transformations, HUD drawing, and video demuxing.", td_style),
            make_cell("Headless variant avoids heavy X11 GUI dependencies, ensuring flawless execution in Linux containers and cloud servers.", td_style)
        ],
        [
            make_cell("NumPy", td_bold),
            make_cell("1.26+", td_code),
            make_cell("Vectorized array operations and geometric area computations.", td_style),
            make_cell("C-optimized matrix calculations calculate relative bounding-box area ratios in microseconds.", td_style)
        ],
        [
            make_cell("Base64 / HTML5 Audio", td_bold),
            make_cell("Native", td_code),
            make_cell("Asynchronous acoustic hazard warning system.", td_style),
            make_cell("Embeds audio directly into DOM; overcomes browser sandbox restrictions that block automated local file playback.", td_style)
        ],
        [
            make_cell("CSS3 Mobile-First Design", td_bold),
            make_cell("Modern", td_code),
            make_cell("Cyber-slate responsive UI with 2x2 grid controls.", td_style),
            make_cell("Fluid typography and automatic column stacking ensure responsive performance on both 4K desktop monitors and smartphone screens.", td_style)
        ]
    ]
    t1 = Table(t1_data, colWidths=[110, 48, 174, 190])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t1)

    story.append(PageBreak())

    # Chapter 3
    story.append(Paragraph("3. Complete Project File & Directory Structure Breakdown", h1_style))
    story.append(Paragraph(
        "The repository follows a clean, modular micro-architecture separating machine learning logic, presentation layers, assets, and cloud deployment configuration:",
        body_style
    ))

    t_tree = [
        [make_cell("File / Directory Path", th_style), make_cell("Component Type", th_style), make_cell("Detailed Description & Architectural Responsibilities", th_style)],
        [
            make_cell("app/app1.py", td_code),
            make_cell("Primary Application", td_bold),
            make_cell("Main Streamlit entry point. Configures page layout, injects responsive CSS, handles WebRTC stream pipeline, runs video playback loops, renders HUD telemetry, and displays diagnosis dashboard.", td_style)
        ],
        [
            make_cell("app/detection.py", td_code),
            make_cell("Decision Engine", td_bold),
            make_cell("Contains data classes (<code>Detection</code>, <code>RoadAnalysis</code>), bounding-box severity classifier, and deterministic rule hierarchy for road condition grading and safe speed calculation.", td_style)
        ],
        [
            make_cell("app/__init__.py", td_code),
            make_cell("Package Marker", td_bold),
            make_cell("Initializes <code>app</code> as a Python module, allowing cross-directory module resolution across sub-packages.", td_style)
        ],
        [
            make_cell("best.pt", td_code),
            make_cell("Model Weights (6.2 MB)", td_bold),
            make_cell("Fine-tuned YOLOv8 neural network weights trained on thousands of annotated real-world pothole images. Loaded dynamically by <code>@st.cache_resource</code>.", td_style)
        ],
        [
            make_cell("assets/alert.wav", td_code),
            make_cell("Audio Asset", td_bold),
            make_cell("High-frequency audio waveform (176 KB) fired when the road transitions to Poor condition to alert drivers before impact.", td_style)
        ],
        [
            make_cell("screenshots/", td_code),
            make_cell("Media Assets", td_bold),
            make_cell("Contains <code>home.png</code> and <code>demo.png</code> visual references demonstrating app interface and bounding box detection for documentation and README display.", td_style)
        ],
        [
            make_cell("requirements.txt", td_code),
            make_cell("Python Dependencies", td_bold),
            make_cell("Specifies exact Python wheels (<code>streamlit</code>, <code>ultralytics</code>, <code>opencv-python-headless</code>, <code>streamlit-webrtc</code>, <code>av</code>, <code>pillow</code>, <code>numpy<2</code>) installed by pip.", td_style)
        ],
        [
            make_cell("packages.txt", td_code),
            make_cell("System OS Packages", td_bold),
            make_cell("Instructs Debian/Ubuntu host containers on Streamlit Cloud to install low-level C libraries: <code>libgl1</code>, <code>libglib2.0-0t64</code>, and <code>libgthread-2.0-0</code>.", td_style)
        ],
        [
            make_cell("runtime.txt", td_code),
            make_cell("Cloud Runtime", td_bold),
            make_cell("Locks the Streamlit Community Cloud execution environment to <code>python-3.11.9</code>, ensuring zero package deprecation conflicts.", td_style)
        ],
        [
            make_cell(".gitattributes", td_code),
            make_cell("Git LFS Rules", td_bold),
            make_cell("Configures Git Large File Storage filters for binary tracking (<code>*.pt</code>, <code>*.wav</code>, <code>*.png</code>).", td_style)
        ],
        [
            make_cell(".gitignore", td_code),
            make_cell("Version Control Ignore", td_bold),
            make_cell("Excludes virtual environment folders (<code>venv/</code>), Python bytecode (<code>__pycache__/</code>), and temporary session caches.", td_style)
        ]
    ]
    ttree = Table(t_tree, colWidths=[120, 102, 300])
    ttree.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(ttree)

    story.append(Spacer(1, 6))

    # Chapter 4
    story.append(Paragraph("4. Key Features & Operational Capabilities", h1_style))
    story.append(Paragraph(
        "The system incorporates six advanced operational features engineered for both desktop analysis and in-cabin vehicular deployment:",
        body_style
    ))
    story.append(Paragraph("• <b>1. Multi-Input Modality Suite:</b> Operates seamlessly across four input formats: real-time browser camera (WebRTC), high-resolution smartphone snapshots (camera input), pre-recorded dashcam video clips (MP4/AVI), and high-resolution photo uploads (JPG/PNG).", bullet_style))
    story.append(Paragraph("• <b>2. Zero-Lag 30 FPS Real-Time Streaming:</b> WebRTC integration streams video peer-to-peer directly from smartphone rear cameras. Features 640px auto-scaling, fast 320px YOLO inference, and alternate-frame execution to eliminate CPU lag on cloud servers.", bullet_style))
    story.append(Paragraph("• <b>3. Relative Geometric Severity Classification:</b> Analyzes the surface area ratio of defects against total camera viewport geometry, grading hazards into Minor (🟢), Moderate (🟡), and Severe (🔴).", bullet_style))
    story.append(Paragraph("• <b>4. Deterministic Road Hazard Intelligence:</b> Evaluates cumulative defect density to grade overall pavement as <b>Good</b>, <b>Moderate</b>, or <b>Poor</b>.", bullet_style))
    story.append(Paragraph("• <b>5. Safe Driving Speed Advisory:</b> Continuously computes and displays dynamic maximum safe driving speeds (20 km/h for Poor, 40 km/h for Moderate, 60 km/h for Good).", bullet_style))
    story.append(Paragraph("• <b>6. Acoustic Warning Guardrails:</b> Plays an audible alarm when road conditions degrade to Poor, featuring a 3.0-second cooldown interval to prevent driver alarm fatigue.", bullet_style))

    story.append(PageBreak())

    # Chapter 5
    story.append(Paragraph("5. Mathematical Engine & Decision Logic", h1_style))
    story.append(Paragraph(
        "Inside <code>detection.py</code>, relative bounding-box geometry is computed to classify individual potholes by physical severity:",
        body_style
    ))
    story.append(Paragraph(
        "$$\\text{Relative Defect Area (}\\alpha\\text{)} = \\frac{\\text{Width}_{bbox} \\times \\text{Height}_{bbox}}{\\text{Width}_{frame} \\times \\text{Height}_{frame}} = \\frac{|x_2 - x_1| \\times |y_2 - y_1|}{W_{frame} \\times H_{frame}}$$",
        code_style
    ))

    t_sev = [
        [make_cell("Severity Tier", th_style), make_cell("Area Threshold (α)", th_style), make_cell("Bounding Color", th_style), make_cell("Physical Asphalt Characteristics & Impact", th_style)],
        [make_cell("🟢 Minor Damage", td_bold), make_cell("α < 0.005 (0.5%)", td_code), make_cell("Green (#22c55e, 2px)", td_style), make_cell("Surface cracks, shallow pitting. Negligible suspension vibration.", td_style)],
        [make_cell("🟡 Moderate Hazard", td_bold), make_cell("0.005 ≤ α < 0.025", td_code), make_cell("Amber (#f59e0b, 3px)", td_style), make_cell("Medium pothole (20-50 cm). Noticeable impact shock; tire wear hazard.", td_style)],
        [make_cell("🔴 Severe Hazard", td_bold), make_cell("α ≥ 0.025 (2.5%)", td_code), make_cell("Red (#ef4444, 4px)", td_style), make_cell("Deep structural crater (>50 cm). High risk of rim bend, tire blowout, or roll.", td_style)]
    ]
    tsev = Table(t_sev, colWidths=[95, 95, 110, 222])
    tsev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(tsev)

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Deterministic Decision Rules for Road Assessment & Speed Advisory:</b>", h2_style))

    t_rules = [
        [make_cell("Rule Precedence", th_style), make_cell("Logical Condition", th_style), make_cell("Road Condition", th_style), make_cell("Safe Speed", th_style), make_cell("Actionable Safety Warning", th_style)],
        [make_cell("Rule 1 (Critical)", td_bold), make_cell("Severe Count ≥ 1", td_code), make_cell("🔴 POOR", td_bold), make_cell("20 km/h", td_bold), make_cell("DANGER: Severe potholes detected! Reduce speed immediately to avoid vehicle damage.", td_style)],
        [make_cell("Rule 2 (Density)", td_bold), make_cell("Moderate Count ≥ 2", td_code), make_cell("🟡 MODERATE", td_bold), make_cell("40 km/h", td_bold), make_cell("CAUTION: Multiple moderate potholes ahead. Maintain safe distance and decelerate.", td_style)],
        [make_cell("Rule 3 (Scatter)", td_bold), make_cell("Total Count ≥ 3", td_code), make_cell("🟡 MODERATE", td_bold), make_cell("40 km/h", td_bold), make_cell("NOTICE: Scattered surface defects detected. Road quality degraded; drive with care.", td_style)],
        [make_cell("Rule 4 (Nominal)", td_bold), make_cell("Otherwise", td_code), make_cell("🟢 GOOD", td_bold), make_cell("60 km/h", td_bold), make_cell("Road surface is within safe operating parameters. Standard cruising permitted.", td_style)]
    ]
    tr = Table(t_rules, colWidths=[85, 95, 75, 65, 202])
    tr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(tr)

    story.append(Spacer(1, 6))

    # Chapter 6
    story.append(Paragraph("6. End-to-End Perception & Data Flow Pipeline", h1_style))
    story.append(Paragraph(
        "The end-to-end telemetry pipeline operates across seven discrete execution phases per frame:",
        body_style
    ))
    story.append(Paragraph("1. <b>Frame Acquisition:</b> Image/video frames are polled from WebRTC video worker, file uploader, or camera snapshot buffer.", bullet_style))
    story.append(Paragraph("2. <b>Dynamic Scaling & Preprocessing:</b> High-resolution streams are scaled down to 640px maximum width, retaining asphalt features while maintaining CPU throughput.", bullet_style))
    story.append(Paragraph("3. <b>YOLOv8 Inference:</b> Tensor pass runs at <code>imgsz=320</code> with configurable confidence threshold (default: 0.25).", bullet_style))
    story.append(Paragraph("4. <b>Bounding Box Parsing:</b> Raw coordinates ($x_1, y_1, x_2, y_2$) and confidence values are mapped to <code>Detection</code> domain objects.", bullet_style))
    story.append(Paragraph("5. <b>Hazard Evaluation:</b> Decision engine classifies defect severity and evaluates Road Condition rules.", bullet_style))
    story.append(Paragraph("6. <b>Visual HUD Rendering:</b> OpenCV overlays color-coded bounding boxes, severity labels, confidence scores, top HUD telemetry bar, and condition badges.", bullet_style))
    story.append(Paragraph("7. <b>Reactive Dashboard Update & Audio Alert:</b> Streamlit updates speedometer and metric cards, triggering Base64 audio if transitioning into Poor condition.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF 1 at: {filepath}")


# ══════════════════════════════════════════════════════════════════════════════
#   PDF 2: COMPLETE SETUP, LOCAL EXECUTION & STREAMLIT CLOUD HOSTING GUIDE
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
    story.append(Paragraph("OPERATOR MANUAL: PREREQUISITES, LOCAL SETUP, RESOLVING BOTTLENECKS & CLOUD HOSTING", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=8))

    # Chapter 1
    story.append(Paragraph("1. Tools & Prerequisites Required Before Project Begins", h1_style))
    story.append(Paragraph(
        "Before setting up the project locally or preparing for cloud deployment, verify that your development workstation satisfies these hardware and software prerequisites:",
        body_style
    ))

    t_req = [
        [make_cell("Tool / Requirement", th_style), make_cell("Required Version", th_style), make_cell("Role & Purpose", th_style), make_cell("Verification / Download Command", th_style)],
        [
            make_cell("Python Runtime", td_bold),
            make_cell("3.11.x 64-bit", td_code),
            make_cell("Executes PyTorch, OpenCV, and Streamlit scripts.", td_style),
            make_cell("<code>python --version</code> (Download from python.org)", td_style)
        ],
        [
            make_cell("Git CLI", td_bold),
            make_cell("2.40+", td_code),
            make_cell("Clones codebase and syncs commits to GitHub.", td_style),
            make_cell("<code>git --version</code> (Download from git-scm.com)", td_style)
        ],
        [
            make_cell("Git LFS (Large File Storage)", td_bold),
            make_cell("3.3+", td_code),
            make_cell("Mandatory for uploading and downloading binary model weights (<code>best.pt</code>).", td_style),
            make_cell("<code>git lfs --version</code> followed by <code>git lfs install</code>", td_style)
        ],
        [
            make_cell("Visual Studio Code (IDE)", td_bold),
            make_cell("Latest", td_code),
            make_cell("Integrated development environment with Python and terminal support.", td_style),
            make_cell("code.visualstudio.com (Include Python extension)", td_style)
        ],
        [
            make_cell("Hardware (CPU / RAM)", td_bold),
            make_cell("4+ Cores, 8GB RAM", td_code),
            make_cell("Runs local deep learning inference and multi-threaded video streaming.", td_style),
            make_cell("Recommended: 16GB RAM for multi-hour video analysis.", td_style)
        ],
        [
            make_cell("Webcam / Smartphone", td_bold),
            make_cell("720p / 1080p", td_code),
            make_cell("Captures real-time road footage for live detection testing.", td_style),
            make_cell("Any standard USB webcam or mobile browser camera.", td_style)
        ],
        [
            make_cell("Accounts Needed", td_bold),
            make_cell("Free Tier", td_code),
            make_cell("GitHub (repository hosting) & Streamlit Cloud (web hosting).", td_style),
            make_cell("github.com & share.streamlit.io", td_style)
        ]
    ]
    trq = Table(t_req, colWidths=[105, 75, 172, 170])
    trq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(trq)

    # Chapter 2
    story.append(Paragraph("2. Step-by-Step Local Environment Setup & Execution", h1_style))
    story.append(Paragraph(
        "Follow these sequential commands in your VS Code terminal to establish an isolated environment and run the project locally:",
        body_style
    ))

    story.append(Paragraph("<b>Step 1: Clone the GitHub Repository</b>", h2_style))
    story.append(Paragraph("git clone https://github.com/muthujoygroup-art/pothole-detection-system.git<br/>cd pothole-detection-system", code_style))

    story.append(Paragraph("<b>Step 2: Initialize Isolated Virtual Environment (venv)</b>", h2_style))
    story.append(Paragraph("python -m venv venv", code_style))

    story.append(Paragraph("<b>Step 3: Activate the Virtual Environment</b>", h2_style))
    story.append(Paragraph("• <b>On Windows PowerShell:</b> <code>.\\venv\\Scripts\\activate</code><br/>"
                           "• <b>On Windows Command Prompt (CMD):</b> <code>.\\venv\\Scripts\\activate.bat</code><br/>"
                           "• <b>On macOS / Linux (bash/zsh):</b> <code>source venv/bin/activate</code>", body_style))

    story.append(Paragraph("<b>Step 4: Install Dependencies via Python Module</b>", h2_style))
    story.append(Paragraph(
        "Always execute package installation using <code>python -m pip</code> rather than calling <code>pip.exe</code> directly to bypass Windows Application Control blocks:",
        body_style
    ))
    story.append(Paragraph("python -m pip install -r requirements.txt", code_style))

    story.append(Paragraph("<b>Step 5: Verify Model Weights File (best.pt)</b>", h2_style))
    story.append(Paragraph(
        "Confirm that <code>best.pt</code> (approx. 6.2 MB) exists in the project root directory. If Git LFS pointer is small (approx 130 bytes), pull the full file using: <code>git lfs pull</code>.",
        body_style
    ))

    story.append(Paragraph("<b>Step 6: Launch the Streamlit Web Application</b>", h2_style))
    story.append(Paragraph("python -m streamlit run app/app1.py", code_style))

    story.append(Paragraph("<b>Step 7: Access the Dashboard in Your Browser</b>", h2_style))
    story.append(Paragraph("• <b>Local PC Access:</b> Open <code>http://localhost:8501</code> in Chrome, Edge, or Safari.<br/>"
                           "• <b>Mobile Access on Same Wi-Fi:</b> Open your mobile browser and enter the Network URL printed in your terminal: <code>http://[YOUR_PC_IP]:8501</code> (e.g., <code>http://192.168.1.15:8501</code>).", body_style))

    story.append(PageBreak())

    # Chapter 3
    story.append(Paragraph("3. Resolving Windows-Specific Security & Path Bottlenecks", h1_style))
    story.append(Paragraph(
        "Windows systems frequently enforce security policies or legacy filesystem limits that can trigger setup errors. Apply these verified resolutions:",
        body_style
    ))

    story.append(Paragraph("Issue 1: 'Program pip.exe failed to run: Application Control policy blocked this file'", h2_style))
    story.append(Paragraph(
        "<b>Technical Cause:</b> Windows Defender Application Control (WDAC) or SmartApp Control blocks executable binary stubs generated inside virtual environment folders.<br/>"
        "<b>Permanent Fix:</b> Bypass the stub by executing pip as a module: <code>python -m pip install -r requirements.txt</code>",
        callout_style
    ))

    story.append(Paragraph("Issue 2: 'Execution of scripts is disabled on this system' (PowerShell Error)", h2_style))
    story.append(Paragraph(
        "<b>Technical Cause:</b> PowerShell restricts execution of external script files by default.<br/>"
        "<b>Permanent Fix:</b> In PowerShell, run: <code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass</code>, then activate the venv.",
        callout_style
    ))

    story.append(Paragraph("Issue 3: 'OSError: [Errno 2] No such file or directory (MAX_PATH Limit)'", h2_style))
    story.append(Paragraph(
        "<b>Technical Cause:</b> Deeply nested third-party packages exceed the default Windows 260-character path limit.<br/>"
        "<b>Permanent Fix:</b> In an Administrator PowerShell, run this command to enable native Win32 long paths:",
        body_style
    ))
    story.append(Paragraph("New-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem' -Name 'LongPathsEnabled' -Value 1 -PropertyType DWORD -Force", code_style))

    story.append(Spacer(1, 6))

    # Chapter 4
    story.append(Paragraph("4. Complete Guide: Hosting from GitHub to Streamlit Cloud", h1_style))
    story.append(Paragraph(
        "Deploying the project on Streamlit Community Cloud makes it accessible worldwide via a public URL with zero hosting fees. Follow these verified deployment steps:",
        body_style
    ))

    story.append(Paragraph("<b>Step 1: Push Code & LFS Files to GitHub</b>", h2_style))
    story.append(Paragraph(
        "Because <code>best.pt</code> and <code>assets/alert.wav</code> are tracked with Git LFS in <code>.gitattributes</code>, a standard <code>git push</code> only uploads text pointers. You must push LFS objects explicitly:",
        body_style
    ))
    story.append(Paragraph("git add .\ngit commit -m \"Prepare for Streamlit Cloud Deployment\"\ngit push origin main\ngit lfs push --all origin main", code_style))

    story.append(Paragraph("<b>Step 2: Connect to Streamlit Community Cloud</b>", h2_style))
    story.append(Paragraph(
        "1. Open <b>share.streamlit.io</b> in your browser.<br/>"
        "2. Click <b>Continue with GitHub</b> and sign in with your GitHub account (<code>muthujoygroup-art</code>).<br/>"
        "3. Grant Streamlit Cloud the necessary OAuth permissions to access your repositories.",
        body_style
    ))

    story.append(Paragraph("<b>Step 3: Create App & Fill Deployment Coordinates</b>", h2_style))
    story.append(Paragraph(
        "Click <b>Create app</b> (top right) → select <b>I already have an app</b>, then enter these exact parameters:",
        body_style
    ))

    t_cloud = [
        [make_cell("Form Field Name", th_style), make_cell("Exact Value to Enter / Select", th_style), make_cell("Critical Notes & Explanation", th_style)],
        [
            make_cell("Repository", td_bold),
            make_cell("muthujoygroup-art/pothole-detection-system", td_code),
            make_cell("Select your repository from the dropdown or paste the repository name.", td_style)
        ],
        [
            make_cell("Branch", td_bold),
            make_cell("main", td_code),
            make_cell("Default branch containing all recent UI and WebRTC updates.", td_style)
        ],
        [
            make_cell("Main file path", td_bold),
            make_cell("app/app1.py", td_code),
            make_cell("⚠️ CRITICAL: Streamlit defaults to 'app.py' or 'streamlit_app.py'. You MUST enter 'app/app1.py' or deployment fails with FileNotFoundError.", td_style)
        ],
        [
            make_cell("App URL (Optional)", td_bold),
            make_cell("pothole-detection.streamlit.app", td_code),
            make_cell("Custom subdomain for clean, memorable sharing with evaluators and clients.", td_style)
        ]
    ]
    tcl = Table(t_cloud, colWidths=[110, 192, 220])
    tcl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(tcl)

    story.append(Paragraph("<b>Step 4: Advanced Settings (Python Version)</b>", h2_style))
    story.append(Paragraph(
        "Click <b>Advanced settings</b> before deploying and select <b>Python 3.11</b>. This matches your <code>runtime.txt</code> configuration.",
        body_style
    ))

    story.append(Paragraph("<b>Step 5: Deploy & Monitor Build</b>", h2_style))
    story.append(Paragraph(
        "Click <b>Deploy!</b>. Streamlit Cloud automatically clones your repository, installs system packages from <code>packages.txt</code>, installs Python dependencies from <code>requirements.txt</code>, and launches your app live.",
        body_style
    ))

    story.append(PageBreak())

    # Chapter 5
    story.append(Paragraph("5. Streamlit Cloud Troubleshooting Matrix & Error Fixes", h1_style))
    story.append(Paragraph(
        "Reference this troubleshooting guide to diagnose and resolve any cloud deployment anomalies:",
        body_style
    ))

    t_tb = [
        [make_cell("Error / Symptom on Cloud", th_style), make_cell("Root Cause Analysis", th_style), make_cell("Exact Corrective Action / Fix", th_style)],
        [
            make_cell("🐙 Failed to download sources<br/>(Smudge error / 404)", td_bold),
            make_cell("Git LFS objects (<code>best.pt</code>, <code>alert.wav</code>) exist as pointer files on GitHub without the actual binary data.", td_style),
            make_cell("In local terminal, run: <code>git lfs push --all origin main</code> to upload the binary blobs to GitHub LFS, then reboot the app in Streamlit Cloud.", td_style)
        ],
        [
            make_cell("⚠️ FileNotFoundError:<br/>[Errno 2] 'app.py'", td_bold),
            make_cell("The Main file path in Streamlit deployment settings was left at default <code>app.py</code>.", td_style),
            make_cell("Go to Streamlit dashboard → App Settings → General → Change Main file path to <code>app/app1.py</code> and save.", td_style)
        ],
        [
            make_cell("❌ Camera not opened on cloud<br/>(cv2.VideoCapture error)", td_bold),
            make_cell("Cloud virtual machines are headless servers without physical webcam hardware plugged into them.", td_style),
            make_cell("Use the <b>📹 Live Camera (WebRTC)</b> mode. WebRTC connects your mobile phone or laptop camera through the browser rather than server hardware.", td_style)
        ],
        [
            make_cell("You do not have access to this app or it does not exist", td_bold),
            make_cell("The URL opened in the browser corresponds to a deleted app instance.", td_style),
            make_cell("Click <b>My apps</b> in the top navigation bar at share.streamlit.io and select the active running app card.", td_style)
        ],
        [
            make_cell("Live camera stream lag / stuttering on mobile", td_bold),
            make_cell("Smartphone sending 1080p/4K frames over saturated mobile network, overloading cloud CPU.", td_style),
            make_cell("Ensure <code>media_stream_constraints</code> requests 640x480 resolution and model executes at <code>imgsz=320</code> (already configured in latest commit).", td_style)
        ],
        [
            make_cell("App stuck in 'Baking' or building state", td_bold),
            make_cell("PyTorch or Ultralytics download timed out during initial container setup.", td_style),
            make_cell("Click the bottom-right three dots (<code>⋮</code>) → select <b>Reboot app</b>. You can monitor progress by opening the <b>Logs</b> drawer.", td_style)
        ]
    ]
    ttb = Table(t_tb, colWidths=[130, 160, 232])
    ttb.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(ttb)

    story.append(Spacer(1, 8))

    # Chapter 6
    story.append(Paragraph("6. Operating the App: Visual Indicators & Driver Response", h1_style))
    story.append(Paragraph(
        "Once deployed locally or on Streamlit Cloud, drivers and evaluators should interpret the HUD indicators as follows:",
        body_style
    ))

    t_op = [
        [make_cell("Operating Mode", th_style), make_cell("Best Use Case", th_style), make_cell("How to Operate", th_style), make_cell("Generated Output", th_style)],
        [
            make_cell("📹 Live Camera (WebRTC)", td_bold),
            make_cell("Live in-cabin driving dashcam; real-time pothole tracking.", td_style),
            make_cell("Select mode → tap 'START' → point camera at road. Clean UI without recording clutter.", td_style),
            make_cell("Real-time 30 FPS video with color-coded bounding boxes, HUD telemetry, and safe speed.", td_style)
        ],
        [
            make_cell("📱 Mobile Snapshot", td_bold),
            make_cell("Pedestrian or stationary inspection of specific road defects.", td_style),
            make_cell("Select mode → point camera at pothole → tap shutter button.", td_style),
            make_cell("High-resolution frozen frame analysis with exact defect severity grading and confidence.", td_style)
        ],
        [
            make_cell("📸 Image Upload", td_bold),
            make_cell("Post-drive survey evaluation using captured field photos.", td_style),
            make_cell("Drag & drop JPG/PNG image into the uploader zone.", td_style),
            make_cell("Immediate bounding box visualization, defect tally, and road safety assessment.", td_style)
        ],
        [
            make_cell("🎬 Video Upload", td_bold),
            make_cell("Batch dashcam evaluation of entire route recordings.", td_style),
            make_cell("Upload MP4/AVI file → video evaluates frame-by-frame.", td_style),
            make_cell("Continuous route assessment with dynamic speed recommendations and audio alerts.", td_style)
        ]
    ]
    top = Table(t_op, colWidths=[95, 115, 142, 170])
    top.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(top)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF 2 at: {filepath}")


if __name__ == "__main__":
    out_dir = r"C:\Users\HP\Documents\Muthu Projects\PROJECT 04 - AI - POTHOLE - DETECTION - SYSTEM\AI-Pothole-Detection-System"
    pdf1_path = os.path.join(out_dir, "PDF_1_Project_Structure_and_Technologies.pdf")
    pdf2_path = os.path.join(out_dir, "PDF_2_Setup_Execution_and_Hosting_Guide.pdf")
    
    build_pdf_1(pdf1_path)
    build_pdf_2(pdf2_path)
    
    # Also overwrite the original filenames for compatibility
    pdf1_legacy = os.path.join(out_dir, "PDF_1_Project_Details_and_Technologies.pdf")
    pdf2_legacy = os.path.join(out_dir, "PDF_2_Setup_and_Execution_Guide.pdf")
    build_pdf_1(pdf1_legacy)
    build_pdf_2(pdf2_legacy)
    print("All upgraded PDFs generated with perfect alignment and comprehensive content!")
