# ═══════════════════════════════════════════════════════════════════════════════
#   AI Road Damage & Pothole Detection System
#   app/app1.py  |  Run: python -m streamlit run app/app1.py
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import base64
import tempfile
import time
from datetime import datetime

import cv2
import numpy as np
import streamlit as st

# ── WebRTC Live Streaming ─────────────────────────────────────────────────────
try:
    from streamlit_webrtc import (
        webrtc_streamer,
        WebRtcMode,
        RTCConfiguration,
        VideoProcessorBase,
    )
    import av
    HAS_WEBRTC = True
except Exception:
    HAS_WEBRTC = False

RTC_CONFIGURATION = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
        ]
    }
)

# ── Resolve project root & add to path ────────────────────────────────────────
_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_APP_DIR, ".."))
for _p in (_APP_DIR, _ROOT_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Import decision engine ────────────────────────────────────────────────────
from detection import (
    Detection, DetectionSummary, RoadAnalysis,
    classify_severity, run_analysis,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Road Damage Detection",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── MODEL LOADER ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model():
    try:
        from ultralytics import YOLO
        for candidate in (
            os.path.join(_ROOT_DIR, "best.pt"),
            os.path.join(_APP_DIR,  "best.pt"),
            "best.pt",
        ):
            if os.path.exists(candidate):
                return YOLO(candidate)
    except Exception:
        pass
    return None

model = load_model()

# ── SESSION STATE ──────────────────────────────────────────────────────────────
_DEFAULTS = {
    "run_webcam":          False,
    "last_alert":          0.0,
    "prev_condition":      None,
    "last_frame":          None,
    "last_analysis":       None,
    "last_img_name":       None,
    "last_vid_name":       None,
    "last_vid_key":        None,
    "vid_bytes":            b"",
    "vid_processed":        False,
    "vid_stopped_by_user":  False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════════════════════════════════════
#   YOLO BOX CONVERSION
# ══════════════════════════════════════════════════════════════════════════════

def yolo_boxes_to_detections(boxes, frame_h: int, frame_w: int) -> list[Detection]:
    detections = []
    for box in boxes:
        xyxy = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0].cpu().numpy())
        x1, y1, x2, y2 = map(float, xyxy)
        detections.append(Detection(
            bbox=(x1, y1, x2, y2),
            confidence=conf,
            frame_width=frame_w,
            frame_height=frame_h,
        ))
    return detections


# ══════════════════════════════════════════════════════════════════════════════
#   FRAME ANNOTATION
# ══════════════════════════════════════════════════════════════════════════════

_SEV_BGR   = {"Minor": (34, 197, 94), "Moderate": (30, 180, 245), "Severe": (60, 60, 238)}
_SEV_THICK = {"Minor": 2, "Moderate": 3, "Severe": 4}
_COND_BGR  = {"Good": (34, 197, 94), "Moderate": (30, 165, 245), "Poor": (60, 60, 238)}

def draw_boxes(frame: np.ndarray, analysis: RoadAnalysis,
               fps: float = 0.0, conf_thresh: float = 0.25) -> np.ndarray:
    frame = frame.copy()
    img_h, img_w = frame.shape[:2]

    for det in analysis.summary.detections:
        sev   = classify_severity(det)
        color = _SEV_BGR[sev]
        thick = _SEV_THICK[sev]
        x1, y1, x2, y2 = map(int, det.bbox)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thick)

        label = f"{sev} | {int(det.confidence * 100)}%"
        font  = cv2.FONT_HERSHEY_SIMPLEX
        fsc, ftk = 0.50, 1
        (tw, th), bl = cv2.getTextSize(label, font, fsc, ftk)
        lx1, ly1 = x1, max(y1 - th - bl - 8, 0)
        cv2.rectangle(frame, (lx1, ly1), (lx1 + tw + 8, y1), color, -1)
        cv2.putText(frame, label, (lx1 + 4, y1 - bl - 2),
                    font, fsc, (255, 255, 255), ftk, cv2.LINE_AA)

    # Top HUD Bar
    fps_str  = f"{fps:.0f}" if fps > 0 else "--"
    bar_text = f" FPS: {fps_str}  |  Potholes: {analysis.summary.total}  |  Conf: {conf_thresh:.2f} "
    font     = cv2.FONT_HERSHEY_SIMPLEX
    fsc, ftk = 0.52, 2
    (_, bh), bl = cv2.getTextSize(bar_text, font, fsc, ftk)

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (img_w, bh + bl + 14), (12, 14, 20), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    cv2.putText(frame, bar_text, (10, bh + 8), font, fsc, (230, 235, 245), ftk, cv2.LINE_AA)

    tag = f" {analysis.condition} "
    (tw, th), tbl = cv2.getTextSize(tag, font, fsc, ftk)
    cv2.rectangle(frame, (img_w - tw - 14, 2), (img_w - 2, th + tbl + 12),
                  _COND_BGR[analysis.condition], -1)
    cv2.putText(frame, tag, (img_w - tw - 10, bh + 8),
                font, fsc, (255, 255, 255), ftk, cv2.LINE_AA)

    return frame


# ══════════════════════════════════════════════════════════════════════════════
#   WEBRTC VIDEO PROCESSOR (REAL-TIME 30 FPS STREAMING)
# ══════════════════════════════════════════════════════════════════════════════

if HAS_WEBRTC:
    class PotholeVideoProcessor(VideoProcessorBase):
        def __init__(self):
            self.confidence = 0.25
            self.last_analysis = None
            self._prev_t = time.time()
            self._fps = 0.0
            self._frame_count = 0
            self._cached_analysis = None

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            h, w = img.shape[:2]

            # Fast downscale if camera sends high-res stream (saves CPU & bandwidth)
            if w > 640:
                scale = 640.0 / w
                img = cv2.resize(img, (640, int(h * scale)))
                h, w = img.shape[:2]

            self._frame_count += 1
            now = time.time()
            dt = max(now - self._prev_t, 1e-4)
            self._fps = 1.0 / dt
            self._prev_t = now

            if model is not None:
                # Infer every 2nd frame at fast 320px for silky-smooth 0-lag real-time detection on CPU
                if self._frame_count % 2 == 0 or self._cached_analysis is None:
                    results = model.predict(img, imgsz=320, conf=self.confidence, verbose=False)
                    dets = yolo_boxes_to_detections(results[0].boxes, h, w)
                    self._cached_analysis = run_analysis(dets)
                    self.last_analysis = self._cached_analysis

                annotated = draw_boxes(img, self._cached_analysis, self._fps, self.confidence)
                return av.VideoFrame.from_ndarray(annotated, format="bgr24")

            return frame



# ══════════════════════════════════════════════════════════════════════════════
#   ALERT AUDIO
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def _alert_b64() -> str:
    path = os.path.join(_ROOT_DIR, "assets", "alert.wav")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

_ALERT_CACHE: dict = {}

def play_alert(current_condition: str):
    now  = time.time()
    prev = st.session_state.get("prev_condition", None)

    should_alert = (current_condition == "Poor") and (prev != current_condition)
    cooldown_ok  = (now - st.session_state.last_alert > 3.0)

    if should_alert and cooldown_ok:
        if _ALERT_CACHE.get("html") is None:
            b64 = _alert_b64()
            if b64:
                _ALERT_CACHE["html"] = (
                    f'<script>(function(){{'
                    f'try{{var b=atob("{b64}");'
                    f'var a=new Uint8Array(b.length);'
                    f'for(var i=0;i<b.length;i++)a[i]=b.charCodeAt(i);'
                    f'var u=URL.createObjectURL(new Blob([a],{{type:"audio/wav"}}));'
                    f'var x=new Audio(u);x.volume=0.85;'
                    f'x.play().catch(function(){{}});'
                    f'}}catch(e){{}}}})()</script>'
                )
        if _ALERT_CACHE.get("html"):
            st.components.v1.html(_ALERT_CACHE["html"], height=0)
        st.session_state.last_alert = now

    st.session_state.prev_condition = current_condition


# ══════════════════════════════════════════════════════════════════════════════
#   DASHBOARD CARD HTML
# ══════════════════════════════════════════════════════════════════════════════

_C = {
    "Good":     {"hex": "#22c55e", "glow": "rgba(34,197,94,0.35)",  "bg": "rgba(34,197,94,.10)",  "icon": "🟢", "label_bg": "#064e3b"},
    "Moderate": {"hex": "#f59e0b", "glow": "rgba(245,158,11,0.35)", "bg": "rgba(245,158,11,.10)", "icon": "🟡", "label_bg": "#451a03"},
    "Poor":     {"hex": "#ef4444", "glow": "rgba(239,68,68,0.40)",  "bg": "rgba(239,68,68,.10)",  "icon": "🔴", "label_bg": "#450a0a"},
}

def _dashboard_html(analysis: RoadAnalysis) -> str:
    cond  = analysis.condition
    speed = analysis.speed_kmh
    warn  = analysis.warning

    cc  = _C[cond]
    ch  = cc["hex"]
    cg  = cc["glow"]
    cb  = cc["bg"]
    ci  = cc["icon"]
    clb = cc["label_bg"]

    return (
        f'<div class="dash-container">'
        f'<div class="dash-card accent-card" style="border: 1px solid {ch}aa; box-shadow: 0 0 24px {cg};">'
        f'<div class="section-title">🛣️ Assessed Road Condition</div>'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">'
        f'<div style="font-size:clamp(1.8rem, 4vw, 2.3rem);font-weight:900;color:{ch};line-height:1.2;">'
        f'{ci} {cond}</div>'
        f'<div style="font-size:0.85rem;font-weight:800;color:#ffffff;letter-spacing:1.8px;'
        f'text-transform:uppercase;background:{clb};padding:7px 16px;'
        f'border-radius:8px;border:1px solid {ch};">{cond.upper()}</div>'
        f'</div></div>'
        f'<div class="dash-card accent-card" style="border: 1px solid {ch}aa; box-shadow: 0 0 24px {cg};">'
        f'<div class="section-title">⚡ Safe Driving Speed Advisory</div>'
        f'<div style="display:flex;align-items:flex-end;gap:10px;">'
        f'<div style="font-size:clamp(2.4rem, 5vw, 3.2rem);font-weight:900;color:{ch};line-height:1;">{speed}</div>'
        f'<div style="padding-bottom:5px;">'
        f'<div style="font-size:0.95rem;font-weight:800;color:#f3f4f6;text-transform:uppercase;">KM / H</div>'
        f'<div style="font-size:0.72rem;color:#9ca3af;font-weight:600;text-transform:uppercase;">Max Safe Speed</div>'
        f'</div></div></div>'
        f'<div class="dash-card" style="background:{cb};border:1.5px solid {ch};">'
        f'<div class="section-title" style="color:{ch};font-weight:800;">⚠️ Safety Alert</div>'
        f'<div style="font-size:0.95rem;font-weight:700;color:#ffffff;line-height:1.5;">{warn}</div>'
        f'</div>'
        f'</div>'
    )

def render_dashboard(analysis: RoadAnalysis, ph=None):
    html = _dashboard_html(analysis)
    if ph is not None:
        ph.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

# Idle state
_IDLE = RoadAnalysis(
    condition="Good", speed_kmh=60,
    warning="✅ Road is safe for normal driving. No hazardous potholes detected.",
    summary=DetectionSummary(total=0, minor=0, moderate=0, severe=0),
    display_score=100.0,
)

# Standby cards HTML
_EMPTY_IMG_HTML = (
    '<div class="empty-preview-card">'
    '<div class="empty-preview-icon">🖼️</div>'
    '<div class="empty-preview-title">No Road Image Uploaded</div>'
    '<div class="empty-preview-desc">Upload a dashcam or road surface photo above to run real-time YOLOv8 damage detection and hazard grading.</div>'
    '</div>'
)

_EMPTY_VID_HTML = (
    '<div class="empty-preview-card">'
    '<div class="empty-preview-icon">📹</div>'
    '<div class="empty-preview-title">No Video Uploaded</div>'
    '<div class="empty-preview-desc">Upload a driving or dashcam clip above to inspect road condition and detect potholes frame-by-frame.</div>'
    '</div>'
)

_EMPTY_CAM_HTML = (
    '<div class="empty-preview-card">'
    '<div class="empty-preview-icon">📷</div>'
    '<div class="empty-preview-title">Webcam Standby</div>'
    '<div class="empty-preview-desc">Click \'▶ Start Live Webcam\' above to activate your camera and begin real-time road hazard detection.</div>'
    '</div>'
)

_EMPTY_PHONE_HTML = (
    '<div class="empty-preview-card">'
    '<div class="empty-preview-icon">📱</div>'
    '<div class="empty-preview-title">Live Mobile Camera Standby</div>'
    '<div class="empty-preview-desc">Use the camera capture shutter below to capture the live road view from your smartphone or tablet.</div>'
    '</div>'
)


# ══════════════════════════════════════════════════════════════════════════════
#   HIGH-CONTRAST, IMPRESSIVE & RESPONSIVE CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* Base Dark Theme & Contrast Reset */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0c0f17 !important;
    color: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }
[data-testid="collapsedControl"], [data-testid="stDecoration"], [data-testid="stToolbar"] { display: none !important; }

.main .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1250px !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
}

/* Force High Contrast for ALL Streamlit Labels */
label, label p, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
    color: #ffffff !important;
    font-size: 0.96rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: #f97316 !important;
    font-size: 0.88rem !important;
    font-weight: 800 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}

/* Header Banner */
.app-header {
    background: linear-gradient(135deg, #161c2c 0%, #111420 100%);
    border: 1px solid rgba(249, 115, 22, 0.35);
    border-radius: 16px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 1.2rem;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.header-title-box { display: flex; align-items: center; gap: 14px; }
.header-icon { font-size: 2.2rem; filter: drop-shadow(0 2px 8px rgba(249, 115, 22, 0.4)); }
.header-title {
    font-size: clamp(1.3rem, 3.8vw, 1.85rem);
    font-weight: 900;
    color: #f97316;
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.header-subtitle {
    font-size: 0.78rem;
    color: #cbd5e1;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 700;
    margin-top: 2px;
}
.status-pill {
    background: rgba(34, 197, 94, 0.16);
    border: 1px solid rgba(34, 197, 94, 0.6);
    color: #4ade80;
    font-size: 0.82rem;
    font-weight: 800;
    padding: 7px 16px;
    border-radius: 100px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 0 15px rgba(34, 197, 94, 0.25);
}

/* High-Contrast Segmented Radio Buttons */
div[role="radiogroup"] {
    background: #151a28 !important;
    border: 1px solid #28334d !important;
    border-radius: 12px !important;
    padding: 6px !important;
    display: flex !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
}
div[role="radiogroup"] > label {
    background: #1e2638 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    flex: 1 1 auto !important;
    text-align: center !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
}
div[role="radiogroup"] > label:hover {
    background: #2b364d !important;
    border-color: #f97316 !important;
}
div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(135deg, #ea580c 0%, #f97316 100%) !important;
    border-color: #fb923c !important;
    color: #ffffff !important;
    box-shadow: 0 4px 16px rgba(249, 115, 22, 0.45) !important;
}
div[role="radiogroup"] label p {
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
}

/* Slider High Visibility */
div[data-testid="stSlider"] div[data-baseweb="slider"] {
    padding-top: 10px !important;
}
div[data-testid="stSlider"] [role="slider"] {
    background-color: #f97316 !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 0 12px rgba(249, 115, 22, 0.6) !important;
}

/* Severity Legend */
.sev-legend-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    background: #141926;
    border: 1px solid #28334d;
    border-radius: 12px;
    padding: 10px 18px;
    font-size: 0.88rem;
    font-weight: 800;
    flex-wrap: wrap;
    margin: 0.6rem 0 1rem;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
.sev-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Fix Blinding White File Uploader */
[data-testid="stFileUploader"] {
    background: transparent !important;
    margin-bottom: 1rem !important;
}
[data-testid="stFileUploaderDropzone"],
section[data-testid="stFileUploadDropzone"],
[data-testid="stFileUploader"] > section {
    background-color: #151a28 !important;
    border: 2px dashed #f97316 !important;
    border-radius: 14px !important;
    padding: 1.2rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}
[data-testid="stFileUploaderDropzone"] *,
section[data-testid="stFileUploadDropzone"] *,
[data-testid="stFileUploader"] * {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}
[data-testid="stFileUploaderDropzone"] button,
section[data-testid="stFileUploadDropzone"] button {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    padding: 0.5rem 1.4rem !important;
    box-shadow: 0 4px 14px rgba(249, 115, 22, 0.4) !important;
}

/* Empty State Preview Card */
.empty-preview-card {
    background: #141926;
    border: 2px dashed #28334d;
    border-radius: 14px;
    padding: 3rem 1.5rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 380px;
}
.empty-preview-icon {
    font-size: 3rem;
    margin-bottom: 10px;
    filter: drop-shadow(0 4px 12px rgba(249, 115, 22, 0.3));
}
.empty-preview-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #f97316;
}
.empty-preview-desc {
    font-size: 0.85rem;
    color: #94a3b8;
    max-width: 380px;
    margin-top: 6px;
    line-height: 1.5;
}

/* Dashboard Metrics & Cards */
.dash-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.dash-card {
    background: #141926;
    border: 1px solid #28334d;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}
.section-title {
    font-size: 0.78rem;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    margin-bottom: 10px;
}

/* Performance Tags */
.fps-tag {
    display: inline-block;
    background: #141926;
    border: 1px solid #28334d;
    color: #ffffff;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-family: monospace;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.4rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    box-shadow: 0 4px 16px rgba(249, 115, 22, 0.4) !important;
}
.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(249, 115, 22, 0.55) !important;
}

/* Clean Streamlined WebRTC Display — Hide all unnecessary toggles/dropdowns */
div[data-testid="stWebRtc"] {
    background: #141926 !important;
    border: 1px solid #28334d !important;
    border-radius: 14px !important;
    padding: 8px !important;
    overflow: hidden !important;
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}
div[data-testid="stWebRtc"] video {
    border-radius: 10px !important;
    width: 100% !important;
    max-height: 480px !important;
    object-fit: cover !important;
    background: #090c13 !important;
}
div[data-testid="stWebRtc"] button {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    padding: 10px 32px !important;
    margin: 8px auto !important;
    cursor: pointer !important;
    box-shadow: 0 4px 14px rgba(249, 115, 22, 0.45) !important;
}
div[data-testid="stWebRtc"] select,
div[data-testid="stWebRtc"] label,
div[data-testid="stWebRtc"] input[type="checkbox"],
div[data-testid="stWebRtc"] small {
    display: none !important;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-top: 0.5rem !important;
    }
    .app-header {
        padding: 0.8rem 1rem !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
    }
    .header-icon { font-size: 1.6rem !important; }
    .header-title { font-size: 1.15rem !important; }
    .header-subtitle { display: none !important; }
    .status-pill { font-size: 0.72rem !important; padding: 4px 10px !important; }

    /* Segmented mode buttons become a neat 2x2 grid on mobile */
    div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 6px !important;
        padding: 4px !important;
    }
    div[role="radiogroup"] > label {
        min-width: unset !important;
        padding: 10px 6px !important;
        font-size: 0.82rem !important;
    }
    div[role="radiogroup"] label p {
        font-size: 0.82rem !important;
    }

    /* Stack left/right columns vertically so preview and diagnosis take full width */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 12px !important;
    }
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    .sev-legend-wrap {
        gap: 8px !important;
        padding: 8px 10px !important;
        font-size: 0.76rem !important;
    }
    .dash-card {
        padding: 14px 16px !important;
    }
    .empty-preview-card {
        min-height: 200px !important;
        padding: 1.5rem 1rem !important;
    }
}
</style>

<!-- Header -->
<div class="app-header">
  <div class="header-title-box">
    <span class="header-icon">🛣️</span>
    <div>
      <div class="header-title">Road Damage &amp; Pothole Detection</div>
      <div class="header-subtitle">Real-Time Computer Vision &amp; Hazard Intelligence</div>
    </div>
  </div>
  <div class="status-pill">● System Active</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#   CONTROLS BAR
# ══════════════════════════════════════════════════════════════════════════════

if model is None:
    st.error("⚠️ Model file (best.pt) not found! Ensure best.pt is located in the project root directory.")

ctrl_col1, ctrl_col2 = st.columns([1.8, 1])
with ctrl_col1:
    mode = st.radio(
        "Select Inspection Mode:",
        ["📹 Live Camera (WebRTC)", "📱 Mobile Snapshot", "📸 Image Upload", "🎬 Video Upload"],
        horizontal=True
    )
with ctrl_col2:
    confidence = st.slider("🎯 Detection Confidence Threshold", 0.10, 1.00, 0.25, 0.05, format="%.2f")

# Severity Legend
st.markdown("""
<div class="sev-legend-wrap">
  <span class="sev-item"><span style="color:#22c55e;font-size:1.1rem;">■</span> <strong style="color:#ffffff;">Minor Damage</strong></span>
  <span class="sev-item"><span style="color:#f59e0b;font-size:1.1rem;">■</span> <strong style="color:#ffffff;">Moderate Hazard</strong></span>
  <span class="sev-item"><span style="color:#ef4444;font-size:1.1rem;">■</span> <strong style="color:#ffffff;">Severe Hazard</strong></span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#   MODE 1: IMAGE DETECTION
# ══════════════════════════════════════════════════════════════════════════════

if "Image" in mode:
    uploaded = st.file_uploader("Upload Road Photo (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.markdown('<p class="stCaption">📷 Processed Road View</p>', unsafe_allow_html=True)
        frame_ph = st.empty()
        if not uploaded:
            frame_ph.markdown(_EMPTY_IMG_HTML, unsafe_allow_html=True)
    with right:
        st.markdown('<p class="stCaption">📊 Live Road Diagnosis</p>', unsafe_allow_html=True)
        dash_ph = st.empty()
        if st.session_state.last_analysis is None:
            render_dashboard(_IDLE, ph=dash_ph)
        else:
            render_dashboard(st.session_state.last_analysis, ph=dash_ph)

    if uploaded and model:
        if st.session_state.get("last_img_name") != uploaded.name:
            st.session_state.last_analysis = None
            st.session_state.last_img_name = uploaded.name

        raw  = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        img  = cv2.imdecode(raw, cv2.IMREAD_COLOR)
        h, w = img.shape[:2]
        if w > 1100:
            img = cv2.resize(img, (1100, int(h * 1100 / w)))
            h, w = img.shape[:2]

        with st.spinner("Analyzing road defects..."):
            t0      = time.time()
            results = model.predict(img, conf=confidence, verbose=False)
            elapsed = time.time() - t0
        fps_val = 1.0 / max(elapsed, 1e-4)

        detections = yolo_boxes_to_detections(results[0].boxes, h, w)
        analysis   = run_analysis(detections)

        annotated = draw_boxes(img, analysis, fps_val, confidence)

        with frame_ph.container():
            st.image(annotated, channels="BGR", use_container_width=True)
            st.markdown(
                f'<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;">'
                f'<span class="fps-tag">⚡ {fps_val:.1f} FPS</span>'
                f'<span class="fps-tag">⏱ {elapsed*1000:.0f} ms</span>'
                f'<span class="fps-tag">🎯 Conf: {confidence:.2f}</span>'
                f'</div>', unsafe_allow_html=True)

        render_dashboard(analysis, ph=dash_ph)
        st.session_state.last_frame    = annotated
        st.session_state.last_analysis = analysis
        play_alert(analysis.condition)


# ══════════════════════════════════════════════════════════════════════════════
#   MODE 2: VIDEO DETECTION
# ══════════════════════════════════════════════════════════════════════════════

elif "Video" in mode:
    vid_up = st.file_uploader("Upload Dashcam Video (MP4, AVI, MOV)", type=["mp4", "avi", "mov"])

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.markdown('<p class="stCaption">🎬 Video Feed Output</p>', unsafe_allow_html=True)
        frame_ph = st.empty()
        perf_ph  = st.empty()
        if not vid_up:
            frame_ph.markdown(_EMPTY_VID_HTML, unsafe_allow_html=True)
    with right:
        st.markdown('<p class="stCaption">📊 Real-Time Road Diagnosis</p>', unsafe_allow_html=True)
        dash_ph = st.empty()
        if st.session_state.last_analysis is not None:
            render_dashboard(st.session_state.last_analysis, ph=dash_ph)
        else:
            render_dashboard(_IDLE, ph=dash_ph)

    if vid_up and model:
        vid_key  = getattr(vid_up, "file_id", f"{vid_up.name}_{vid_up.size}")
        new_file = (st.session_state.get("last_vid_key") != vid_key)
        if new_file:
            st.session_state.vid_bytes           = vid_up.read()
            st.session_state.last_vid_key        = vid_key
            st.session_state.last_vid_name       = vid_up.name
            st.session_state.last_analysis       = None
            st.session_state.prev_condition      = None
            st.session_state.vid_processed       = False
            st.session_state.vid_stopped_by_user = False
            render_dashboard(_IDLE, ph=dash_ph)

        stop_col, _ = st.columns([1, 2])
        with stop_col:
            stop_video = st.button("⏹ Stop Processing", key="stop_vid")

        if stop_video:
            st.session_state.vid_stopped_by_user = True

        if not st.session_state.get("vid_processed", False):
            vid_bytes = st.session_state.get("vid_bytes", b"")
            if not vid_bytes:
                st.error("Unable to read video file.")
                st.stop()

            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(vid_bytes)
            tfile.close()
            cap = cv2.VideoCapture(tfile.name)

            while cap.isOpened():
                if st.session_state.get("vid_stopped_by_user", False):
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                h, w = frame.shape[:2]
                if w > 1100:
                    frame = cv2.resize(frame, (1100, int(h * 1100 / w)))
                    h, w  = frame.shape[:2]

                t0      = time.time()
                results = model.predict(frame, conf=confidence, verbose=False)
                fps_val = 1.0 / max(time.time() - t0, 1e-4)

                frame_dets     = yolo_boxes_to_detections(results[0].boxes, h, w)
                frame_analysis = run_analysis(frame_dets)

                annotated = draw_boxes(frame, frame_analysis, fps_val, confidence)

                frame_ph.image(annotated, channels="BGR", use_container_width=True)
                perf_ph.markdown(
                    f'<div style="display:flex;gap:8px;margin-top:6px;flex-wrap:wrap;">'
                    f'<span class="fps-tag">⚡ {fps_val:.1f} FPS</span>'
                    f'<span class="fps-tag">🎯 Conf: {confidence:.2f}</span>'
                    f'</div>', unsafe_allow_html=True)

                render_dashboard(frame_analysis, ph=dash_ph)
                play_alert(frame_analysis.condition)
                st.session_state.last_frame = annotated

            cap.release()
            try:
                os.unlink(tfile.name)
            except Exception:
                pass

            st.session_state.vid_processed = True
            st.session_state.last_analysis = _IDLE
            render_dashboard(_IDLE, ph=dash_ph)

            status_msg = "Stopped by user." if st.session_state.get("vid_stopped_by_user") else "✔ Video processing complete."
            st.success(status_msg)


# ══════════════════════════════════════════════════════════════════════════════
#   MODE 3: REAL-TIME LIVE CAMERA (WEBRTC FOR MOBILE & DESKTOP ON CLOUD)
# ══════════════════════════════════════════════════════════════════════════════

elif "Live" in mode:
    st.markdown(
        '<p style="color:#cbd5e1;font-size:0.88rem;font-weight:600;margin-bottom:8px;">'
        '⚡ Point your camera at the road. Live detections & safety grading stream at real-time FPS directly in your browser:'
        '</p>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.markdown('<p class="stCaption">📹 Live Camera Feed (WebRTC)</p>', unsafe_allow_html=True)
        if HAS_WEBRTC:
            webrtc_ctx = webrtc_streamer(
                key="pothole-live-stream",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIGURATION,
                video_processor_factory=PotholeVideoProcessor,
                media_stream_constraints={
                    "video": {
                        "facingMode": {"ideal": "environment"},
                        "width": {"ideal": 640, "max": 640},
                        "height": {"ideal": 480, "max": 480},
                        "frameRate": {"ideal": 24, "max": 30},
                    },
                    "audio": False,
                },
                sendback_audio=False,
                media_toggle_controls=False,
                video_receiver_size=1,
                async_processing=True,
            )
            if webrtc_ctx.video_processor:
                webrtc_ctx.video_processor.confidence = confidence
        else:
            st.warning("⚠️ WebRTC module not available. Install `streamlit-webrtc` to enable live streaming.")
            btn_c1, btn_c2 = st.columns([1, 1])
            with btn_c1:
                if st.button("▶ Start Local OpenCV Webcam", key="start_wc_local"):
                    st.session_state.run_webcam    = True
                    st.session_state.last_analysis = None
            with btn_c2:
                if st.button("⏹ Stop Local OpenCV Webcam", key="stop_wc_local"):
                    st.session_state.run_webcam = False

    with right:
        st.markdown('<p class="stCaption">📊 Real-Time Road Diagnosis</p>', unsafe_allow_html=True)
        dash_ph = st.empty()
        if HAS_WEBRTC and webrtc_ctx and webrtc_ctx.state.playing and webrtc_ctx.video_processor and webrtc_ctx.video_processor.last_analysis:
            render_dashboard(webrtc_ctx.video_processor.last_analysis, ph=dash_ph)
        else:
            render_dashboard(_IDLE, ph=dash_ph)

        st.markdown(
            '<div style="background:#141926;border:1px solid #28334d;border-radius:10px;padding:12px 14px;margin-top:12px;font-size:0.82rem;color:#94a3b8;line-height:1.5;">'
            '💡 <strong>Real-Time Stream Active:</strong> Real-time bounding boxes, hazard classification, FPS counter, and road assessment HUD are rendered directly onto the camera feed at 30 FPS.'
            '</div>',
            unsafe_allow_html=True
        )

    # Local OpenCV webcam fallback (only used if running offline without WebRTC)
    if not HAS_WEBRTC and st.session_state.run_webcam and model:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("❌ Camera could not be opened. Check webcam connection and permissions.")
        else:
            while st.session_state.run_webcam:
                ret, frame = cap.read()
                if not ret:
                    break
                h, w = frame.shape[:2]
                if w > 1100:
                    frame = cv2.resize(frame, (1100, int(h * 1100 / w)))
                    h, w  = frame.shape[:2]

                t0      = time.time()
                results = model.predict(frame, conf=confidence, verbose=False)
                fps_val = 1.0 / max(time.time() - t0, 1e-4)

                frame_dets     = yolo_boxes_to_detections(results[0].boxes, h, w)
                frame_analysis = run_analysis(frame_dets)

                annotated = draw_boxes(frame, frame_analysis, fps_val, confidence)

                frame_ph.image(annotated, channels="BGR", use_container_width=True)
                render_dashboard(frame_analysis, ph=dash_ph)
                play_alert(frame_analysis.condition)
                st.session_state.last_frame = annotated

            cap.release()
            st.session_state.last_analysis = _IDLE
            render_dashboard(_IDLE, ph=dash_ph)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#   MODE 4: MOBILE SNAPSHOT (HIGH-RES PHOTO CAPTURE)
# ══════════════════════════════════════════════════════════════════════════════

elif "Snapshot" in mode or "Mobile" in mode:
    st.markdown('<p style="color:#cbd5e1;font-size:0.88rem;font-weight:600;margin-bottom:8px;">Capture a high-resolution photo of road damage from your device camera:</p>', unsafe_allow_html=True)
    cam_picture = st.camera_input("Road Camera Capture", key="mobile_cam_snap")

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.markdown('<p class="stCaption">📷 Live Camera Processed View</p>', unsafe_allow_html=True)
        frame_ph = st.empty()
        if not cam_picture:
            frame_ph.markdown(_EMPTY_PHONE_HTML, unsafe_allow_html=True)
    with right:
        st.markdown('<p class="stCaption">📊 Real-Time Road Diagnosis</p>', unsafe_allow_html=True)
        dash_ph = st.empty()
        if st.session_state.last_analysis is None:
            render_dashboard(_IDLE, ph=dash_ph)
        else:
            render_dashboard(st.session_state.last_analysis, ph=dash_ph)

    if cam_picture and model:
        raw  = np.asarray(bytearray(cam_picture.read()), dtype=np.uint8)
        img  = cv2.imdecode(raw, cv2.IMREAD_COLOR)
        h, w = img.shape[:2]
        if w > 1100:
            img = cv2.resize(img, (1100, int(h * 1100 / w)))
            h, w = img.shape[:2]

        with st.spinner("Analyzing camera capture..."):
            t0      = time.time()
            results = model.predict(img, conf=confidence, verbose=False)
            elapsed = time.time() - t0
        fps_val = 1.0 / max(elapsed, 1e-4)

        detections = yolo_boxes_to_detections(results[0].boxes, h, w)
        analysis   = run_analysis(detections)

        annotated = draw_boxes(img, analysis, fps_val, confidence)

        with frame_ph.container():
            st.image(annotated, channels="BGR", use_container_width=True)
            st.markdown(
                f'<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;">'
                f'<span class="fps-tag">⚡ {fps_val:.1f} FPS</span>'
                f'<span class="fps-tag">⏱ {elapsed*1000:.0f} ms</span>'
                f'<span class="fps-tag">🎯 Conf: {confidence:.2f}</span>'
                f'</div>', unsafe_allow_html=True)

        render_dashboard(analysis, ph=dash_ph)
        st.session_state.last_frame    = annotated
        st.session_state.last_analysis = analysis
        play_alert(analysis.condition)


# ══════════════════════════════════════════════════════════════════════════════
#   MINIMAL CLEAN FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin-top:3.5rem;padding-top:1.5rem;border-top:1px solid #1f2738;text-align:center;font-size:0.8rem;color:#94a3b8;font-weight:600;">
  🛣️ AI Road Damage &amp; Pothole Detection System &nbsp;·&nbsp; Powered by YOLOv8 &amp; Streamlit
</div>
""", unsafe_allow_html=True)
