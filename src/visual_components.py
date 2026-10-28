"""
QuantumShield — Visual Component Library
High-end SVG and WebGL visual components for the Davula Akhil design system:
1. Animated SVG Threat Dial Gauge (0.0 to 10.0 risk elevation)
2. Interactive WebGL Three.js 3D Quantum Threat Sphere
3. NIST FIPS 203 ML-KEM-768 Visual Cryptographic Pipeline
4. High-Fidelity 8-Qubit Qiskit Shor Factoring Circuit Architecture
"""

from __future__ import annotations
import math


def render_threat_dial_gauge(score: float, level: str = "CRITICAL", action: str = "BLOCK & ENFORCE ML-KEM") -> str:
    """
    Renders an animated high-contrast SVG Cyber Threat Dial Gauge.
    Score: 0.0 to 10.0.
    """
    clamped_score = max(0.0, min(10.0, float(score)))
    # Map score 0-10 to angle 180° to 0° (left to right)
    pct = clamped_score / 10.0
    angle_deg = 180.0 - (pct * 180.0)
    angle_rad = math.radians(angle_deg)
    
    # Needle coordinates (Center at 200, 170, needle length 110)
    cx, cy, r = 200, 170, 115
    nx = cx + r * math.cos(angle_rad)
    ny = cy - r * math.sin(angle_rad)

    # Risk styling
    if clamped_score >= 8.0:
        theme_color = "#f85149"  # Crimson
        glow_color = "rgba(248, 81, 73, 0.4)"
        status_text = "SEVERE RISK"
    elif clamped_score >= 6.0:
        theme_color = "#f0883e"  # Amber
        glow_color = "rgba(240, 136, 62, 0.4)"
        status_text = "HIGH RISK"
    elif clamped_score >= 3.5:
        theme_color = "#e3b341"  # Yellow
        glow_color = "rgba(227, 179, 65, 0.4)"
        status_text = "ELEVATED"
    else:
        theme_color = "#3fb950"  # Green
        glow_color = "rgba(63, 185, 80, 0.4)"
        status_text = "SECURE / NOMINAL"

    svg = f"""
    <div style="width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px 0;">
        <svg viewBox="0 0 400 230" width="100%" style="max-width: 440px; overflow: visible;">
            <defs>
                <filter id="dial-glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="8" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <filter id="needle-glow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="4" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <linearGradient id="gauge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#3fb950" />
                    <stop offset="35%" stop-color="#e3b341" />
                    <stop offset="70%" stop-color="#f0883e" />
                    <stop offset="100%" stop-color="#f85149" />
                </linearGradient>
            </defs>

            <!-- Background Track Arc -->
            <path d="M 60 170 A 140 140 0 0 1 340 170" fill="none" stroke="#161b22" stroke-width="18" stroke-linecap="round" />
            
            <!-- Grid Tick Marks -->
            <path d="M 60 170 A 140 140 0 0 1 340 170" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="18" stroke-dasharray="2 18" stroke-linecap="butt" />

            <!-- Colored Segment Arc (Active Portion) -->
            <path d="M 60 170 A 140 140 0 0 1 340 170" fill="none" stroke="url(#gauge-grad)" stroke-width="12" stroke-linecap="round" filter="url(#dial-glow)" opacity="0.85" />

            <!-- Danger Zone Highlight Arc -->
            <path d="M 298 71 A 140 140 0 0 1 340 170" fill="none" stroke="#f85149" stroke-width="14" stroke-linecap="round" opacity="0.6" />

            <!-- Center Digital Readout Box -->
            <rect x="135" y="105" width="130" height="60" rx="12" fill="#0d1117" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
            <text x="200" y="138" font-family="'Syne', 'Space Grotesk', sans-serif" font-size="34" font-weight="800" fill="#fafafa" text-anchor="middle" letter-spacing="-1">{clamped_score:.1f}</text>
            <text x="200" y="156" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="{theme_color}" text-anchor="middle" letter-spacing="1.5">{status_text}</text>

            <!-- Radial Needle -->
            <line x1="200" y1="170" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{theme_color}" stroke-width="3.5" stroke-linecap="round" filter="url(#needle-glow)" />
            
            <!-- Needle Pivot Rings -->
            <circle cx="200" cy="170" r="14" fill="#07080a" stroke="{theme_color}" stroke-width="3" />
            <circle cx="200" cy="170" r="6" fill="{theme_color}" filter="url(#needle-glow)" />

            <!-- Scale Labels -->
            <text x="50" y="196" font-family="'JetBrains Mono', monospace" font-size="11" fill="#7d8590" text-anchor="middle">0.0</text>
            <text x="200" y="24" font-family="'JetBrains Mono', monospace" font-size="11" fill="#7d8590" text-anchor="middle">5.0</text>
            <text x="350" y="196" font-family="'JetBrains Mono', monospace" font-size="11" fill="#f85149" text-anchor="middle">10.0</text>
            <text x="200" y="205" font-family="'JetBrains Mono', monospace" font-size="10" fill="#8b949e" text-anchor="middle" letter-spacing="2">SYNTHESIS RISK INDEX</text>
        </svg>
    </div>
    """
    return svg


def render_3d_threat_sphere(height: int = 320) -> str:
    """
    Renders an interactive Three.js 3D Quantum Threat Sphere.
    Displays a rotating wireframe cyber sphere with glowing particles,
    pulsing attack arcs, and real-time interactive rotation controls.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background-color: transparent;
                font-family: 'JetBrains Mono', monospace;
            }}
            #container {{
                position: relative;
                width: 100%;
                height: {height}px;
                background: radial-gradient(circle at center, #0e1217 0%, #07080a 80%);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 18px;
                overflow: hidden;
            }}
            #hud-overlay {{
                position: absolute;
                top: 14px;
                left: 18px;
                pointer-events: none;
                z-index: 10;
            }}
            .hud-tag {{
                font-size: 10px;
                letter-spacing: 2px;
                color: #c8ff00;
                text-transform: uppercase;
                margin-bottom: 4px;
                font-weight: 700;
            }}
            .hud-title {{
                font-family: 'Space Grotesk', -apple-system, sans-serif;
                font-size: 14px;
                color: #ffffff;
                font-weight: 700;
            }}
            #hud-telemetry {{
                position: absolute;
                bottom: 14px;
                right: 18px;
                pointer-events: none;
                z-index: 10;
                text-align: right;
                font-size: 10px;
                color: #7d8590;
                line-height: 1.5;
            }}
            .hud-stat {{
                color: #c8ff00;
                font-weight: 700;
            }}
            .pulse-dot {{
                display: inline-block;
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #c8ff00;
                box-shadow: 0 0 8px #c8ff00;
                margin-right: 4px;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="hud-overlay">
                <div class="hud-tag"><span class="pulse-dot"></span>QUANTUM RADAR // ACTIVE TELEMETRY</div>
                <div class="hud-title">3D Attack Vector & PQC Shield Topology</div>
            </div>
            <div id="hud-telemetry">
                <div>SURFACE NODES: <span class="hud-stat">128 Q-NODES</span></div>
                <div>LATTICE ENCRYPTION: <span class="hud-stat">ML-KEM-768</span></div>
                <div>SHOR TAMPER RESISTANCE: <span class="hud-stat">100% IMMUNE</span></div>
            </div>
        </div>

        <script>
            const container = document.getElementById('container');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.z = 240;

            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            container.appendChild(renderer.domElement);

            // Group for rotation
            const globeGroup = new THREE.Group();
            scene.add(globeGroup);

            // 1. Wireframe Outer Sphere
            const sphereGeo = new THREE.SphereGeometry(75, 24, 24);
            const sphereMat = new THREE.MeshBasicMaterial({{
                color: 0x1e2638,
                wireframe: true,
                transparent: true,
                opacity: 0.35
            }});
            const wireSphere = new THREE.Mesh(sphereGeo, sphereMat);
            globeGroup.add(wireSphere);

            // 2. Glowing Nodes (Points)
            const count = 300;
            const posArray = new Float32Array(count * 3);
            for(let i = 0; i < count; i++) {{
                const u = Math.random();
                const v = Math.random();
                const theta = u * 2.0 * Math.PI;
                const phi = Math.acos(2.0 * v - 1.0);
                const r = 75 + (Math.random() * 4 - 2);
                posArray[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                posArray[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                posArray[i * 3 + 2] = r * Math.cos(phi);
            }}
            const pointsGeo = new THREE.BufferGeometry();
            pointsGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
            const pointsMat = new THREE.PointsMaterial({{
                size: 2.8,
                color: 0xc8ff00,
                transparent: true,
                opacity: 0.75
            }});
            const particleSystem = new THREE.Points(pointsGeo, pointsMat);
            globeGroup.add(particleSystem);

            // 3. Orbiting Quantum Ring (Tilted)
            const ringGeo = new THREE.RingGeometry(96, 98, 64);
            const ringMat = new THREE.MeshBasicMaterial({{
                color: 0x00d2ff,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.5
            }});
            const ringMesh = new THREE.Mesh(ringGeo, ringMat);
            ringMesh.rotation.x = Math.PI / 2.8;
            ringMesh.rotation.y = Math.PI / 6;
            globeGroup.add(ringMesh);

            // 4. Attack Vector Arc (Hostile APK -> Core Banking)
            const p1 = new THREE.Vector3(-55, 30, 45); // Endpoint Red
            const p2 = new THREE.Vector3(55, -20, 45); // Banking Green
            const mid = new THREE.Vector3(0, 50, 75);  // Arc peak

            const curve = new THREE.QuadraticBezierCurve3(p1, mid, p2);
            const curvePoints = curve.getPoints(50);
            const curveGeo = new THREE.BufferGeometry().setFromPoints(curvePoints);
            const curveMat = new THREE.LineBasicMaterial({{ color: 0xf85149, linewidth: 2 }});
            const arcLine = new THREE.Line(curveGeo, curveMat);
            globeGroup.add(arcLine);

            // Hostile Node Marker
            const hostileGeo = new THREE.SphereGeometry(3.5, 16, 16);
            const hostileMat = new THREE.MeshBasicMaterial({{ color: 0xf85149 }});
            const hostileNode = new THREE.Mesh(hostileGeo, hostileMat);
            hostileNode.position.copy(p1);
            globeGroup.add(hostileNode);

            // Safe Banking Node Marker
            const safeGeo = new THREE.SphereGeometry(4, 16, 16);
            const safeMat = new THREE.MeshBasicMaterial({{ color: 0x3fb950 }});
            const safeNode = new THREE.Mesh(safeGeo, safeMat);
            safeNode.position.copy(p2);
            globeGroup.add(safeNode);

            // Interactive Drag
            let isDragging = false;
            let prevMouseX = 0;
            let prevMouseY = 0;

            container.addEventListener('mousedown', (e) => {{
                isDragging = true;
                prevMouseX = e.clientX;
                prevMouseY = e.clientY;
            }});

            window.addEventListener('mouseup', () => {{ isDragging = false; }});

            container.addEventListener('mousemove', (e) => {{
                if (isDragging) {{
                    const deltaX = e.clientX - prevMouseX;
                    const deltaY = e.clientY - prevMouseY;
                    globeGroup.rotation.y += deltaX * 0.007;
                    globeGroup.rotation.x += deltaY * 0.007;
                    prevMouseX = e.clientX;
                    prevMouseY = e.clientY;
                }}
            }});

            // Animation Loop
            let clock = new THREE.Clock();
            function animate() {{
                requestAnimationFrame(animate);
                const delta = clock.getDelta();
                if (!isDragging) {{
                    globeGroup.rotation.y += 0.004;
                    globeGroup.rotation.x += 0.001;
                }}
                ringMesh.rotation.z += 0.006;
                renderer.render(scene, camera);
            }}
            animate();

            // Resize Observer
            window.addEventListener('resize', () => {{
                if (container.clientWidth > 0 && container.clientHeight > 0) {{
                    camera.aspect = container.clientWidth / container.clientHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(container.clientWidth, container.clientHeight);
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html


def render_pqc_pipeline_diagram() -> str:
    """
    Renders an interactive SVG architectural flow diagram of the
    NIST FIPS 203 ML-KEM-768 + AES-256-GCM Cryptographic Pipeline.
    """
    svg = """
    <div style="width: 100%; overflow-x: auto; padding: 12px 0;">
        <svg viewBox="0 0 960 220" width="100%" style="min-width: 800px; display: block; margin: 0 auto;">
            <defs>
                <filter id="box-glow" x="-10%" y="-10%" width="120%" height="120%">
                    <feGaussianBlur stdDeviation="6" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <linearGradient id="pqc-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#161b22" />
                    <stop offset="100%" stop-color="#0d1117" />
                </linearGradient>
                <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 8 5 L 0 9 z" fill="#c8ff00" />
                </marker>
                <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 8 5 L 0 9 z" fill="#58a6ff" />
                </marker>
            </defs>

            <!-- Step 1: Client Node -->
            <g transform="translate(10, 20)">
                <rect width="210" height="170" rx="14" fill="url(#pqc-grad)" stroke="rgba(255,255,255,0.12)" stroke-width="1.5" />
                <rect x="0" y="0" width="210" height="4" rx="2" fill="#58a6ff" />
                <text x="16" y="32" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#58a6ff" letter-spacing="1">STAGE 01 // CLIENT</text>
                <text x="16" y="56" font-family="'Space Grotesk', sans-serif" font-size="15" font-weight="700" fill="#ffffff">Android Mobile App</text>
                <text x="16" y="80" font-family="'JetBrains Mono', monospace" font-size="11" fill="#8b949e">• KeyGen() via M-LWE</text>
                <text x="16" y="100" font-family="'JetBrains Mono', monospace" font-size="11" fill="#8b949e">• Lattice Matrix (k=3)</text>
                
                <rect x="16" y="118" width="178" height="36" rx="6" fill="#1c2128" stroke="rgba(88, 166, 255, 0.3)" />
                <text x="24" y="134" font-family="'JetBrains Mono', monospace" font-size="10" fill="#58a6ff">PUBLIC KEY (ek)</text>
                <text x="24" y="148" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#ffffff">1,184 Bytes</text>
            </g>

            <!-- Arrow 1 -> 2 -->
            <path d="M 230 105 L 285 105" fill="none" stroke="#58a6ff" stroke-width="2" stroke-dasharray="4 4" marker-end="url(#arrow-blue)" />

            <!-- Step 2: Encapsulation Engine -->
            <g transform="translate(295, 20)">
                <rect width="250" height="170" rx="14" fill="url(#pqc-grad)" stroke="#238636" stroke-width="1.5" filter="url(#box-glow)" opacity="0.95" />
                <rect x="0" y="0" width="250" height="4" rx="2" fill="#3fb950" />
                <text x="16" y="32" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#3fb950" letter-spacing="1">STAGE 02 // NIST FIPS 203</text>
                <text x="16" y="56" font-family="'Space Grotesk', sans-serif" font-size="15" font-weight="700" fill="#ffffff">ML-KEM-768 Encaps</text>
                <text x="16" y="80" font-family="'JetBrains Mono', monospace" font-size="11" fill="#8b949e">• (ct, ss) = Encaps(ek)</text>
                <text x="16" y="100" font-family="'JetBrains Mono', monospace" font-size="11" fill="#8b949e">• Derives 256-bit SS</text>

                <rect x="16" y="118" width="218" height="36" rx="6" fill="#1c2128" stroke="rgba(63, 185, 80, 0.4)" />
                <text x="24" y="134" font-family="'JetBrains Mono', monospace" font-size="10" fill="#3fb950">CIPHERTEXT (ct)</text>
                <text x="24" y="148" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#ffffff">1,088 Bytes (Lattice Proof)</text>
            </g>

            <!-- Arrow 2 -> 3 -->
            <path d="M 555 105 L 610 105" fill="none" stroke="#c8ff00" stroke-width="2" marker-end="url(#arrow)" />

            <!-- Step 3: Server Vault & Symmetric Encryption -->
            <g transform="translate(620, 20)">
                <rect width="325" height="170" rx="14" fill="url(#pqc-grad)" stroke="#c8ff00" stroke-width="1.5" />
                <rect x="0" y="0" width="325" height="4" rx="2" fill="#c8ff00" />
                <text x="16" y="32" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#c8ff00" letter-spacing="1">STAGE 03 // CORE VAULT</text>
                <text x="16" y="56" font-family="'Space Grotesk', sans-serif" font-size="15" font-weight="700" fill="#ffffff">AES-256-GCM Session Tunnel</text>
                <text x="16" y="80" font-family="'JetBrains Mono', monospace" font-size="11" fill="#8b949e">• Decaps(ct, dk) → 256-bit Shared Secret</text>
                <text x="16" y="100" font-family="'JetBrains Mono', monospace" font-size="11" fill="#8b949e">• Authenticated Encryption + 128-bit MAC Tag</text>

                <rect x="16" y="118" width="293" height="36" rx="6" fill="#1c2128" stroke="rgba(200, 255, 0, 0.3)" />
                <text x="24" y="134" font-family="'JetBrains Mono', monospace" font-size="10" fill="#c8ff00">HNDL IMMUNITY</text>
                <text x="24" y="148" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#ffffff">0% Shor Factoring Vulnerability</text>
            </g>
        </svg>
    </div>
    """
    return svg


def render_quantum_circuit_schematic(base: int = 7, composite_n: int = 15) -> str:
    """
    Renders an SVG schematic representing the 8-qubit Shor Factoring Circuit
    (4 counting qubits + 4 target qubits + modular exponentiation + QFT†).
    """
    svg = f"""
    <div style="width: 100%; overflow-x: auto; padding: 12px 0;">
        <svg viewBox="0 0 940 280" width="100%" style="min-width: 820px; display: block; margin: 0 auto; background: #0c1017; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;">
            <defs>
                <filter id="gate-glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>

            <!-- Circuit Header -->
            <text x="24" y="28" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#c8ff00" letter-spacing="1.5">
                QISKIT RUNTIME CIRCUIT // SHOR ORDER-FINDING (N={composite_n}, a={base})
            </text>
            <text x="750" y="28" font-family="'JetBrains Mono', monospace" font-size="11" fill="#7d8590">
                8 QUBITS · LEVEL-3 DEPTH
            </text>

            <!-- Wires -->
            <!-- Counting Register Qubits: q0, q1, q2, q3 -->
            <g transform="translate(0, 20)">
                <!-- q0 -->
                <text x="24" y="52" font-family="'JetBrains Mono', monospace" font-size="12" fill="#58a6ff">|q₀⟩</text>
                <line x1="60" y1="48" x2="880" y2="48" stroke="#30363d" stroke-width="2" />
                <!-- q1 -->
                <text x="24" y="87" font-family="'JetBrains Mono', monospace" font-size="12" fill="#58a6ff">|q₁⟩</text>
                <line x1="60" y1="83" x2="880" y2="83" stroke="#30363d" stroke-width="2" />
                <!-- q2 -->
                <text x="24" y="122" font-family="'JetBrains Mono', monospace" font-size="12" fill="#58a6ff">|q₂⟩</text>
                <line x1="60" y1="118" x2="880" y2="118" stroke="#30363d" stroke-width="2" />
                <!-- q3 -->
                <text x="24" y="157" font-family="'JetBrains Mono', monospace" font-size="12" fill="#58a6ff">|q₃⟩</text>
                <line x1="60" y1="153" x2="880" y2="153" stroke="#30363d" stroke-width="2" />

                <!-- Divider -->
                <line x1="60" y1="175" x2="880" y2="175" stroke="#21262d" stroke-width="1" stroke-dasharray="6 4" />

                <!-- Target Register Qubits: q4..q7 (Auxiliary) -->
                <text x="24" y="202" font-family="'JetBrains Mono', monospace" font-size="12" fill="#7ee787">|aux⟩</text>
                <line x1="60" y1="198" x2="880" y2="198" stroke="#30363d" stroke-width="3" />
                <text x="65" y="215" font-family="'JetBrains Mono', monospace" font-size="10" fill="#7d8590">4-Qubit Ancilla Register (|1⟩)</text>

                <!-- Gate Stage 1: Hadamard Gates on Counting Register -->
                <g transform="translate(100, 33)">
                    <rect width="28" height="28" rx="5" fill="#1f6feb" stroke="#58a6ff" />
                    <text x="14" y="19" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="#fff" text-anchor="middle">H</text>
                </g>
                <g transform="translate(100, 68)">
                    <rect width="28" height="28" rx="5" fill="#1f6feb" stroke="#58a6ff" />
                    <text x="14" y="19" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="#fff" text-anchor="middle">H</text>
                </g>
                <g transform="translate(100, 103)">
                    <rect width="28" height="28" rx="5" fill="#1f6feb" stroke="#58a6ff" />
                    <text x="14" y="19" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="#fff" text-anchor="middle">H</text>
                </g>
                <g transform="translate(100, 138)">
                    <rect width="28" height="28" rx="5" fill="#1f6feb" stroke="#58a6ff" />
                    <text x="14" y="19" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="#fff" text-anchor="middle">H</text>
                </g>

                <!-- Gate Stage 2: Controlled Modular Exponentiation Unitaries U^(a^(2^j) mod 15) -->
                <!-- U1 from q0 -->
                <circle cx="190" cy="48" r="4.5" fill="#c8ff00" />
                <line x1="190" y1="48" x2="190" y2="198" stroke="#c8ff00" stroke-width="1.5" />
                <rect x="165" y="186" width="50" height="24" rx="4" fill="#238636" stroke="#3fb950" />
                <text x="190" y="202" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">U^{base}¹</text>

                <!-- U2 from q1 -->
                <circle cx="280" cy="83" r="4.5" fill="#c8ff00" />
                <line x1="280" y1="83" x2="280" y2="198" stroke="#c8ff00" stroke-width="1.5" />
                <rect x="255" y="186" width="50" height="24" rx="4" fill="#238636" stroke="#3fb950" />
                <text x="280" y="202" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">U^{base}²</text>

                <!-- U4 from q2 -->
                <circle cx="370" cy="118" r="4.5" fill="#c8ff00" />
                <line x1="370" y1="118" x2="370" y2="198" stroke="#c8ff00" stroke-width="1.5" />
                <rect x="345" y="186" width="50" height="24" rx="4" fill="#238636" stroke="#3fb950" />
                <text x="370" y="202" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">U^{base}⁴</text>

                <!-- U8 from q3 -->
                <circle cx="460" cy="153" r="4.5" fill="#c8ff00" />
                <line x1="460" y1="153" x2="460" y2="198" stroke="#c8ff00" stroke-width="1.5" />
                <rect x="435" y="186" width="50" height="24" rx="4" fill="#238636" stroke="#3fb950" />
                <text x="460" y="202" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">U^{base}⁸</text>

                <!-- Gate Stage 3: 4-Qubit Inverse Quantum Fourier Transform (QFT†) Block -->
                <g transform="translate(540, 35)">
                    <rect width="130" height="135" rx="8" fill="#5b21b6" stroke="#a855f7" stroke-width="1.5" filter="url(#gate-glow)" />
                    <text x="65" y="65" font-family="'Syne', sans-serif" font-size="20" font-weight="800" fill="#ffffff" text-anchor="middle">QFT †</text>
                    <text x="65" y="85" font-family="'JetBrains Mono', monospace" font-size="10" fill="#e9d5ff" text-anchor="middle">4-Qubit Inverse</text>
                    <text x="65" y="105" font-family="'JetBrains Mono', monospace" font-size="9" fill="#c084fc" text-anchor="middle">Phase Extractor</text>
                </g>

                <!-- Gate Stage 4: Measurement Meters -->
                <g transform="translate(730, 36)">
                    <rect width="36" height="24" rx="4" fill="#161b22" stroke="#8b949e" />
                    <path d="M 7 17 A 11 11 0 0 1 29 17 M 18 17 L 26 8" stroke="#f0883e" stroke-width="1.5" fill="none" />
                </g>
                <g transform="translate(730, 71)">
                    <rect width="36" height="24" rx="4" fill="#161b22" stroke="#8b949e" />
                    <path d="M 7 17 A 11 11 0 0 1 29 17 M 18 17 L 26 8" stroke="#f0883e" stroke-width="1.5" fill="none" />
                </g>
                <g transform="translate(730, 106)">
                    <rect width="36" height="24" rx="4" fill="#161b22" stroke="#8b949e" />
                    <path d="M 7 17 A 11 11 0 0 1 29 17 M 18 17 L 26 8" stroke="#f0883e" stroke-width="1.5" fill="none" />
                </g>
                <g transform="translate(730, 141)">
                    <rect width="36" height="24" rx="4" fill="#161b22" stroke="#8b949e" />
                    <path d="M 7 17 A 11 11 0 0 1 29 17 M 18 17 L 26 8" stroke="#f0883e" stroke-width="1.5" fill="none" />
                </g>

                <!-- Classical Register Wire -->
                <line x1="775" y1="50" x2="850" y2="50" stroke="#f0883e" stroke-width="1.5" />
                <line x1="775" y1="85" x2="850" y2="85" stroke="#f0883e" stroke-width="1.5" />
                <line x1="775" y1="120" x2="850" y2="120" stroke="#f0883e" stroke-width="1.5" />
                <line x1="775" y1="155" x2="850" y2="155" stroke="#f0883e" stroke-width="1.5" />
                <text x="860" y="105" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#f0883e">c[4]</text>
            </g>
        </svg>
    </div>
    """
    return svg
