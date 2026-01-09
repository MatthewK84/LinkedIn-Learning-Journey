# Counter-UAS Interceptor Drone
## Technical Requirements Document
### High-Speed Kinetic/Capture

**Document Version:** 1.0  
**Target Unit Cost:** ≤ $22,000 USD (expendable interceptor)  
**Compliance:** NDAA Section 889 Compliant

---

## 1. Executive Summary

This document defines requirements for a high-speed counter-UAS (C-UAS) interceptor capable of autonomous target engagement at speeds up to 220 MPH (191 knots / 98 m/s). The platform is designed for rapid-response intercept of Group 1–2 adversarial drones in defended airspace.

**Capability Requirements:**

| Parameter | Interceptor|
|-----------|-------------|
| Maximum Speed | 191 knots (220 MPH) |
| Mission | Target neutralization |
| Endurance | 15–25 min (sprint capable) |
| Payload | Tracking sensor + defeat mechanism |
| Configuration | Flying wing or swept-wing |
| Recovery | Expendable or recoverable |
| Maneuverability | 8–12g instantaneous |

---

## 2. Mission Profile

### 2.1 Concept of Operations

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INTERCEPT MISSION PROFILE                            │
│                                                                         │
│  ALTITUDE                                                               │
│     ▲                                                                   │
│     │                         ┌──── INTERCEPT                           │
│ 2000'│                    ___/│     (220 MPH)                           │
│     │                ___/     │        ●════●                           │
│     │            ___/         │       /      \                          │
│ 1000'│       ___/  CLIMB      │      /   ▼    \ DEFEAT                  │
│     │   ___/     (Sprint)     │     / TARGET   \                        │
│     │  /                      │    /            \                       │
│  500'│ / LAUNCH               │   /              \ RTB (if reusable)    │
│     │/  (VTOL or Rail)        │  /                \___                  │
│     └───────────────────────────────────────────────────► TIME          │
│     0    30s    60s    90s   120s   150s                                │
│                                                                         │
│  DETECTION ──► TRACK ──► LAUNCH ──► INTERCEPT ──► DEFEAT ──► RTB/EXPEND│
│    (GCS)      (Radar)   (<30s)     (60-90s)      (Kinetic)              │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Mission Requirements

| Phase | Requirement |
|-------|-------------|
| Alert Posture | Ready to launch within 30 seconds |
| Launch | VTOL, pneumatic rail, or hand-launch capable |
| Climb | ≥ 3,000 ft/min to intercept altitude |
| Sprint | 220 MPH sustainable for ≥ 3 minutes |
| Intercept Geometry | Pursuit, head-on, or crossing engagement |
| Target Acquisition | Autonomous handoff from ground radar |
| Terminal Guidance | Onboard seeker (EO/IR or RF) |
| Defeat Mechanism | Kinetic, net capture, or proximity effect |
| Recovery | Expendable (primary) or parachute recovery |

### 2.3 Target Set

| Target Class | Size | Speed | Altitude |
|--------------|------|-------|----------|
| Group 1 sUAS | < 20 lbs | 0–60 knots | 0–1,200 ft AGL |
| Group 2 sUAS | 20–55 lbs | 0–150 knots | 0–3,500 ft AGL |
| Commercial Drones | 1–10 lbs | 0–45 knots | 0–400 ft AGL |
| FPV Attack Drones | 1–5 lbs | 60–100 knots | 0–500 ft AGL |
| Loitering Munitions | 10–40 lbs | 50–150 knots | 100–5,000 ft AGL |

---

## 3. Performance Requirements

### 3.1 Speed Performance

| Parameter | Threshold | Objective |
|-----------|-----------|-----------|
| Maximum Speed (level flight) | 191 knots (220 MPH) | 217 knots (250 MPH) |
| Cruise Speed | 130 knots | 150 knots |
| Loiter Speed | 60 knots | 50 knots |
| Time to Max Speed | ≤ 45 seconds | ≤ 30 seconds |
| Acceleration (0–191 kts) | — | 4.3 kts/s average |

### 3.2 Flight Envelope

| Parameter | Requirement |
|-----------|-------------|
| Service Ceiling | ≥ 10,000 ft MSL |
| Operating Altitude | 50–5,000 ft AGL |
| Maximum Dive Speed | 250 MPH (Vne) |
| Climb Rate (max power) | ≥ 4,000 ft/min |
| Climb Rate (cruise power) | ≥ 1,500 ft/min |

### 3.3 Maneuverability

| Parameter | Requirement | Notes |
|-----------|-------------|-------|
| Instantaneous Load Factor | +12g / -6g | Structural |
| Sustained Load Factor | +8g | At max speed |
| Roll Rate | ≥ 300°/s | At 150 knots |
| Maximum Bank Angle | 80° | Sustained turn |
| Turn Radius (at 191 kts, 8g) | ~380 ft | For pursuit geometry |

### 3.4 Endurance

| Profile | Endurance |
|---------|-----------|
| Sprint (220 MPH continuous) | ≥ 8 minutes |
| Mixed (cruise + sprint) | ≥ 15 minutes |
| Loiter (60 knots) | ≥ 25 minutes |
| Combat Radius | ≥ 8 km (sprint intercept) |
| Combat Radius | ≥ 15 km (cruise + sprint) |

---

## 4. Airframe Requirements

### 4.1 Configuration Trade Study

| Configuration | Pros | Cons | Suitability |
|---------------|------|------|-------------|
| **Flying Wing** | Low drag, simple structure, good for kinetic | Limited payload volume, pitch stability | ★★★★★ |
| **Swept Wing Conventional** | Proven high-speed design, stable | Higher drag than flying wing | ★★★★ |
| **Delta Wing** | High speed, high AoA capability | Complex controls, less efficient cruise | ★★★ |
| **Blended Wing Body** | Good payload volume, moderate drag | Complex manufacturing | ★★★ |
| **Quad-plane VTOL** | Vertical launch, hover | Too much drag at 220 MPH, weight penalty | ★ |

**Selected Configuration:** Flying Wing (Primary) or Swept-Wing Conventional (Alternate)

### 4.2 Flying Wing Design Parameters

| Parameter | Requirement |
|-----------|-------------|
| Wingspan | 1.2–1.5 m (4–5 ft) |
| Wing Area | 0.25–0.35 m² |
| Aspect Ratio | 5–7 |
| Sweep Angle | 25–35° (leading edge) |
| Airfoil | Reflexed (MH-45, MH-60, or custom) |
| Wing Loading | 15–25 kg/m² |
| Thickness Ratio | 10–12% (root), 8–10% (tip) |

### 4.3 Structural Requirements

| Parameter | Requirement | Notes |
|-----------|-------------|-------|
| Design Load Factor | +15g / -7.5g | 1.25× ultimate |
| Ultimate Load Factor | +18g / -9g | |
| Airframe Weight | ≤ 6 lbs (2.7 kg) | Structure only |
| All-Up Weight | 15–22 lbs (7–10 kg) | Mission dependent |
| Maximum Dynamic Pressure | 65 lb/ft² (at 250 MPH SL) | Vne condition |
| Material | Carbon fiber composite | High-modulus preferred |
| Impact Tolerance | Survive 50g deceleration | For kinetic intercept |

### 4.4 Aerodynamic Performance

| Parameter | Requirement |
|-----------|-------------|
| L/D (cruise, 130 kts) | ≥ 12 |
| L/D (sprint, 191 kts) | ≥ 8 |
| CD0 (zero-lift drag) | ≤ 0.025 |
| Oswald Efficiency | ≥ 0.85 |
| CLmax | ≥ 1.2 (for recovery maneuvers) |
| Stall Speed | ≤ 45 knots |

### 4.5 Launch and Recovery

| Method | Description | Trade-offs |
|--------|-------------|------------|
| **Pneumatic Rail** | Compressed air catapult, 0–60 knots in 3m | Fast response, ground equipment needed |
| **Bungee Launch** | Elastic cord, 0–40 knots | Simple, slower |
| **VTOL (Optional)** | Detachable quad motors | +3 lbs weight, flexible positioning |
| **Hand Launch** | Running throw | Limited to lighter configs |
| **Recovery** | Parachute (reusable) or expendable | Chute adds 0.5 lbs |

**Primary:** Pneumatic rail launcher (15-second ready-to-launch)  
**Alternate:** Detachable VTOL module for expeditionary ops

---

## 5. Propulsion System

### 5.1 Propulsion Trade Study

| System | Max Speed | Efficiency | Complexity | Cost | Suitability |
|--------|-----------|------------|------------|------|-------------|
| **EDF (Electric Ducted Fan)** | 220+ MPH | Moderate | Low | $$ | ★★★★★ |
| **High-KV Direct Drive** | 180 MPH | High at low speed | Low | $ | ★★★ |
| **Small Turbine (jet)** | 300+ MPH | Low | High | $$$$ | ★★ |
| **Hybrid (fuel + electric)** | 250 MPH | High | Very High | $$$$$ | ★ |

**Selected System:** Electric Ducted Fan (EDF)

### 5.2 EDF System Requirements

| Parameter | Requirement |
|-----------|-------------|
| Fan Diameter | 90–120 mm |
| Static Thrust | ≥ 6 kg (13.2 lbs) |
| Thrust at 191 kts | ≥ 2.5 kg (5.5 lbs) |
| Power Input | 4,000–6,000 W |
| RPM | 35,000–50,000 |
| Motor KV | 1,200–1,800 KV |
| Efficiency (static) | ≥ 55% |
| Efficiency (at speed) | ≥ 70% |

### 5.3 EDF Selection (NDAA Compliant)

| Option | Manufacturer | Origin | Specs | Cost | NDAA |
|--------|--------------|--------|-------|------|------|
| **Schübeler DS-94-DIA HST** | Schübeler | Germany | 94mm, 6.2kg thrust, 6.5kW | $850 | ✓ |
| **Schübeler DS-104-DIA HST** | Schübeler | Germany | 104mm, 8.5kg thrust, 8kW | $1,100 | ✓ |
| **Turbines RC Titan** | Turbines RC | USA | 90mm, custom wind | $600 | ✓ |
| **Wren Turbines MW54** | Wren | UK | Micro turbine, 12 lbs thrust | $4,500 | ✓ |
| Schübeler + Lehner Motor | Germany | Matched system | $1,200 | ✓ |

**Selected Hardware:**  
- **Schübeler DS-94-DIA HST** — Germany (NATO ally)
- **Motor:** Lehner 2280/5 or Hacker A60-18S (Germany)

| DS-94-DIA HST Specifications | Value |
|-----------------------------|-------|
| Fan Diameter | 94 mm |
| Static Thrust | 6.2 kg (13.6 lbs) |
| Thrust at 180 MPH | 2.8 kg (6.2 lbs) |
| Input Power | 6,500 W max |
| RPM | 47,000 |
| Weight (fan unit) | 380 g |
| Recommended Motor | Lehner 2280/5 |
| Cost (complete) | $1,200 |

### 5.4 ESC Requirements

| Parameter | Requirement |
|-----------|-------------|
| Continuous Current | ≥ 200A |
| Burst Current | ≥ 280A (10s) |
| Voltage | 12S (44.4V nominal) |
| BEC | Not required |
| Telemetry | RPM, current, temperature |
| Timing | High (22–30°) |
| PWM Frequency | ≥ 32 kHz |

**Selected Hardware:**  
- **YGE 205HVT** — Germany
- **Alternate:** Castle Creations Phoenix Edge 200HV — USA

| YGE 205HVT Specifications | Value |
|--------------------------|-------|
| Continuous Current | 205A |
| Voltage Range | 6S–14S |
| BEC | 8A switching |
| Telemetry | Full (Jeti, HoTT, S.Port) |
| Weight | 138 g |
| Cost | $380 |

---

## 6. Power System

### 6.1 Battery Requirements

| Parameter | Requirement |
|-----------|-------------|
| Chemistry | High-discharge LiPo |
| Configuration | 12S (44.4V nominal) |
| Capacity | ≥ 5,000 mAh |
| Discharge Rate | ≥ 75C continuous |
| Energy | ≥ 220 Wh |
| Weight | ≤ 1.5 kg |
| Cell Origin | US, Japan, South Korea, EU |

### 6.2 Power Budget

| Phase | Power Draw | Duration | Energy |
|-------|------------|----------|--------|
| Launch/Climb | 6,500 W | 45 s | 81 Wh |
| Sprint (220 MPH) | 5,500 W | 180 s | 275 Wh |
| Cruise (130 kt) | 2,000 W | 300 s | 167 Wh |
| Intercept Maneuver | 6,500 W | 30 s | 54 Wh |
| **Total (Sprint Mission)** | — | ~6 min | ~410 Wh |
| **Total (Mixed Mission)** | — | ~12 min | ~400 Wh |

**Conclusion:** Require 2× battery packs for adequate energy margin.

### 6.3 Battery Selection

**Selected Hardware:**  
- **MaxAmps 12S 5000mAh 150C** ×2 (parallel) — USA

| MaxAmps 12S 5000 Specifications | Value |
|--------------------------------|-------|
| Configuration | 12S1P |
| Capacity | 5,000 mAh |
| Discharge | 150C continuous |
| Energy | 222 Wh per pack |
| Weight | 1.15 kg per pack |
| Cost | $450 per pack |

**System Total:**  
- 2× packs in parallel = 10,000 mAh, 444 Wh
- Weight: 2.3 kg
- Cost: $900

---

## 7. Avionics and Guidance

### 7.1 Flight Controller

| Parameter | Requirement |
|-----------|-------------|
| Platform | ArduPilot (Plane) or custom |
| Loop Rate | ≥ 400 Hz |
| IMU | Triple-redundant, ≥ 2000°/s gyro range |
| Barometer | Dual, static port isolated |
| Control Law | High-rate attitude control, intercept guidance |

**Hardware:**  
- **CubePilot Cube Orange+** with high-rate firmware
- **Alternate:** Custom STM32H7 for deterministic timing

### 7.2 Guidance System

| Mode | Algorithm | Requirement |
|------|-----------|-------------|
| Waypoint | Standard navigation | Cruise to patrol area |
| Pursuit | Pure pursuit or velocity pursuit | Tail-chase geometry |
| Lead Pursuit | Proportional navigation (PN) | Head-on/crossing |
| Terminal | Augmented PN (APN) | Final 500m to impact |
| Collision Avoidance | Abort/re-engage logic | If no-fire zone entered |

**Guidance Implementation:**  
- Proportional Navigation Constant (N): 3–5
- Update Rate: ≥ 50 Hz
- Line-of-Sight Rate Estimation: Kalman filter on seeker data

### 7.3 Target Tracking Sensor (Seeker)

| Parameter | Threshold | Objective |
|-----------|-----------|-----------|
| Type | EO (visible/NIR) | EO + SWIR or RF |
| Resolution | ≥ 1280×720 | ≥ 1920×1080 |
| Frame Rate | ≥ 60 fps | ≥ 120 fps |
| Field of View | ≥ 40° (acquisition) | 60° |
| Tracking FOV | ≥ 10° (narrow) | 15° |
| Detection Range | ≥ 1,000 m (Group 1 target) | ≥ 2,000 m |
| Track Accuracy | ≤ 1° | ≤ 0.5° |
| Processor | Onboard AI inference | |

**Selected Hardware:**  
- **Allied Vision Alvium 1800 U-1240** (USB3, global shutter) — Germany
- **Lens:** Tamron M118FM16 (16mm, 1/1.8") — Japan
- **Processor:** NVIDIA Jetson Orin Nano 8GB — USA

| Seeker System Specifications | Value |
|-----------------------------|-------|
| Sensor | Sony IMX226, 12 MP, global shutter |
| Frame Rate | 60 fps @ 4K, 120 fps @ 1080p |
| Interface | USB 3.1 Gen 1 |
| AI Inference | YOLO-based detection, 30 fps @ 1080p |
| Tracking | KCF/MOSSE + Kalman filter |
| Cost | $1,100 (camera + lens + compute) |

### 7.4 Additional Sensors

| Sensor | Purpose | Hardware | Cost |
|--------|---------|----------|------|
| GNSS | Navigation, target geolocation | u-blox ZED-F9P | $180 |
| Radar Altimeter | Low-altitude safety | Ainstein US-D1 | $350 |
| Airspeed | Flight envelope protection | MS4525DO (high-speed cal) | $80 |
| ADS-B In | Blue-force tracking | uAvionix pingRX | $300 |

---

## 8. Target Defeat Mechanisms

### 8.1 Defeat Mechanism Options

| Mechanism | Description | Pros | Cons | Pk |
|-----------|-------------|------|------|-----|
| **Kinetic (Ram)** | Direct airframe impact | Simple, no extra payload | Expendable, requires precision | 85–95% |
| **Warhead** | Fragmentation or blast | High Pk, standoff | ITAR, safety, cost | 95%+ |
| **Deployed Net** | Entanglement capture | Non-kinetic, recoverable | Added weight, range limited | 70–85% |
| **Directed Energy** | HPM or laser | Reusable, multi-shot | Power, size, cost | 60–80% |
| **Electronic Attack** | GPS/C2 jamming | Soft kill, reusable | Target may continue flight | 50–70% |

### 8.2 Recommended Configuration

**Primary: Kinetic Interceptor (Expendable)**
- Direct ram using hardened leading edge.
- Reinforced nose cone (aluminum or tungsten-filled).
- No warhead, no ITAR concerns.
- Lowest cost per engagement.
- Similar to Anduril Anvil concept.

**Secondary: Net Capture (Reusable)**
- Deployed net at 20–50m range.
- Entangles target rotors/props.
- Parachute recovery of interceptor.
- Higher unit cost, lower cost per engagement if recovered.

### 8.3 Kinetic Interceptor Specifications

| Parameter | Requirement |
|-----------|-------------|
| Impact Surface | Reinforced nose, ≥ 200 cm² |
| Material | Aluminum honeycomb + tungsten ballast |
| Closing Speed | Up to 350 MPH combined |
| Impact Energy | ≥ 5,000 J (sufficient for Group 1–2) |
| Miss Distance (for kill) | ≤ 0.5 m |
| Terminal Accuracy (CEP) | ≤ 0.3 m |

### 8.4 Net Capture System

| Parameter | Requirement |
|-----------|-------------|
| Net Size | 3m × 3m (deployed) |
| Net Material | Kevlar or Dyneema |
| Deployment Range | 20–50 m from target |
| Deployment Method | Pneumatic or spring-loaded |
| Weight Penalty | +1.5 lbs |
| Cost Penalty | +$800 |

---

## 9. Command, Control, and Communications

### 9.1 Datalink Requirements

| Parameter | Requirement |
|-----------|-------------|
| Range | ≥ 10 km LOS |
| Latency | ≤ 50 ms (for guidance updates) |
| Uplink Rate | ≥ 500 kbps (commands, target cues) |
| Downlink Rate | ≥ 5 Mbps (video, telemetry) |
| Encryption | AES-256 |
| Frequency | 2.4 GHz or 900 MHz |
| Lost Link | Autonomous continue/abort logic |

**Selected Hardware:**  
- **Doodle Labs RM-2450-2K** (compact variant) — USA
- Weight: 45g
- Cost: $1,000 (air unit only; ground unit shared with cueing system)

### 9.2 Integration with C-UAS System

| Interface | Protocol | Purpose |
|-----------|----------|---------|
| Target Cueing | ASTERIX Cat 048/062 or JSON API | Radar track handoff |
| Launch Command | MAVLink or custom | Fire authorization |
| Telemetry | MAVLink | Health, position, status |
| Video | RTP/H.264 | Seeker imagery |
| Kill Assessment | Automated (track loss) | BDA confirmation |

### 9.3 Ground-Based Cueing Radar

The interceptor requires external target cueing from a ground-based radar or EO system. Compatible systems:

| System | Manufacturer | Origin | Detection Range | Cost |
|--------|--------------|--------|-----------------|------|
| **Echodyne EchoGuard** | Echodyne | USA | 3+ km (sUAS) | $75,000 |
| **SpotterRF NX Series** | SpotterRF | USA | 1.5 km (sUAS) | $35,000 |
| **Blighter A800 3D** | Blighter | UK | 5+ km (sUAS) | $150,000 |
| **Robin Radar IRIS** | Robin Radar | Netherlands | 5+ km | $120,000 |

**Assumption:** Ground radar and C2 system are GFE (Government Furnished Equipment) and not included in per-unit interceptor cost.

---

## 10. Physical Specifications Summary

### 10.1 Interceptor Dimensions

| Parameter | Value |
|-----------|-------|
| Configuration | Flying wing |
| Wingspan | 1.4 m (55 in) |
| Length | 0.8 m (31 in) |
| Height | 0.2 m (8 in) |
| Wing Area | 0.30 m² |
| Aspect Ratio | 6.5 |
| Wing Loading | 30 kg/m² |

### 10.2 Weight Breakdown

| Component | Weight (kg) | Weight (lbs) |
|-----------|-------------|--------------|
| Airframe (composite) | 1.5 | 3.3 |
| EDF + ESC | 0.7 | 1.5 |
| Battery (2× 12S 5000) | 2.3 | 5.1 |
| Avionics (FC, GNSS, sensors) | 0.4 | 0.9 |
| Seeker system | 0.3 | 0.7 |
| Datalink | 0.1 | 0.2 |
| Kinetic nose / net system | 0.7 | 1.5 |
| Wiring, misc | 0.3 | 0.7 |
| **Total** | **6.3 kg** | **13.9 lbs** |

### 10.3 Performance Summary

| Parameter | Value |
|-----------|-------|
| MGTOW | 14 lbs (6.3 kg) |
| Max Speed | 220 MPH (191 kts) |
| Cruise Speed | 150 MPH (130 kts) |
| Sprint Endurance | 8 minutes |
| Mixed Endurance | 15 minutes |
| Combat Radius | 8–15 km |
| Max g-Load | +12g |
| Sustained g-Load | +8g |

---

## 11. NDAA-Compliant Bill of Materials

### 11.1 Complete BOM

| Category | Component | Manufacturer | Origin | Cost |
|----------|-----------|--------------|--------|------|
| **Airframe** | | | | |
| | Flying wing structure | Custom (carbon fiber) | USA | $1,200 |
| | Kinetic nose assembly | Custom (Al + tungsten) | USA | $300 |
| | Control surfaces (elevons) | Integrated composite | USA | Incl. |
| | Servos ×4 | KST X10 Mini | Taiwan | $200 |
| | Launch rail interface | Machined aluminum | USA | $150 |
| | **Subtotal** | | | **$1,850** |
| **Propulsion** | | | | |
| | EDF Unit | Schübeler DS-94-DIA HST | Germany | $850 |
| | Motor | Lehner 2280/5 | Germany | $350 |
| | ESC | YGE 205HVT | Germany | $380 |
| | **Subtotal** | | | **$1,580** |
| **Power** | | | | |
| | Battery ×2 | MaxAmps 12S 5000mAh 150C | USA | $900 |
| | Power distribution | Custom harness | USA | $80 |
| | **Subtotal** | | | **$980** |
| **Avionics** | | | | |
| | Flight controller | CubePilot Cube Orange+ | Australia | $320 |
| | Carrier board | Custom mini carrier | USA | $150 |
| | GNSS | u-blox ZED-F9P | Switzerland | $180 |
| | Airspeed sensor | MS4525DO (high-speed) | USA | $80 |
| | Radar altimeter | Ainstein US-D1 | USA | $350 |
| | ADS-B receiver | uAvionix pingRX | USA | $300 |
| | **Subtotal** | | | **$1,380** |
| **Seeker System** | | | | |
| | Camera | Allied Vision Alvium 1800 | Germany | $600 |
| | Lens | Tamron M118FM16 | Japan | $150 |
| | Compute | Jetson Orin Nano 8GB | USA | $350 |
| | **Subtotal** | | | **$1,100** |
| **Communications** | | | | |
| | Datalink (air) | Doodle Labs RM-2450-2K | USA | $1,000 |
| | Antenna | Taoglas embedded | Ireland | $60 |
| | **Subtotal** | | | **$1,060** |
| **Integration** | | | | |
| | Wiring, connectors | Custom harness | USA | $150 |
| | Conformal coating | MG Chemicals | Canada | $30 |
| | Assembly labor (2 hrs) | — | USA | $200 |
| | Testing / QC (1 hr) | — | USA | $100 |
| | **Subtotal** | | | **$480** |

### 11.2 Unit Cost Summary

| Element | Cost |
|---------|------|
| Airframe | $1,850 |
| Propulsion | $1,580 |
| Power | $980 |
| Avionics | $1,380 |
| Seeker | $1,100 |
| Communications | $1,060 |
| Integration | $480 |
| **BOM Total** | **$8,430** |

### 11.3 Non-Recurring Engineering (50-Unit LRIP)

| NRE Category | Cost | Per-Unit |
|--------------|------|----------|
| Airframe design & tooling | $35,000 | $700 |
| Guidance software development | $50,000 | $1,000 |
| Seeker integration / AI training | $25,000 | $500 |
| Flight test program (10 test articles) | $30,000 | $600 |
| Launcher development | $15,000 | $300 |
| Documentation / training | $8,000 | $160 |
| **Total NRE** | **$163,000** | **$3,260** |

### 11.4 Fully Burdened Unit Cost

| Lot Size | BOM | NRE/Unit | Consumables | **Total** |
|----------|-----|----------|-------------|-----------|
| 20 units | $8,430 | $8,150 | $500 | **$17,080** |
| 50 units | $8,000 | $3,260 | $500 | **$11,760** |
| 100 units | $7,500 | $1,630 | $500 | **$9,630** |
| 500 units | $6,800 | $330 | $500 | **$7,630** |

**At 50-unit lot: $11,760 per interceptor (well under $16,000 target)**

---

## 12. Support Equipment

### 12.1 Launch System

| Component | Description | Cost |
|-----------|-------------|------|
| Pneumatic Rail Launcher | 3m rail, compressed air, 0–60 kts | $8,000 |
| Air Compressor | Portable, 4500 psi | $2,500 |
| Launch Controller | Wireless trigger, safety interlocks | $1,500 |
| Transport Trailer | Tow-behind, fits launcher + 10 interceptors | $5,000 |
| **Total** | | **$17,000** |

Pro-rated: $340/unit (50-unit program, 1 launcher per 50 aircraft)

### 12.2 Ground Control Station

| Component | Description | Cost |
|-----------|-------------|------|
| Ruggedized Laptop | Getac B360 | $4,000 |
| Doodle Labs Ground Radio | RM-2450-2J | $1,200 |
| Display Software | Custom C-UAS interface | Incl. NRE |
| Antenna (ground) | Taoglas directional | $200 |
| **Total** | | **$5,400** |

Pro-rated: $540/unit (1 GCS per 10 aircraft)

### 12.3 Radar Integration

---

## 13. Concept of Employment

### 13.1 System Configuration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     C-UAS INTERCEPTOR SYSTEM                            │
│                                                                         │
│                        ┌──────────────────┐                             │
│                        │   CUEING RADAR   │                             │
│                        │  (Echodyne, etc) │                             │
│                        └────────┬─────────┘                             │
│                                 │ Target Tracks                         │
│                                 ▼                                       │
│                        ┌──────────────────┐                             │
│                        │  COMMAND & CTRL  │                             │
│                        │     (GCS)        │                             │
│                        └────────┬─────────┘                             │
│                                 │ Launch Cmd                            │
│                 ┌───────────────┼───────────────┐                       │
│                 │               │               │                       │
│                 ▼               ▼               ▼                       │
│          ┌───────────┐   ┌───────────┐   ┌───────────┐                  │
│          │INTERCEPTOR│   │INTERCEPTOR│   │INTERCEPTOR│                  │
│          │    #1     │   │    #2     │   │    #3     │   ···            │
│          │(on rail)  │   │(in flight)│   │(standby)  │                  │
│          └───────────┘   └─────┬─────┘   └───────────┘                  │
│                                │                                        │
│                                │ Intercept                              │
│                                ▼                                        │
│                          ┌───────────┐                                  │
│                          │  TARGET   │                                  │
│                          │  (sUAS)   │                                  │
│                          └───────────┘                                  │
│                                                                         │
│  TIMELINE:  Detect ──► Track ──► ID ──► Launch ──► Guide ──► Defeat    │
│              (2s)      (3s)     (5s)    (15s)     (60s)      (1s)       │
│                                                                         │
│             TOTAL ENGAGEMENT TIME: ~90 seconds                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 13.2 Deployment

| Asset | Quantity | Purpose |
|-------|----------|---------|
| Interceptors (ready) | 4 | Immediate response |
| Interceptors (reload) | 8 | Sustained ops |
| Launcher | 1 | Quad-rail |
| GCS | 1 | Operator station |
| Cueing Radar | 1 | Target detection |
| Generator | 1 | Power for all systems |

### 13.3 Engagement Sequence

1. **Detection:** Radar acquires unknown track.
2. **Classification:** AI/operator identifies as threat.
3. **Authorization:** Operator confirms engagement.
4. **Launch:** Interceptor departs rail (0–60 kts in 2 seconds).
5. **Climb:** Sprint to intercept altitude.
6. **Midcourse:** Datalink guidance from radar track.
7. **Terminal:** Seeker acquires, proportional navigation.
8. **Intercept:** Kinetic impact or net deployment.
9. **BDA:** Track termination confirmed.

---

## 14. Comparison to Existing Systems

| System | Manufacturer | Speed | Defeat Method | Unit Cost | NDAA |
|--------|--------------|-------|---------------|-----------|------|
| **This Design** | Custom | 220 MPH | Kinetic/Net | ~$12K | ✓ |
| Anduril Anvil | Anduril (USA) | 180+ MPH | Kinetic | ~$15K | ✓ |
| Fortem DroneHunter | Fortem (USA) | 100 MPH | Net capture | ~$50K | ✓ |
| Coyote Block 2 | RTX (USA) | 175 MPH | Warhead | ~$80K | ✓ |
| SkyDome Interceptor | D-Fend (Israel) | 150 MPH | Net | ~$30K | ✓ |

---

## 15. Summary

### 15.1 Compliance Status

| Requirement | Status |
|-------------|--------|
| NDAA Section 889 | ✓ Compliant |
| No Chinese components | ✓ Verified |
| Allied-nation sourcing | ✓ USA, Germany, Australia, Switzerland, Taiwan, Japan |
| ITAR-free | ✓ No controlled items |

### 15.2 Path Forward

1. **Phase 1 (3 months):** Detailed design, CFD analysis, component procurement
2. **Phase 2 (2 months):** Prototype fabrication (3 units)
3. **Phase 3 (2 months):** Flight test, guidance integration
4. **Phase 4 (3 months):** Seeker development, target tracking validation
5. **Phase 5 (2 months):** Live intercept testing
6. **Phase 6 (4 months):** LRIP (50 units)

---

## Appendix A: Aerodynamic Analysis

### A.1 Drag Buildup (at 191 knots, sea level)

| Component | CD | % Total |
|-----------|-----|---------|
| Wing (induced) | 0.0085 | 34% |
| Wing (profile) | 0.0070 | 28% |
| Fuselage/body | 0.0045 | 18% |
| EDF inlet | 0.0025 | 10% |
| Control surfaces | 0.0015 | 6% |
| Interference | 0.0010 | 4% |
| **Total CD** | **0.0250** | 100% |

### A.2 Performance Calculations

| Parameter | Value |
|-----------|-------|
| Dynamic Pressure (q) at 191 kts SL | 62 lb/ft² |
| Wing Area (S) | 3.2 ft² |
| Drag (D = qSCD) | 5.0 lbs |
| Thrust Required | 5.0 lbs |
| Thrust Available (EDF at speed) | 6.2 lbs |
| Excess Thrust | 1.2 lbs |
| Thrust Margin | 24% ✓ |

---

## Appendix B: Alternative VTOL Configuration

If VTOL launch is required (expeditionary ops without rail launcher):

### B.1 Detachable VTOL Module

| Component | Specification | Weight | Cost |
|-----------|--------------|--------|------|
| VTOL frame | Carbon tube, quick-release | 300g | $150 |
| Motors ×4 | KDE2306XF-2550 | 200g | $120 |
| ESCs ×4 | BLHeli_S 35A (verify source) | 80g | $80 |
| Props ×4 | 7×3.5" | 40g | $20 |
| Wiring/connectors | XT60, JST | 50g | $30 |
| **Total** | | **670g (+1.5 lbs)** | **$400** |

### B.2 VTOL Performance Impact

| Parameter | Rail Launch | VTOL |
|-----------|-------------|------|
| MGTOW | 14 lbs | 15.5 lbs |
| Max Speed | 220 MPH | 200 MPH |
| Sprint Endurance | 8 min | 6 min |
| Unit Cost | $12,000 | $12,400 |

---
