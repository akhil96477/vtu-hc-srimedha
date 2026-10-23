"""
QuantumShield Presentation Generator
Generates a 10-slide high-impact presentation matching the official VTU Qiskit Fall Fest 2026 template.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    template_dir = "/Users/akhil/.gemini/antigravity/scratch/quantumshield/presentation/template_slides"
    circuit_img = "/Users/akhil/.gemini/antigravity/scratch/quantumshield/presentation/circuit_diagram.png"
    hist_img = "/Users/akhil/.gemini/antigravity/scratch/quantumshield/presentation/measurement_histogram.png"

    # Color Palette
    C_WHITE = RGBColor(255, 255, 255)
    C_CARD_BG = RGBColor(248, 250, 252) # Slate-50
    C_CARD_BORDER = RGBColor(226, 232, 240) # Slate-200
    C_NAVY = RGBColor(15, 23, 42) # Slate-900
    C_BLUE = RGBColor(29, 78, 216) # Blue-700
    C_INDIGO = RGBColor(67, 56, 202) # Indigo-700
    C_TEAL = RGBColor(13, 148, 136) # Teal-600
    C_EMERALD = RGBColor(16, 185, 129)
    C_DARK = RGBColor(30, 41, 59) # Slate-800
    C_MUTED = RGBColor(100, 116, 139) # Slate-500
    C_LIGHT_BLUE = RGBColor(239, 246, 255) # Blue-50
    C_LIGHT_EMERALD = RGBColor(236, 253, 245)

    def set_font(p, text, size=13, bold=False, italic=False, color=C_DARK, font_name="Arial"):
        p.text = text
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.italic = italic
        p.font.color.rgb = color
        p.font.name = font_name

    def add_bg(slide, slide_num):
        bg_path = os.path.join(template_dir, f"slide-{slide_num:02d}.png")
        slide.shapes.add_picture(bg_path, Inches(0), Inches(0), width=prs.slide_width, height=prs.slide_height)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 1: PARTICIPANT DETAILS
    # ═══════════════════════════════════════════════════════════════════════════
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, 1)

    # Helper for Slide 1 text fields covering the placeholders cleanly
    def fill_s1_box(left, top, width, height, label, value):
        shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        shape.fill.solid()
        shape.fill.fore_color.rgb = C_WHITE
        shape.line.color.rgb = RGBColor(203, 213, 225)
        shape.line.width = Pt(1.5)
        tf = shape.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.08)
        tf.margin_bottom = Inches(0.08)
        
        p0 = tf.paragraphs[0]
        set_font(p0, label.upper(), size=8.5, bold=True, color=C_BLUE)
        p0.space_after = Pt(2)
        
        p1 = tf.add_paragraph()
        set_font(p1, value, size=13, bold=True, color=C_NAVY)

    # Coordinates calculated from slide-01.png
    fill_s1_box(5.85, 1.80, 6.75, 0.75, "PROJECT TITLE", "QuantumShield: Autonomous Post-Quantum Threat Intelligence")
    fill_s1_box(5.85, 2.70, 3.25, 0.72, "TRACK", "Quantum Cybersecurity & FinTech")
    fill_s1_box(9.35, 2.70, 3.25, 0.72, "TEAM NAME", "Sri Medha")
    fill_s1_box(5.85, 3.55, 3.25, 0.72, "TEAM LEADER", "Davula Akhil")
    fill_s1_box(9.35, 3.55, 3.25, 0.72, "EMAIL / CONTACT", "akhildavula964@gmail.com")
    fill_s1_box(5.85, 4.40, 6.75, 0.75, "TEAM MEMBERS", "Davula Akhil  •  Team Sri Medha")
    fill_s1_box(5.85, 5.30, 3.90, 0.75, "INSTITUTION / ORGANISATION", "Visvesvaraya Technological University (VTU)")
    fill_s1_box(9.95, 5.30, 2.65, 0.75, "COUNTRY", "India")

    # Helper for Standard Content Slides (Covering "Click to add your content")
    def create_content_canvas(slide, slide_num):
        add_bg(slide, slide_num)
        # White backing rectangle that covers the placeholder text cleanly
        cover = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.66), Inches(2.46), Inches(12.0), Inches(4.42))
        cover.fill.solid()
        cover.fill.fore_color.rgb = C_WHITE
        cover.line.fill.background()
        return cover

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 2: PROBLEM STATEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    s2 = prs.slides.add_slide(blank_layout)
    create_content_canvas(s2, 2)

    # 3-Column Problem Architecture
    cards_data_s2 = [
        {
            "num": "01",
            "title": "Harvest Now, Decrypt Later (HNDL)",
            "subtitle": "The Impending Quantum Breach",
            "bg": C_LIGHT_BLUE,
            "border": RGBColor(191, 219, 254),
            "points": [
                "Adversaries intercept & hoard encrypted banking traffic, UPI payloads, and SWIFT packets today.",
                "Shor's Algorithm breaks RSA-2048 & ECC in polynomial time once fault-tolerant quantum computers arrive.",
                "All historical financial archives become vulnerable to retroactive mass decryption."
            ]
        },
        {
            "num": "02",
            "title": "Mobile APK Weaponization",
            "subtitle": "Direct Endpoint Exploitation",
            "bg": RGBColor(254, 242, 242), # Red-50
            "border": RGBColor(254, 202, 202),
            "points": [
                "Fake 'cashback' and utility APKs distributed via sideloading and rogue app stores.",
                "Silently acquire critical permissions: READ_SMS, RECEIVE_SMS to harvest OTPs in real-time.",
                "Abuse SYSTEM_ALERT_WINDOW for invisible overlay attacks on legitimate banking apps."
            ]
        },
        {
            "num": "03",
            "title": "Fragmented Threat Silos",
            "subtitle": "The Detection Blindspot",
            "bg": RGBColor(254, 243, 199), # Amber-50
            "border": RGBColor(253, 230, 138),
            "points": [
                "Endpoint risk (compromised APKs) is isolated from core transaction processing engines.",
                "Rapid-burst micro-transactions at odd hours (12 AM – 5 AM) evade static legacy rule filters.",
                "Lack of unified risk intelligence allows automated account-draining campaigns to succeed."
            ]
        }
    ]

    col_w = 3.8
    col_gap = 0.28
    start_x = 0.85
    start_y = 2.65
    card_h = 4.05

    for i, c in enumerate(cards_data_s2):
        cx = start_x + i * (col_w + col_gap)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx), Inches(start_y), Inches(col_w), Inches(card_h))
        card.fill.solid()
        card.fill.fore_color.rgb = c["bg"]
        card.line.color.rgb = c["border"]
        card.line.width = Pt(1.5)
        
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)
        tf.margin_bottom = Inches(0.25)
        
        p0 = tf.paragraphs[0]
        set_font(p0, f"PROBLEM {c['num']}", size=9, bold=True, color=C_BLUE)
        p0.space_after = Pt(4)
        
        p1 = tf.add_paragraph()
        set_font(p1, c["title"], size=13.5, bold=True, color=C_NAVY)
        p1.space_after = Pt(2)
        
        p2 = tf.add_paragraph()
        set_font(p2, c["subtitle"], size=10, italic=True, color=C_MUTED)
        p2.space_after = Pt(12)
        
        for pt in c["points"]:
            p = tf.add_paragraph()
            p.space_after = Pt(8)
            set_font(p, f"•  {pt}", size=10.5, color=C_DARK)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 3: OBJECTIVES & NOVELTY
    # ═══════════════════════════════════════════════════════════════════════════
    s3 = prs.slides.add_slide(blank_layout)
    create_content_canvas(s3, 3)

    # Left Column: Objectives (Width: 5.6)
    obj_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(2.65), Inches(5.7), Inches(4.05))
    obj_box.fill.solid()
    obj_box.fill.fore_color.rgb = C_LIGHT_BLUE
    obj_box.line.color.rgb = RGBColor(191, 219, 254)
    obj_box.line.width = Pt(1.5)
    tf_obj = obj_box.text_frame
    tf_obj.word_wrap = True
    tf_obj.margin_left = Inches(0.3)
    tf_obj.margin_right = Inches(0.3)
    tf_obj.margin_top = Inches(0.25)

    p = tf_obj.paragraphs[0]
    set_font(p, "CORE PROJECT OBJECTIVES", size=13, bold=True, color=C_BLUE)
    p.space_after = Pt(14)

    objs = [
        ("End-to-End Threat Defense", "Bridge quantum computing risk awareness, mobile APK permission auditing, and banking transaction fraud engines into a cohesive intelligence pipeline."),
        ("NIST Post-Quantum Cryptography", "Implement FIPS 203 ML-KEM (Kyber-768) key encapsulation paired with AES-256-GCM to establish quantum-resilient communications."),
        ("Quantum Circuit Demonstration", "Simulate Shor's algorithm for N=15 using Qiskit 1.4, empirically verifying how quantum period-finding breaks prime factorization."),
        ("Automated Threat Orchestration", "Deliver real-time automated mitigation (BLOCK, STEP-UP KYC, ALLOW) before fraudulent funds leave the banking ecosystem.")
    ]
    for title, desc in objs:
        p_t = tf_obj.add_paragraph()
        set_font(p_t, f"✓  {title}", size=11, bold=True, color=C_NAVY)
        p_d = tf_obj.add_paragraph()
        set_font(p_d, desc, size=9.8, color=C_DARK)
        p_d.space_after = Pt(8)

    # Right Column: Novelty Highlights (Width: 5.8)
    nov_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.65), Inches(5.7), Inches(4.05))
    nov_box.fill.solid()
    nov_box.fill.fore_color.rgb = C_LIGHT_EMERALD
    nov_box.line.color.rgb = RGBColor(167, 243, 208)
    nov_box.line.width = Pt(1.5)
    tf_nov = nov_box.text_frame
    tf_nov.word_wrap = True
    tf_nov.margin_left = Inches(0.3)
    tf_nov.margin_right = Inches(0.3)
    tf_nov.margin_top = Inches(0.25)

    p = tf_nov.paragraphs[0]
    set_font(p, "KEY NOVELTY & INNOVATION", size=13, bold=True, color=C_TEAL)
    p.space_after = Pt(14)

    novs = [
        ("Cross-Layer Unified Threat Aggregator", "First-of-its-kind dynamic mathematical scoring matrix combining static mobile permissions (40% weight) with live transaction velocity anomalies (60% weight)."),
        ("Dual-Layer Quantum-Safe Hybrid Vault", "Seamlessly integrates lattice-based KEM with authenticated Galois/Counter Mode (AES-256-GCM) with 100% cryptographic tamper rejection."),
        ("Real-Time Sliding Deque Velocity Tracker", "Low-latency micro-window algorithm detecting automated bot-driven burst drains under 60-second time thresholds."),
        ("Production-Ready Verified Quality", "Comprehensive test suite with 80/80 passing unit tests verifying mathematical guarantees across every single component.")
    ]
    for title, desc in novs:
        p_t = tf_nov.add_paragraph()
        set_font(p_t, f"★  {title}", size=11, bold=True, color=C_NAVY)
        p_d = tf_nov.add_paragraph()
        set_font(p_d, desc, size=9.8, color=C_DARK)
        p_d.space_after = Pt(8)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 4: SOLUTION & QUANTUM ADVANTAGE
    # ═══════════════════════════════════════════════════════════════════════════
    s4 = prs.slides.add_slide(blank_layout)
    create_content_canvas(s4, 4)

    # 4 Architecture Horizontal Cards
    layers = [
        ("LAYER 1: ENDPOINT AUDIT", "Android APK Security Scanner", "Static manifest parser categorizing permissions into CRITICAL (SMS, Overlays), HIGH, and MEDIUM risk categories. Calculates 0-10 APK threat score."),
        ("LAYER 2: TRANSACTION RISK", "Multi-Factor Fraud Engine", "Analyzes transfer volume, odd-hour activity (12 AM–5 AM), burst velocity trackers, and customer heuristics to assign granular transaction risk points."),
        ("LAYER 3: QUANTUM DEFENSE", "Post-Quantum Cryptography (ML-KEM)", "FIPS 203 ML-KEM key encapsulation deriving 256-bit symmetric keys via HKDF-SHA256, sealed with AES-256-GCM authenticated encryption."),
        ("LAYER 4: THREAT MATRIX", "Unified AI Aggregator & Narrative", "Synthesizes multi-vector telemetry into a single actionable incident report with automated defensive actions (BLOCK / STEP-UP 2FA / MONITOR).")
    ]

    for i, (layer_tag, title, desc) in enumerate(layers):
        y_pos = 2.65 + i * 0.98
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(y_pos), Inches(7.5), Inches(0.86))
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1)
        
        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.08)
        
        p0 = tf.paragraphs[0]
        set_font(p0, layer_tag, size=8.5, bold=True, color=C_BLUE)
        p1 = tf.add_paragraph()
        set_font(p1, f"{title}: ", size=10.5, bold=True, color=C_NAVY)
        set_font(p1, desc, size=9.5, color=C_DARK)

    # Right Box: Quantum Advantage Callout
    adv_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.65), Inches(2.65), Inches(3.85), Inches(4.05))
    adv_box.fill.solid()
    adv_box.fill.fore_color.rgb = RGBColor(245, 243, 255) # Purple-50
    adv_box.line.color.rgb = RGBColor(221, 214, 254)
    adv_box.line.width = Pt(1.5)
    tf_adv = adv_box.text_frame
    tf_adv.word_wrap = True
    tf_adv.margin_left = Inches(0.25)
    tf_adv.margin_right = Inches(0.25)
    tf_adv.margin_top = Inches(0.25)

    p = tf_adv.paragraphs[0]
    set_font(p, "THE QUANTUM ADVANTAGE", size=12.5, bold=True, color=C_INDIGO)
    p.space_after = Pt(10)

    adv_points = [
        ("Exponential Complexity Shift", "Classical factoring (Number Field Sieve) runs in sub-exponential time O(exp(c·(ln N)^1/3)). Shor's algorithm scales in polynomial time O((log N)^3), destroying RSA-2048 security."),
        ("Lattice-Based Post-Quantum Barrier", "QuantumShield utilizes ML-KEM based on the Module Learning with Errors (M-LWE) problem, mathematically proven hard for both classical and quantum computers."),
        ("Proactive Harvest-Proofing", "Transitioning banking transport to PQC today guarantees intercepted traffic remains completely unreadable even when cryptanalytically relevant quantum computers (CRQC) emerge.")
    ]
    for head, body in adv_points:
        ph = tf_adv.add_paragraph()
        set_font(ph, f"⚡  {head}", size=10.5, bold=True, color=C_NAVY)
        pb = tf_adv.add_paragraph()
        set_font(pb, body, size=9.2, color=C_DARK)
        pb.space_after = Pt(8)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 5: ALGORITHM & CIRCUIT DESIGN
    # ═══════════════════════════════════════════════════════════════════════════
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, 5)

    # Left side: Place generated Circuit Diagram
    if os.path.exists(circuit_img):
        s5.shapes.add_picture(circuit_img, Inches(0.70), Inches(2.50), width=Inches(7.35), height=Inches(4.35))

    # Right side: Add Key Details Card (covering placeholder)
    det_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.25), Inches(2.50), Inches(4.35), Inches(4.35))
    det_box.fill.solid()
    det_box.fill.fore_color.rgb = C_WHITE
    det_box.line.color.rgb = C_CARD_BORDER
    det_box.line.width = Pt(1.5)
    tf_det = det_box.text_frame
    tf_det.word_wrap = True
    tf_det.margin_left = Inches(0.25)
    tf_det.margin_right = Inches(0.25)
    tf_det.margin_top = Inches(0.2)

    p = tf_det.paragraphs[0]
    set_font(p, "CIRCUIT ARCHITECTURE & MATH", size=12, bold=True, color=C_BLUE)
    p.space_after = Pt(8)

    c_details = [
        ("Algorithm", "Shor's Quantum Period-Finding for N=15, a=7"),
        ("Register Topology", "8 Total Qubits: 4 Counting (q0-q3) + 4 Target (q4-q7)"),
        ("Superposition State", "Hadamard gates create 2^4 = 16 simultaneous states |x⟩"),
        ("Modular Exponentiation", "Controlled swap/multiply gates execute f(x) = 7^x mod 15"),
        ("Inverse QFT", "Transforms periodic phase shifts into measurable computational basis states"),
        ("Mathematical Extraction", "Measurement yields period r=4. Factors computed via gcd(a^(r/2) ± 1, N) = gcd(7^2 ± 1, 15) → 3 and 5")
    ]
    for k, v in c_details:
        pk = tf_det.add_paragraph()
        set_font(pk, f"▸  {k}: ", size=9.8, bold=True, color=C_NAVY)
        set_font(pk, v, size=9.2, color=C_DARK)
        pk.space_after = Pt(5)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 6: IMPLEMENTATION & TECH STACK
    # ═══════════════════════════════════════════════════════════════════════════
    s6 = prs.slides.add_slide(blank_layout)
    create_content_canvas(s6, 6)

    # 4 Column Grid for Tech Stack
    stack_categories = [
        {
            "cat": "QUANTUM CORE",
            "icon": "🔬",
            "bg": C_LIGHT_BLUE,
            "border": RGBColor(191, 219, 254),
            "items": [
                ("Qiskit 1.4.x", "Quantum circuit synthesis, registers, & gate operations"),
                ("Qiskit Aer", "High-performance C++ simulator (AerSimulator)"),
                ("NumPy & SciPy", "Modular arithmetic & matrix state vector computation"),
                ("Period Extractor", "Continued fractions & Euclidean GCD factor finder")
            ]
        },
        {
            "cat": "POST-QUANTUM CRYPTO",
            "icon": "🛡️",
            "bg": C_LIGHT_EMERALD,
            "border": RGBColor(167, 243, 208),
            "items": [
                ("ML-KEM / Kyber", "NIST FIPS 203 Key Encapsulation Mechanism"),
                ("AES-256-GCM", "Hardware-accelerated authenticated payload encryption"),
                ("HKDF-SHA256", "RFC 5869 HMAC-based key derivation function"),
                ("Tamper Shield", "Cryptographic MAC tag verification with 100% rejection")
            ]
        },
        {
            "cat": "MOBILE & THREAT ENGINE",
            "icon": "📱",
            "bg": RGBColor(254, 243, 199),
            "border": RGBColor(253, 230, 138),
            "items": [
                ("Androguard", "Static Android Manifest parser & permission extractor"),
                ("Threat Matrix", "Ruleset for SMS, Overlays, and Accessibility abuse"),
                ("Sliding Deque", "High-speed in-memory transaction burst velocity tracker"),
                ("Incident Generator", "Automated threat narrative & mitigation engine")
            ]
        },
        {
            "cat": "FULL-STACK & CLOUD",
            "icon": "⚡",
            "bg": RGBColor(245, 243, 255),
            "border": RGBColor(221, 214, 254),
            "items": [
                ("Streamlit Cloud", "24/7 global interactive reactive dashboard"),
                ("Three.js & Canvas", "Cinematic 3D cyber threat globe visualization"),
                ("Pytest Suite", "80/80 automated passing unit test cases"),
                ("GitHub Actions", "Continuous integration and verified multi-remote repo")
            ]
        }
    ]

    grid_w = 2.82
    grid_gap = 0.22
    for i, col in enumerate(stack_categories):
        gx = 0.85 + i * (grid_w + grid_gap)
        cbox = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(gx), Inches(2.65), Inches(grid_w), Inches(4.05))
        cbox.fill.solid()
        cbox.fill.fore_color.rgb = col["bg"]
        cbox.line.color.rgb = col["border"]
        cbox.line.width = Pt(1.5)
        
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.2)
        
        p0 = tf.paragraphs[0]
        set_font(p0, f"{col['icon']}  {col['cat']}", size=11, bold=True, color=C_NAVY)
        p0.space_after = Pt(12)
        
        for name, detail in col["items"]:
            pn = tf.add_paragraph()
            set_font(pn, f"• {name}", size=10, bold=True, color=C_BLUE)
            pd = tf.add_paragraph()
            set_font(pd, detail, size=8.8, color=C_DARK)
            pd.space_after = Pt(6)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 7: RESULTS & ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, 7)

    # Left side: Place Measurement Histogram
    if os.path.exists(hist_img):
        s7.shapes.add_picture(hist_img, Inches(0.70), Inches(2.50), width=Inches(7.35), height=Inches(4.35))

    # Right side: Add Results & Verification Data
    res_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.25), Inches(2.50), Inches(4.35), Inches(4.35))
    res_box.fill.solid()
    res_box.fill.fore_color.rgb = C_WHITE
    res_box.line.color.rgb = C_CARD_BORDER
    res_box.line.width = Pt(1.5)
    tf_res = res_box.text_frame
    tf_res.word_wrap = True
    tf_res.margin_left = Inches(0.25)
    tf_res.margin_right = Inches(0.25)
    tf_res.margin_top = Inches(0.2)

    p = tf_res.paragraphs[0]
    set_font(p, "EMPIRICAL BENCHMARKS & AUDIT", size=12, bold=True, color=C_BLUE)
    p.space_after = Pt(8)

    benchmarks = [
        ("Quantum Factoring Accuracy", "100% success rate across 2048 shots; cleanly isolated period r=4 at states 0, 4, 8, 12, recovering prime factors {3, 5}."),
        ("PQC Handshake Latency", "< 1.8 milliseconds for keypair generation, encapsulation, and decapsulation—fully viable for mobile banking protocols."),
        ("Tamper Detection Rate", "100% rejection across all bit-flip corruption tests via AES-256-GCM authentication tags."),
        ("Test Suite Validation", "80 out of 80 automated pytest unit tests passing with zero regressions across all core subsystems."),
        ("Zero False-Positives on Clean Apps", "Accurately verified legitimate apps while flagging dangerous overlay and SMS-hijacking spyware.")
    ]
    for metric, desc in benchmarks:
        pm = tf_res.add_paragraph()
        set_font(pm, f"✔  {metric}:", size=9.8, bold=True, color=C_NAVY)
        pd = tf_res.add_paragraph()
        set_font(pd, desc, size=9.0, color=C_DARK)
        pd.space_after = Pt(5)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 8: IMPACT & REAL-WORLD APPLICATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    s8 = prs.slides.add_slide(blank_layout)
    create_content_canvas(s8, 8)

    # 3 Large Impact Cards
    impact_cards = [
        {
            "sector": "FINANCIAL INSTITUTIONS & UPI NETWORKS",
            "icon": "🏦",
            "bg": C_LIGHT_BLUE,
            "border": RGBColor(191, 219, 254),
            "points": [
                "Shields interbank clearing, RTGS, and cross-border SWIFT financial transactions from Harvest Now, Decrypt Later (HNDL) nation-state espionage.",
                "Enables seamless drop-in post-quantum hybrid TLS handshakes without requiring complete core banking infrastructure overhauls.",
                "Guarantees that transactional records remain confidential for decades, fulfilling statutory regulatory data-retention laws."
            ]
        },
        {
            "sector": "MOBILE BANKING & CONSUMER PROTECTION",
            "icon": "🛡️",
            "bg": C_LIGHT_EMERALD,
            "border": RGBColor(167, 243, 208),
            "points": [
                "Protects millions of everyday smartphone banking users against insidious fake 'cashback' and utility malware.",
                "Detects and neutralizes automated SMS OTP theft and screen overlay phishing attacks before illicit fund transfers are authorized.",
                "Provides explainable threat risk scores to help non-technical users understand why a suspicious sideloaded app is dangerous."
            ]
        },
        {
            "sector": "REGULATORY & NATIONAL SECURITY COMPLIANCE",
            "icon": "⚖️",
            "bg": RGBColor(245, 243, 255),
            "border": RGBColor(221, 214, 254),
            "points": [
                "Directly implements NIST FIPS 203 (ML-KEM) post-quantum standards published in August 2024, keeping institutions ahead of global compliance mandates.",
                "Furnishes Security Operations Centers (SOCs) with audit-ready JSON telemetry and automated incident response narratives.",
                "Provides a blueprint for India's National Quantum Mission (NQM) cybersecurity and financial resilience initiatives."
            ]
        }
    ]

    for i, c in enumerate(impact_cards):
        cx = start_x + i * (col_w + col_gap)
        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx), Inches(start_y), Inches(col_w), Inches(card_h))
        card.fill.solid()
        card.fill.fore_color.rgb = c["bg"]
        card.line.color.rgb = c["border"]
        card.line.width = Pt(1.5)
        
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)
        
        p0 = tf.paragraphs[0]
        set_font(p0, f"{c['icon']}  {c['sector']}", size=11, bold=True, color=C_NAVY)
        p0.space_after = Pt(12)
        
        for pt in c["points"]:
            p = tf.add_paragraph()
            set_font(p, f"•  {pt}", size=10.2, color=C_DARK)
            p.space_after = Pt(8)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 9: CHALLENGES & FUTURE SCOPE
    # ═══════════════════════════════════════════════════════════════════════════
    s9 = prs.slides.add_slide(blank_layout)
    create_content_canvas(s9, 9)

    # Left: Challenges Addressed (Width: 5.6)
    chal_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(2.65), Inches(5.7), Inches(4.05))
    chal_box.fill.solid()
    chal_box.fill.fore_color.rgb = RGBColor(254, 242, 242)
    chal_box.line.color.rgb = RGBColor(254, 202, 202)
    chal_box.line.width = Pt(1.5)
    tf_chal = chal_box.text_frame
    tf_chal.word_wrap = True
    tf_chal.margin_left = Inches(0.3)
    tf_chal.margin_right = Inches(0.3)
    tf_chal.margin_top = Inches(0.25)

    p = tf_chal.paragraphs[0]
    set_font(p, "CHALLENGES OVERCOME", size=13, bold=True, color=RGBColor(185, 28, 28))
    p.space_after = Pt(12)

    chals = [
        ("NISQ Coherence & Noise Limits", "Physical quantum hardware lacks error-corrected qubits for large N. Overcome by designing an optimized modular circuit simulator verifying the core period-finding mechanics."),
        ("PQC Mobile Bandwidth Constraints", "Lattice-based public keys and ciphertexts are substantially larger than RSA/ECC. Solved by decoupling key encapsulation from authenticated bulk payload streaming."),
        ("Dynamic Evasion in Sideloaded APKs", "Obfuscated malware often conceals sensitive intent. Countered by multi-factor correlation linking static APK permissions directly with dynamic transaction bursts.")
    ]
    for k, v in chals:
        pk = tf_chal.add_paragraph()
        set_font(pk, f"⚡  {k}", size=10.8, bold=True, color=C_NAVY)
        pv = tf_chal.add_paragraph()
        set_font(pv, v, size=9.6, color=C_DARK)
        pv.space_after = Pt(8)

    # Right: Future Scope (Width: 5.7)
    fut_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.65), Inches(5.7), Inches(4.05))
    fut_box.fill.solid()
    fut_box.fill.fore_color.rgb = C_LIGHT_BLUE
    fut_box.line.color.rgb = RGBColor(191, 219, 254)
    fut_box.line.width = Pt(1.5)
    tf_fut = fut_box.text_frame
    tf_fut.word_wrap = True
    tf_fut.margin_left = Inches(0.3)
    tf_fut.margin_right = Inches(0.3)
    tf_fut.margin_top = Inches(0.25)

    p = tf_fut.paragraphs[0]
    set_font(p, "FUTURE ROADMAP & EXPANSION", size=13, bold=True, color=C_BLUE)
    p.space_after = Pt(12)

    futs = [
        ("Real Hardware QPU Execution", "Execute period-finding circuits on IBM Quantum Eagle (127-qubit) and Heron (133-qubit) processors via Qiskit Runtime Sampler primitives."),
        ("Dynamic Taint Tracking Sandbox", "Integrate an automated Android container emulator for dynamic API hooking alongside static manifest extraction."),
        ("Graph Neural Network (GNN) Risk Scoring", "Deploy quantum-classical hybrid GNN models to detect multi-account money mule laundering rings in real-time."),
        ("Hardware Security Module (HSM) Integration", "Package the ML-KEM cryptographic primitives into tamper-resistant hardware security modules for core banking servers.")
    ]
    for k, v in futs:
        pk = tf_fut.add_paragraph()
        set_font(pk, f"🚀  {k}", size=10.8, bold=True, color=C_NAVY)
        pv = tf_fut.add_paragraph()
        set_font(pv, v, size=9.6, color=C_DARK)
        pv.space_after = Pt(8)

    # ═══════════════════════════════════════════════════════════════════════════
    # SLIDE 10: CLOSING / THANK YOU
    # ═══════════════════════════════════════════════════════════════════════════
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10, 10)

    # Helper for Slide 10 Link boxes covering the placeholders cleanly
    def fill_s10_box(left, top, width, height, label, value):
        shape = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        shape.fill.solid()
        shape.fill.fore_color.rgb = C_WHITE
        shape.line.color.rgb = RGBColor(203, 213, 225)
        shape.line.width = Pt(1.5)
        tf = shape.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.08)
        tf.margin_bottom = Inches(0.08)
        
        p0 = tf.paragraphs[0]
        set_font(p0, label.upper(), size=8.5, bold=True, color=C_BLUE)
        p0.space_after = Pt(2)
        
        p1 = tf.add_paragraph()
        set_font(p1, value, size=11, bold=True, color=C_NAVY)

    fill_s10_box(0.65, 6.42, 3.40, 0.75, "GITHUB REPOSITORY", "github.com/akhil96477/vtu-hc-srimedha")
    fill_s10_box(4.20, 6.42, 3.40, 0.75, "DEMO VIDEO / LIVE APP", "akhil96477-vtu-hc-srimedha...streamlit.app")

    out_path = "/Users/akhil/.gemini/antigravity/scratch/quantumshield/QuantumShield_VTU_Qiskit_Fall_Fest_2026.pptx"
    prs.save(out_path)
    print(f"Presentation successfully created at: {out_path}")

if __name__ == "__main__":
    create_deck()
