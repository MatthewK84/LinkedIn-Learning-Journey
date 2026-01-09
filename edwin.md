# Group 1.5 Small Unmanned Aircraft System (sUAS)
## Technical & Build Requirements Document
### NDAA Section 889 Compliant Configuration
**Target Unit Cost:** ≤ $16,000 USD (fully burdened)  
**Compliance:** NDAA Section 889, Blue sUAS Framework Aligned, ITAR-free

---

## 1. Executive Summary

This document defines the technical, performance, and build requirements for a Group 1.5 small Unmanned Aircraft System (sUAS) designed for intelligence, surveillance, and reconnaissance (ISR) missions. The system is fully compliant with NDAA Section 889 prohibitions and aligned with DoD Blue sUAS supply chain principles.

**Key Specifications:**
- VTOL quad-plane configuration, 2.2m wingspan
- 90–120 minute endurance with full ISR payload
- Dual-sensor EO/IR gimbal (US-manufactured)
- 25+ km operational radius with encrypted mesh datalink
- GPS-denied navigation capability via visual-inertial odometry
- Fully burdened unit cost ≤ $16,000 at 20-unit LRIP

---

## 2. Compliance Framework

### 2.1 Regulatory Compliance

| Regulation | Requirement | Status |
|------------|-------------|--------|
| NDAA Section 889 | No covered telecommunications/video surveillance equipment | ✓ Compliant |
| DFARS 252.225-7012 | Covered defense telecommunications disclosure | ✓ Compliant |
| Blue sUAS Principles | Supply chain transparency, allied-nation sourcing | ✓ Aligned |
| ITAR/EAR | No controlled items without proper licensing | ✓ ITAR-free design |
| 14 CFR Part 107 | CONUS flight operations (where applicable) | ✓ Compatible |
| FAA Remote ID | Broadcast Remote ID capability | ✓ Included |

### 2.2 Prohibited Sources

The following entities and their subsidiaries are prohibited per NDAA Section 889:
- Huawei Technologies
- ZTE Corporation
- Hytera Communications
- Hangzhou Hikvision
- Dahua Technology
- Any entity owned/controlled by PRC government

### 2.3 Approved Source Nations

Components shall be sourced from the following nations, in order of preference:

| Tier | Nations | Notes |
|------|---------|-------|
| **Tier 1** | United States | Preferred for all critical systems |
| **Tier 2** | Five Eyes (UK, Canada, Australia, New Zealand) | Acceptable for all systems |
| **Tier 3** | NATO Allies (EU, Japan, South Korea, Israel) | Acceptable with documentation |
| **Restricted** | PRC, Russia, Iran, DPRK | Prohibited |

---

## 3. Applicable Standards

- MIL-STD-810H (Environmental Engineering Considerations)
- MIL-STD-461G (EMI/EMC Requirements)
- MIL-STD-464C (Electromagnetic Environmental Effects)
- DO-160G (Environmental Conditions and Test Procedures)
- MAVLink 2.0 / DroneCAN (Communication Protocols)
- STANAG 4586 (NATO UAS Interoperability) — Level 2 objective
- JAUS (Joint Architecture for Unmanned Systems) — Reference
- NIST SP 800-171 (Cybersecurity framework alignment)

---

## 4. UAS Classification

### 4.1 Group 1.5 Parameters

| Parameter | Requirement | Design Target |
|-----------|-------------|---------------|
| Maximum Gross Takeoff Weight | 20–35 lbs (9–16 kg) | 28 lbs (12.7 kg) |
| Normal Operating Altitude | ≤ 3,500 ft AGL | 1,500 ft AGL |
| Maximum Airspeed | ≤ 100 KTAS | 70 KTAS |
| Launch Method | VTOL (vertical takeoff) | Autonomous |
| Recovery Method | VTOL (vertical landing) | Autonomous |

### 4.2 Mission Profile

**Primary Missions:**
- Intelligence, Surveillance, and Reconnaissance (ISR)
- Target acquisition and battle damage assessment (BDA)
- Route reconnaissance and area surveillance

**Secondary Missions:**
- Communications relay
- Signals intelligence (SIGINT) payload integration
- Counter-UAS detection support

**Operating Environment:**
- Day/night operations
- Austere and expeditionary locations
- GPS-denied/degraded environments
- Maritime and littoral zones

---

## 5. Performance Requirements

### 5.1 Flight Performance

| Parameter | Threshold | Objective |
|-----------|-----------|-----------|
| Endurance (ISR configuration) | ≥ 90 minutes | ≥ 120 minutes |
| Operational Radius | ≥ 15 km | ≥ 25 km |
| Maximum Airspeed | ≥ 55 knots | ≥ 70 knots |
| Cruise Speed | 30–40 knots | 35–45 knots |
| Loiter Speed | 25–30 knots | 28 knots |
| Service Ceiling | ≥ 12,000 ft MSL | ≥ 15,000 ft MSL |
| Maximum Wind (sustained ops) | 20 knots | 25 knots |
| Maximum Gust Tolerance | 30 knots | 35 knots |
| Climb Rate (fixed-wing mode) | ≥ 500 ft/min | ≥ 800 ft/min |

### 5.2 VTOL Performance

| Parameter | Requirement |
|-----------|-------------|
| Vertical Takeoff Weight | Full MGTOW (28 lbs) |
| Hover Endurance | ≥ 8 minutes at MGTOW |
| Transition Altitude | ≤ 150 ft AGL |
| Transition Time | ≤ 15 seconds |
| Landing Accuracy (GPS-aided) | ≤ 2 m CEP |
| Landing Accuracy (GPS-denied) | ≤ 5 m CEP |
| Maximum Crosswind (VTOL) | 15 knots |
| Rejected Takeoff Recovery | Automatic safe landing |

### 5.3 Navigation Performance

| Parameter | Requirement |
|-----------|-------------|
| GNSS Position Accuracy | ≤ 1.5 m CEP (RTK available) |
| GPS-Denied Navigation | Visual-inertial odometry (VIO) required |
| GPS-Denied Position Hold | ≤ 3 m drift over 10 minutes |
| GPS-Denied Endurance | ≥ 30 minutes stable flight |
| Waypoint Capacity | ≥ 200 waypoints |
| Geofence Capability | Hard and soft boundaries, 3D volumes |
| Terrain Following | Radar altimeter + DTM integration |

---

## 6. Airframe Requirements

### 6.1 Configuration

| Parameter | Requirement |
|-----------|-------------|
| Type | Fixed-wing VTOL (quad-plane) |
| Wing Configuration | High-wing, constant chord or moderate taper |
| Wingspan | 2.0–2.4 m (6.5–8 ft) |
| Wing Area | ≥ 0.45 m² |
| Aspect Ratio | 8–10 |
| Fuselage Length | 1.0–1.4 m (3.5–4.5 ft) |
| VTOL Motor Configuration | Quad (4× vertical lift motors) |
| Forward Motor | Single pusher (tractor optional) |

### 6.2 Structural Requirements

| Parameter | Requirement |
|-----------|-------------|
| Empty Weight (airframe only) | ≤ 12 lbs (5.4 kg) |
| Empty Weight (flight-ready, no payload) | ≤ 18 lbs (8.2 kg) |
| Maximum Payload Capacity | ≥ 4 lbs (1.8 kg) |
| Design Load Factor | +4.0g / -2.0g |
| Ultimate Load Factor | +6.0g / -3.0g |
| VTOL Thrust-to-Weight Ratio | ≥ 2.0:1 |
| Fatigue Life | ≥ 500 flight hours |
| Service Life | ≥ 1,000 flight cycles |

### 6.3 Materials

| Component | Material | Source Requirement |
|-----------|----------|-------------------|
| Wing Spar | Carbon fiber tube/I-beam | US or allied |
| Wing Skin | Fiberglass/carbon layup or molded EPO | US or allied |
| Fuselage | Carbon fiber monocoque or fiberglass | US or allied |
| Motor Mounts | Machined aluminum or 3D-printed PA-CF | US |
| Fairings/Hatches | 3D-printed ASA, PETG, or PA12 | US |
| Control Surfaces | Foam core with fiberglass skin | US or allied |
| Fasteners | Stainless steel, mil-spec | US |

**Approved US Composite Suppliers:**
- DragonPlate (Elbridge, NY)
- Rock West Composites (West Jordan, UT)
- Composite Approach (Custom layup)
- ACP Composites (Livermore, CA)

### 6.4 Modularity and Transportability

| Parameter | Requirement |
|-----------|-------------|
| Wing Removal | Tool-free, ≤ 60 seconds per wing |
| Tail Removal | Tool-free or single fastener |
| Payload Bay Access | Quick-release hatch |
| Packed Dimensions | ≤ 36" × 18" × 14" (fits USGI rucksack) |
| Packed Weight (full system) | ≤ 50 lbs (aircraft + GCS + 2 batteries + spares) |
| Assembly Time | ≤ 5 minutes (2 operators) |
| Disassembly Time | ≤ 3 minutes (2 operators) |
| Cases | Pelican or SKB (US-manufactured) |

---

## 7. Avionics Requirements

### 7.1 Flight Controller

| Parameter | Requirement |
|-----------|-------------|
| Platform | ArduPilot (preferred) or PX4 |
| Processor | ARM Cortex-M7 @ ≥ 400 MHz |
| IMU Redundancy | Triple-redundant, isolated mounting |
| Barometer Redundancy | Dual barometer |
| Magnetometer | External, away from power systems |
| PWM Outputs | ≥ 14 channels |
| Serial Ports | ≥ 6 UARTs |
| CAN Bus | ≥ 2 DroneCAN ports |
| I2C/SPI | Available for expansion |
| Logging | High-rate onboard (≥ 200 Hz IMU) |

**Selected Hardware:**  
- **CubePilot Cube Orange+** — Australian design, verified supply chain
- **Carrier Board:** ADSB Carrier or Kore carrier (CubePilot ecosystem)
- **Alternate:** mRo Control Zero H7 (100% US, Mayan Robotics, California)

| Cube Orange+ Specifications | Value |
|----------------------------|-------|
| Processor | STM32H757 dual-core (480 MHz) |
| IMUs | 3× (ICM-42688, ICM-20948, ICM-20602) |
| Barometers | 2× MS5611 |
| Magnetometer | 1× internal + external required |
| Vibration Isolation | Triple-dampened cube design |
| Cost | $320 |

### 7.2 GNSS System

| Parameter | Requirement |
|-----------|-------------|
| Receivers | Dual (independent modules) |
| Frequency Bands | L1/L5 or L1/L2 (multi-band required) |
| Constellations | GPS, GLONASS, Galileo, BeiDou |
| Update Rate | ≥ 10 Hz |
| RTK Capable | Yes (for precision operations) |
| Antenna | Active patch, ground plane integrated |

**Selected Hardware:**  
- **u-blox ZED-F9P** ×2 — Swiss-manufactured (Thalwil, Switzerland)
- **Antenna:** Taoglas ADFGP.50A (Ireland) or Maxtena M7HCT (USA)

| ZED-F9P Specifications | Value |
|-----------------------|-------|
| Position Accuracy (RTK) | 1 cm + 1 ppm CEP |
| Position Accuracy (Standard) | 1.5 m CEP |
| Update Rate | Up to 20 Hz |
| Protocols | UBX, NMEA, RTCM 3.3 |
| Cost (module) | $180 each |

### 7.3 Companion Computer

| Parameter | Requirement |
|-----------|-------------|
| AI Compute | ≥ 40 TOPS (INT8) |
| CPU | 6+ ARM cores @ ≥ 1.5 GHz |
| GPU | CUDA-capable (for VIO, detection) |
| RAM | ≥ 8 GB |
| Storage | ≥ 256 GB NVMe |
| Video Interfaces | 2× CSI/MIPI, USB 3.0 |
| Network | Gigabit Ethernet |
| Power Consumption | ≤ 15W typical |

**Selected Hardware:**  
- **NVIDIA Jetson Orin NX 16GB** — US-designed (Santa Clara, CA), Taiwan fab
- **Carrier Board:** Connect Tech Quark (Canada) or Auvidea JNX42 (Germany)

| Orin NX 16GB Specifications | Value |
|----------------------------|-------|
| AI Performance | 100 TOPS (INT8) |
| CPU | 8-core ARM Cortex-A78AE @ 2.0 GHz |
| GPU | 1024-core Ampere |
| RAM | 16 GB LPDDR5 |
| Power | 10–25W configurable |
| Cost | $700 (module + carrier) |

**Software Stack:**
- JetPack 6.x (L4T)
- ROS 2 Humble
- NVIDIA VPI (visual-inertial processing)
- TensorRT (optimized inference)
- GStreamer (video encoding)

### 7.4 Supplemental Sensors

| Sensor | Model | Manufacturer | Origin | Purpose | Cost |
|--------|-------|--------------|--------|---------|------|
| Airspeed | MS5525DSO | TE Connectivity | USA | Air data | $50 |
| Rangefinder | SF11/C | LightWare | South Africa | Terrain following, landing | $280 |
| Optical Flow | PMW3901 + VL53L1X | PixArt/ST | Taiwan/EU | GPS-denied hover | $40 |
| ADS-B In | pingRX | uAvionix | USA | Traffic awareness | $300 |
| Remote ID | pingID | uAvionix | USA | FAA compliance | $200 |

---

## 8. Propulsion System

### 8.1 Forward Flight Motor

| Parameter | Requirement |
|-----------|-------------|
| Motor Type | Brushless outrunner |
| KV Rating | 380–450 KV |
| Power Rating | ≥ 1,200W continuous |
| Efficiency | ≥ 85% at cruise |
| Mounting | Direct or geared |

**Selected Hardware:**  
- **KDE Direct KDE4014XF-380** — 100% US (Bend, Oregon)

| KDE4014XF-380 Specifications | Value |
|-----------------------------|-------|
| KV | 380 |
| Max Continuous Power | 1,450W |
| Max Efficiency | 93% |
| Weight | 198g |
| Shaft | 6mm |
| Cost | $180 |

### 8.2 Forward Flight ESC

| Parameter | Requirement |
|-----------|-------------|
| Current Rating | ≥ 60A continuous |
| Voltage | 6S (22.2V nominal) |
| BEC | Not required (separate BEC) |
| Telemetry | DroneCAN or analog |
| Protocols | DShot600, PWM |

**Selected Hardware:**  
- **KDE Direct KDEXF-UAS55** — 100% US

| KDEXF-UAS55 Specifications | Value |
|---------------------------|-------|
| Continuous Current | 55A |
| Burst Current | 75A (10s) |
| Voltage Range | 3S–6S |
| Firmware | KDE-specific, field-updatable |
| Cost | $150 |

### 8.3 Forward Propeller

| Parameter | Requirement |
|-----------|-------------|
| Diameter | 15–17 inches |
| Pitch | 8–10 inches |
| Material | Carbon fiber |
| Type | Folding (reduces drag in VTOL) |
| Balance | Factory-balanced, ≤ 0.5g imbalance |

**Selected Hardware:**  
- **Mejzlik 16×8 Carbon Folding** — Czech Republic (NATO ally)
- **Alternate:** APC 15×10E (US-manufactured)

Cost: $85

### 8.4 VTOL Lift Motors (×4)

| Parameter | Requirement |
|-----------|-------------|
| Motor Type | Brushless outrunner |
| KV Rating | 500–700 KV |
| Thrust (per motor) | ≥ 4 kg (8.8 lbs) at 100% |
| Combined Thrust | ≥ 2× MGTOW |

**Selected Hardware:**  
- **KDE Direct KDE3510XF-475** ×4 — 100% US

| KDE3510XF-475 Specifications | Value |
|-----------------------------|-------|
| KV | 475 |
| Max Thrust (6S, 12" prop) | 4.8 kg |
| Max Efficiency | 88% |
| Weight | 136g |
| Cost | $95 each ($380 total) |

### 8.5 VTOL ESCs (×4)

**Selected Hardware:**  
- **KDE Direct KDEXF-UAS55HVC** ×4 — 100% US

Cost: $150 each ($600 total)

### 8.6 VTOL Propellers (×4)

**Selected Hardware:**  
- **KDE Direct KDE-CF125-DP** (12.5" carbon, dual-blade) ×4

Cost: $45 each ($180 total)

### 8.7 Propulsion Summary

| Component | Qty | Unit Cost | Total |
|-----------|-----|-----------|-------|
| KDE4014XF-380 (forward) | 1 | $180 | $180 |
| KDEXF-UAS55 ESC (forward) | 1 | $150 | $150 |
| Mejzlik 16×8 prop | 1 | $85 | $85 |
| KDE3510XF-475 (VTOL) | 4 | $95 | $380 |
| KDEXF-UAS55HVC ESC (VTOL) | 4 | $150 | $600 |
| KDE-CF125-DP prop (VTOL) | 4 | $45 | $180 |
| **Propulsion Total** | | | **$1,575** |

---

## 9. Power System

### 9.1 Battery Specifications

| Parameter | Requirement |
|-----------|-------------|
| Chemistry | Lithium Polymer (LiPo) or Lithium-Ion |
| Configuration | 6S (22.2V nominal) |
| Capacity | ≥ 16,000 mAh |
| Discharge Rate | ≥ 15C continuous |
| Energy | ≥ 350 Wh |
| Cell Origin | US, Japan, or South Korea |
| Assembly | US-based |

**Selected Hardware:**  
- **MaxAmps 6S 16000mAh 150C** — US assembly (Spokane, WA), LG/Samsung cells

| MaxAmps 6S 16000 Specifications | Value |
|--------------------------------|-------|
| Configuration | 6S1P |
| Capacity | 16,000 mAh |
| Discharge | 150C burst, 75C continuous |
| Energy | 355 Wh |
| Weight | 1.85 kg |
| Connector | XT90 or custom |
| Cost | $550 |

**Alternate (Higher Performance):**
- **Amprius SiMaxx Custom Pack** — 100% US (Fremont, CA)
- Energy density: 400+ Wh/kg
- Cost: $1,100 (for extended endurance missions)

### 9.2 Power Distribution

| Parameter | Requirement |
|-----------|-------------|
| Main Bus Voltage | 22.2V nominal (25.2V max) |
| Current Capacity | ≥ 150A peak |
| Per-Motor Current Sensing | Required |
| Voltage Monitoring | Per-cell (6S) |
| BEC Outputs | 12V/5A, 5V/5A (redundant 5V) |

**Selected Hardware:**  
- **Mauch Power Cube 4** — Germany (NATO ally)
- Includes: PDB + dual BEC + current/voltage sensing
- Cost: $180

### 9.3 Battery Management

| Feature | Requirement |
|---------|-------------|
| Cell Balancing | External charger |
| State-of-Charge Monitoring | Real-time telemetry |
| Over-Current Protection | Hardware (PDB fusing) |
| Low-Voltage Warning | Configurable (3.5V/cell default) |
| Critical Voltage RTL | Configurable (3.3V/cell default) |
| Temperature Monitoring | Required (NTC on pack) |

---

## 10. Communications System

### 10.1 Command & Control (C2) Datalink

| Parameter | Threshold | Objective |
|-----------|-----------|-----------|
| Range (LOS) | ≥ 15 km | ≥ 30 km |
| Latency (round-trip) | ≤ 100 ms | ≤ 50 ms |
| Throughput (uplink) | ≥ 100 kbps | ≥ 500 kbps |
| Throughput (downlink) | ≥ 5 Mbps | ≥ 20 Mbps |
| Encryption | AES-256 | AES-256 + frequency hopping |
| Frequency Band | 900 MHz or 1.8 GHz | Dual-band |
| Transmit Power | ≤ 1W EIRP (compliant) | Adjustable |
| Link Redundancy | Automatic failover | Seamless handoff |
| Mesh Capability | Not required | Preferred |

**Selected Hardware:**  
- **Doodle Labs Smart Radio RM-2450-2J** (pair) — 100% US (Madison, WI)

| Doodle Labs RM-2450-2J Specifications | Value |
|--------------------------------------|-------|
| Frequency | 2.4 GHz (900 MHz variant available) |
| Range | 30+ km LOS |
| Throughput | Up to 80 Mbps |
| Latency | 8–15 ms |
| Encryption | AES-256 hardware |
| Mesh Support | Up to 5 nodes |
| Video + C2 Integration | Yes |
| Weight | 85g |
| Cost (pair) | $2,400 |

**Benefits:**
- Single radio for both C2 and HD video
- Replaces need for separate video TX
- US-manufactured, defense-proven
- Native MAVLink integration

### 10.2 Lost Link Behavior

| Condition | Threshold | Action |
|-----------|-----------|--------|
| C2 Link Loss | > 10 seconds | Circle and attempt reconnect |
| C2 Link Loss | > 30 seconds | Return to Launch (RTL) |
| C2 Link Loss | > 5 minutes | Land at nearest safe point |
| Critical Battery + Link Loss | < 20% SoC | Immediate RTL |
| Geofence Breach | Any boundary | RTL or loiter (configurable) |

### 10.3 Spectrum Management

| Band | Primary Use | Licensing |
|------|------------|-----------|
| 900 MHz | Long-range C2 backup | FCC Part 15/87 |
| 2.4 GHz | Primary C2 + video | FCC Part 15 |
| 5.8 GHz | High-bandwidth video (alternate) | FCC Part 15 |

---

## 11. Payload System

### 11.1 EO/IR Gimbal Requirements

| Parameter | Threshold | Objective |
|-----------|-----------|-----------|
| EO Sensor Resolution | ≥ 4K (8 MP) | ≥ 20 MP |
| EO Sensor Type | CMOS, rolling shutter | Global shutter |
| Optical Zoom | ≥ 10× | ≥ 30× |
| Digital Zoom | ≥ 4× | ≥ 8× |
| IR Sensor Resolution | ≥ 640×512 | ≥ 1280×1024 |
| IR Sensitivity (NETD) | ≤ 50 mK | ≤ 30 mK |
| IR Spectral Band | LWIR (8–14 μm) | LWIR |
| Stabilization | 3-axis mechanical | 3-axis + IMU fusion |
| Stabilization Accuracy | ≤ 0.03° RMS | ≤ 0.01° RMS |
| Object Tracking | Software-based | Onboard AI tracking |
| Geolocation Accuracy | ≤ 10 m CEP (slant range corrected) | ≤ 5 m CEP |
| Gimbal Weight | ≤ 800 g | ≤ 600 g |
| Gimbal Power | ≤ 15W | ≤ 10W |

**Selected Hardware:**  
- **Teledyne FLIR Vue TZ20-R** — 100% US (Wilsonville, Oregon)

| FLIR Vue TZ20-R Specifications | Value |
|-------------------------------|-------|
| EO Sensor | 1/2.8" CMOS, 2MP (1920×1080) |
| EO Zoom | 20× optical + 4× digital (80× total) |
| IR Sensor | FLIR Boson 640 (640×512 @ 12 μm) |
| IR NETD | < 40 mK |
| Stabilization | 3-axis, ±0.03° accuracy |
| Tracking | Lock-and-follow (on-gimbal) |
| Output | H.264/H.265, Ethernet/HDMI |
| Weight | 580g |
| Power | 12W typical |
| MAVLink | Native integration |
| Cost | $5,500 |

**Alternate Option (Higher EO Resolution):**  
- **NextVision Colibri 2** — Israel (NATO partner)
- 30× EO zoom, 4K sensor, 640 thermal
- Cost: $4,800

### 11.2 Payload Interface

| Parameter | Requirement |
|-----------|-------------|
| Power Output | 12V @ 3A regulated |
| Power Output | 5V @ 2A regulated |
| Data Interface | Gigabit Ethernet (primary) |
| Data Interface | USB 3.0 (secondary) |
| Control Interface | MAVLink passthrough, S.Bus/PWM |
| Mechanical Mount | Quick-release, vibration-isolated |
| Payload Bay Volume | ≥ 250 cm³ |

### 11.3 Gimbal Integration

| Connection | Protocol | Purpose |
|------------|----------|---------|
| Ethernet | GigE Vision / RTP | Video stream to companion computer |
| Serial (UART) | MAVLink | Gimbal control, telemetry |
| PWM/S.Bus | RC passthrough | Manual gimbal control backup |
| Trigger | GPIO | Camera trigger sync |

---

## 12. Ground Control Station

### 12.1 Hardware Requirements

| Parameter | Requirement |
|-----------|-------------|
| Form Factor | Rugged tablet or integrated controller |
| Display Size | ≥ 10 inches |
| Display Resolution | ≥ 1920×1200 |
| Display Brightness | ≥ 1,000 nits (sunlight readable) |
| Operating Time | ≥ 5 hours (internal battery) |
| Controller Input | Integrated joysticks or external RC |
| Ingress Protection | IP65 or better |
| Operating Temperature | -20°C to +50°C |
| MIL-STD-810H | Drop, shock, vibration tested |

**Selected Hardware:**  
- **Getac F110 G6** — Taiwan (Five Eyes supply chain partner)

| Getac F110 G6 Specifications | Value |
|-----------------------------|-------|
| Display | 11.6" IPS, 1920×1080, 1200 nits |
| Processor | Intel Core i5/i7 (11th gen) |
| RAM | 16 GB |
| Storage | 256 GB SSD |
| Battery Life | 8+ hours |
| Rating | IP66, MIL-STD-810H |
| Weight | 1.45 kg |
| OS | Windows 11 |
| Cost | $3,200 |

**Pro-Rated Cost (20-unit program):** $640/unit (5 GCS per 20 aircraft)

### 12.2 GCS Software

| Feature | Requirement |
|---------|-------------|
| Flight Planning | Waypoint, polygon survey, corridor, orbit |
| Real-Time Telemetry | Attitude, position, battery, link quality |
| Video Display | Full-screen, PIP, multi-stream capable |
| Map Support | Offline (MBTiles), WMS, WMTS |
| Mission Recording | Automatic flight log + video archive |
| Interoperability | STANAG 4586 Level 2 (objective) |
| Target Mensuration | Slant range, coordinates, elevation |

**Selected Software:**  
- **QGroundControl** (open-source, BSD license)
- **Alternate:** UgCS Enterprise (commercial support)

### 12.3 External Controller (Optional)

- **Futaba T18SZ** — Japan (NATO ally)
- 18-channel, dual receiver capable
- Cost: $750 (optional for manual override)

---

## 13. Environmental Requirements

### 13.1 Operating Environment

| Parameter | Requirement | Test Standard |
|-----------|-------------|---------------|
| Temperature (Operating) | -20°C to +50°C | MIL-STD-810H Method 501.7/502.7 |
| Temperature (Storage) | -40°C to +70°C | MIL-STD-810H Method 501.7/502.7 |
| Altitude (Operating) | Sea level to 15,000 ft MSL | MIL-STD-810H Method 500.6 |
| Humidity | 5–95% RH (non-condensing) | MIL-STD-810H Method 507.6 |
| Rain | Light rain (operational) | MIL-STD-810H Method 506.6 (Procedure I) |
| Sand/Dust | Blowing dust (operational) | MIL-STD-810H Method 510.7 |
| Salt Fog | 48-hour exposure (storage) | MIL-STD-810H Method 509.7 |
| Vibration | Operational + transport | MIL-STD-810H Method 514.8 |
| Shock | 40g, 11ms, half-sine | MIL-STD-810H Method 516.8 |

### 13.2 Electromagnetic Compatibility

| Parameter | Requirement | Test Standard |
|-----------|-------------|---------------|
| Radiated Emissions | Compliant | MIL-STD-461G RE102 |
| Conducted Emissions | Compliant | MIL-STD-461G CE102 |
| Radiated Susceptibility | Compliant | MIL-STD-461G RS103 |
| ESD Immunity | Level 3 | IEC 61000-4-2 |

---

## 14. Cybersecurity Requirements

### 14.1 Data Protection

| Requirement | Implementation |
|-------------|----------------|
| Data-at-Rest Encryption | AES-256 (onboard storage) |
| Data-in-Transit Encryption | AES-256 (all RF links) |
| Key Management | Hardware security module preferred |
| Secure Boot | Required (hardware root of trust) |
| Firmware Signing | Required (manufacturer signature) |

### 14.2 Anti-Tamper

| Requirement | Implementation |
|-------------|----------------|
| Zeroization | Crypto key destruction on tamper detect |
| Physical Security | Tamper-evident seals on avionics bay |
| SD Card Encryption | Full-disk encryption |
| USB Lockout | Configurable (disable in operational mode) |

### 14.3 Network Security

| Requirement | Implementation |
|-------------|----------------|
| Authentication | MAVLink 2.0 signing |
| Firewall | Companion computer iptables |
| Intrusion Detection | Optional (log anomalous commands) |
| Supply Chain | SBOM (Software Bill of Materials) maintained |

---

## 15. Reliability and Maintainability

### 15.1 Reliability Requirements

| Parameter | Requirement |
|-----------|-------------|
| Mean Time Between Failures (MTBF) | ≥ 300 flight hours |
| Mean Time Between Critical Failures | ≥ 500 flight hours |
| Mission Success Rate | ≥ 95% |
| Redundancy | No single point of failure (flight-critical) |

### 15.2 Redundant Systems

| System | Redundancy Level |
|--------|-----------------|
| IMU | Triple |
| Barometer | Dual |
| GNSS | Dual (independent antennas) |
| Magnetometer | Dual (internal + external) |
| Power Bus | Dual BEC |
| Flight Surfaces | Dual servos on primary surfaces (optional) |
| C2 Link | Dual-band (2.4 GHz + 900 MHz backup) |

### 15.3 Maintainability Requirements

| Parameter | Requirement |
|-----------|-------------|
| Mean Time to Repair (MTTR) | ≤ 30 minutes (field-level) |
| Mean Time to Repair (depot) | ≤ 4 hours |
| Field-Replaceable Units | Motor, prop, servo, battery, wing, payload |
| Special Tools Required | None (standard metric hand tools) |
| Inspection Interval | 50 flight hours |
| Overhaul Interval | 250 flight hours |

### 15.4 Spare Parts Kit

| Item | Quantity | Purpose |
|------|----------|---------|
| VTOL Motor | 2 | Crash replacement |
| VTOL Prop | 8 | Consumable |
| Forward Prop | 2 | Consumable |
| Servo | 4 | Surface actuator |
| GNSS Module | 1 | Avionics spare |
| ESC | 2 | Propulsion spare |
| Wiring Harness | 1 | Electrical repair |
| Conformal Coating | 1 can | Field repair |

---

## 16. Safety Requirements

### 16.1 Flight Termination System

| Feature | Requirement |
|---------|-------------|
| Manual Kill Switch | Dedicated channel, latching |
| Autonomous Termination Triggers | Geofence, critical battery, hardware fault |
| Termination Action | Motor shutdown, controlled descent |
| Parachute Integration | Prepared for (connector, servo) |

### 16.2 Operational Safety

| Requirement | Implementation |
|-------------|----------------|
| Pre-Flight Checklist | Software-enforced |
| Arm Prevention | GPS lock, sensor health, geofence set |
| Return-to-Launch | One-button activation |
| Maximum Range Limit | Configurable (default: operational radius + 10%) |

---

## 17. Bill of Materials — Complete System

### 17.1 Airframe & Structure

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Carbon fiber frame kit | Quad-plane, 2.2m span | Custom / Composite Approach | USA | $900 |
| Wing spar | CF tube, 20mm OD | DragonPlate | USA | $150 |
| Wing skin | Fiberglass/EPO hybrid | Custom | USA | $250 |
| 3D printed components | Motor mounts, fairings, hatches | PA-CF/ASA | USA | $200 |
| Hardware | AN bolts, rivets, hinges | Aircraft Spruce | USA | $150 |
| Control surface servos ×6 | KST DS215MG (25 kg-cm) | KST | Taiwan | $360 |
| Wing quick-release | Aluminum CNC | Custom | USA | $100 |
| **Subtotal** | | | | **$2,110** |

### 17.2 Propulsion

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Forward motor | KDE4014XF-380 | KDE Direct | USA | $180 |
| Forward ESC | KDEXF-UAS55 | KDE Direct | USA | $150 |
| Forward prop | Mejzlik 16×8 CF folding | Mejzlik | Czech | $85 |
| VTOL motors ×4 | KDE3510XF-475 | KDE Direct | USA | $380 |
| VTOL ESCs ×4 | KDEXF-UAS55HVC | KDE Direct | USA | $600 |
| VTOL props ×4 | KDE-CF125-DP | KDE Direct | USA | $180 |
| **Subtotal** | | | | **$1,575** |

### 17.3 Avionics

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Flight controller | Cube Orange+ | CubePilot | Australia | $320 |
| Carrier board | ADSB Carrier Board | CubePilot | Australia | $150 |
| GNSS modules ×2 | u-blox ZED-F9P | u-blox | Switzerland | $360 |
| GNSS antennas ×2 | Maxtena M7HCT | Maxtena | USA | $200 |
| Airspeed sensor | MS5525DSO | TE Connectivity | USA | $50 |
| Rangefinder | LightWare SF11/C | LightWare | South Africa | $280 |
| Optical flow | PMW3901 + VL53L1X | Various | Taiwan/EU | $40 |
| ADS-B receiver | pingRX | uAvionix | USA | $300 |
| Remote ID | pingID | uAvionix | USA | $200 |
| External magnetometer | RM3100 | PNI Sensor | USA | $85 |
| **Subtotal** | | | | **$1,985** |

### 17.4 Companion Computer

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Compute module | Jetson Orin NX 16GB | NVIDIA | USA | $500 |
| Carrier board | Connect Tech Quark | Connect Tech | Canada | $250 |
| NVMe storage | 256GB Samsung 980 Pro | Samsung | South Korea | $50 |
| Cooling | Active heatsink + fan | Connect Tech | Canada | $50 |
| Enclosure | 3D printed + RF shield | Custom | USA | $50 |
| **Subtotal** | | | | **$900** |

### 17.5 Communications

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Datalink (air + ground) | Doodle Labs RM-2450-2J ×2 | Doodle Labs | USA | $2,400 |
| Air antenna | Taoglas TG.30 omni | Taoglas | Ireland | $80 |
| Ground antenna | Taoglas MA111 patch | Taoglas | Ireland | $120 |
| RF cables | LMR-195 assemblies | Times Microwave | USA | $60 |
| Backup RC receiver | FrSky R9 Slim+ | FrSky | China | **EXCLUDED** |
| Backup RC receiver | Futaba R7108SB | Futaba | Japan | $120 |
| **Subtotal** | | | | **$2,780** |

### 17.6 EO/IR Payload

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Gimbal system | FLIR Vue TZ20-R | Teledyne FLIR | USA | $5,500 |
| Gimbal damping mount | Wire rope isolator | Shock Tech | USA | $120 |
| Ethernet cable | Shielded Cat6 | Belden | USA | $20 |
| **Subtotal** | | | | **$5,640** |

### 17.7 Power System

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Flight battery | MaxAmps 6S 16000mAh 150C | MaxAmps | USA | $550 |
| Spare battery | MaxAmps 6S 16000mAh 150C | MaxAmps | USA | $550 |
| Power module | Mauch PL-200 | Mauch Electronics | Germany | $120 |
| PDB | Mauch Power Cube 4 | Mauch Electronics | Germany | $180 |
| Battery tray | Quick-release, CNC aluminum | Custom | USA | $80 |
| **Subtotal** | | | | **$1,480** |

### 17.8 Ground Control Station (Pro-Rated)

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Tablet | Getac F110 G6 | Getac | Taiwan | $640* |
| Tripod mount | RAM Mount X-Grip | RAM Mounts | USA | $60 |
| Sunshade | Custom 3D printed | — | USA | $20 |
| Pelican case | 1510 with foam | Pelican | USA | $200 |
| **Subtotal** | | | | **$920** |

*Pro-rated: 5 GCS units for 20 aircraft program = $3,200 ÷ 4 aircraft/GCS = $640/unit

### 17.9 Integration & Consumables

| Component | Specification | Manufacturer | Origin | Cost |
|-----------|--------------|--------------|--------|------|
| Wiring harnesses | Custom, Molex/TE connectors | Custom | USA | $200 |
| Conformal coating | MG Chemicals 422B | MG Chemicals | Canada | $40 |
| Heat shrink, zip ties | — | HellermannTyton | USA/UK | $30 |
| Loctite, epoxy | — | Henkel | USA | $40 |
| Documentation | Tech manual, flight cards | — | — | $50 |
| Flight case | Pelican 1650 | Pelican | USA | $350 |
| **Subtotal** | | | | **$710** |

---

## 18. Cost Summary

### 18.1 Bill of Materials Summary

| Category | Cost |
|----------|------|
| Airframe & Structure | $2,110 |
| Propulsion | $1,575 |
| Avionics | $1,985 |
| Companion Computer | $900 |
| Communications | $2,780 |
| EO/IR Payload | $5,640 |
| Power System | $1,480 |
| GCS (pro-rated) | $920 |
| Integration & Consumables | $710 |
| **BOM Total** | **$18,100** |

### 18.2 Cost Reduction to Meet $16,000 Target

| Optimization | Savings |
|--------------|---------|
| Single battery (spare as separate line item) | -$550 |
| Payload: NextVision Colibri 2 instead of FLIR TZ20-R | -$700 |
| GCS: Lower-spec tablet or shared asset | -$300 |
| Volume pricing (20+ units): ~12% on major items | -$600 |
| **Total Reductions** | **-$2,150** |

### 18.3 Adjusted BOM

| Category | Original | Adjusted |
|----------|----------|----------|
| Airframe & Structure | $2,110 | $2,110 |
| Propulsion | $1,575 | $1,400 (volume) |
| Avionics | $1,985 | $1,800 (volume) |
| Companion Computer | $900 | $850 (volume) |
| Communications | $2,780 | $2,500 (volume) |
| EO/IR Payload | $5,640 | $4,940 (Colibri 2) |
| Power System | $1,480 | $930 (single battery) |
| GCS (pro-rated) | $920 | $620 (shared asset) |
| Integration & Consumables | $710 | $650 |
| **Adjusted BOM** | | **$15,800** |

### 18.4 Non-Recurring Engineering (20-Unit LRIP)

| NRE Category | Cost | Per-Unit |
|--------------|------|----------|
| Airframe design & tooling | $18,000 | $900 |
| Software integration & tuning | $12,000 | $600 |
| Flight test program | $10,000 | $500 |
| Environmental testing (MIL-STD-810H subset) | $8,000 | $400 |
| Documentation & training | $5,000 | $250 |
| Certification / COA support | $4,000 | $200 |
| **Total NRE** | **$57,000** | **$2,850** |

### 18.5 Fully Burdened Unit Cost

| Cost Element | 20-Unit Lot | 50-Unit Lot |
|--------------|-------------|-------------|
| BOM (adjusted) | $15,800 | $14,500 |
| NRE (amortized) | $2,850 | $1,140 |
| **Fully Burdened** | **$18,650** | **$15,640** |

### 18.6 Path to $16,000 at 20 Units

To achieve $16,000 fully burdened at 20 units, additional reductions required:

| Option | Action | Savings |
|--------|--------|---------|
| A | Use mRo flight controller (US) vs Cube Orange+ | -$150 |
| B | Use RFD900x (Australian) + custom video vs Doodle Labs | -$1,200 |
| C | Reduce NRE scope (skip environmental testing) | -$400/unit |
| D | Partner co-investment in NRE | -$500/unit |

**Configuration for $16,000 Target (Option B + D):**

| Element | Cost |
|---------|------|
| Adjusted BOM | $14,600 |
| NRE (with partner) | $1,400 |
| **Total** | **$16,000** |

---

## 19. Development Schedule

### 19.1 Program Milestones

| Phase | Milestone | Duration | Exit Criteria |
|-------|-----------|----------|---------------|
| Phase 0 | Requirements Finalization | 2 weeks | TRD signed off |
| Phase 1 | Preliminary Design Review (PDR) | 6 weeks | Concept frozen |
| Phase 2 | Critical Design Review (CDR) | 8 weeks | Drawings released |
| Phase 3 | Prototype Fabrication | 6 weeks | First article complete |
| Phase 4 | Ground Testing | 2 weeks | All systems functional |
| Phase 5 | First Flight | 1 week | Airworthiness confirmed |
| Phase 6 | Flight Test Program | 8 weeks | Performance verified |
| Phase 7 | Payload Integration | 4 weeks | Full ISR capability |
| Phase 8 | Environmental Testing | 4 weeks | MIL-STD-810H subset |
| Phase 9 | LRIP (20 units) | 12 weeks | Delivery complete |
| **Total** | | **53 weeks** | |

### 19.2 Deliverables

| Deliverable | Format |
|-------------|--------|
| Technical Data Package | CAD (STEP), drawings (PDF) |
| Software Source Code | Git repository |
| Flight Manual | PDF, printed |
| Maintenance Manual | PDF, printed |
| Training Curriculum | Slides, videos |
| Acceptance Test Procedures | PDF |
| As-Built Configuration | Serial-tracked BOM |

---

## 20. Verification Matrix

| Req ID | Requirement | Section | Verification Method |
|--------|-------------|---------|---------------------|
| PERF-001 | Endurance ≥ 90 min | 5.1 | Test |
| PERF-002 | Range ≥ 15 km | 5.1 | Test |
| PERF-003 | Speed ≥ 55 kts | 5.1 | Test |
| PERF-004 | GPS-denied flight ≥ 30 min | 5.3 | Test |
| STRUCT-001 | MGTOW ≤ 35 lbs | 4.1 | Inspection |
| STRUCT-002 | Load factor +4g/-2g | 6.2 | Analysis |
| AVION-001 | Triple IMU | 7.1 | Inspection |
| AVION-002 | Dual GNSS | 7.2 | Inspection |
| COMM-001 | Range ≥ 15 km | 10.1 | Test |
| COMM-002 | Encryption AES-256 | 10.1 | Analysis |
| PAYLOAD-001 | EO ≥ 4K | 11.1 | Inspection |
| PAYLOAD-002 | IR ≤ 50 mK NETD | 11.1 | Test |
| ENV-001 | Temp -20°C to +50°C | 13.1 | Test |
| ENV-002 | IP rating ≥ IP44 | 13.1 | Test |
| REL-001 | MTBF ≥ 300 hours | 15.1 | Analysis |
| SEC-001 | AES-256 at rest | 14.1 | Analysis |
| COST-001 | Unit cost ≤ $16,000 | 18.6 | Audit |
| COMPL-001 | NDAA Section 889 | 2.1 | Audit |

---

## 21. Appendices

### Appendix A: System Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    GROUP 1.5 sUAS — SYSTEM ARCHITECTURE                    │
│                           (NDAA COMPLIANT)                                 │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           AIRFRAME                                  │   │
│  │                                                                     │   │
│  │   VTOL MOTORS (×4)              FORWARD MOTOR                       │   │
│  │   KDE3510XF-475 [USA]           KDE4014XF-380 [USA]                 │   │
│  │        │                              │                             │   │
│  │   VTOL ESCs (×4)                FORWARD ESC                         │   │
│  │   KDE UAS55HVC [USA]            KDE UAS55 [USA]                     │   │
│  │        │                              │                             │   │
│  │        └──────────────┬───────────────┘                             │   │
│  │                       │                                             │   │
│  │              ┌────────┴────────┐                                    │   │
│  │              │   POWER DIST    │                                    │   │
│  │              │   Mauch [DEU]   │                                    │   │
│  │              └────────┬────────┘                                    │   │
│  │                       │                                             │   │
│  │   ┌───────────────────┼───────────────────┐                         │   │
│  │   │                   │                   │                         │   │
│  │   ▼                   ▼                   ▼                         │   │
│  │ ┌──────────┐   ┌─────────────┐   ┌──────────────┐                   │   │
│  │ │ BATTERY  │   │   FLIGHT    │   │  COMPANION   │                   │   │
│  │ │ MaxAmps  │   │ CONTROLLER  │   │  COMPUTER    │                   │   │
│  │ │  [USA]   │   │ Cube Orange+│   │ Jetson Orin  │                   │   │
│  │ │          │   │   [AUS]     │   │  NX [USA]    │                   │   │
│  │ └──────────┘   └──────┬──────┘   └──────┬───────┘                   │   │
│  │                       │                 │                           │   │
│  │              ┌────────┴────────┐        │                           │   │
│  │              │    SENSORS      │        │                           │   │
│  │              │                 │        │                           │   │
│  │              │ • GNSS ×2 [CHE] │        │ ┌───────────────┐         │   │
│  │              │ • IMU ×3 [AUS]  │        │ │  EO/IR GIMBAL │         │   │
│  │              │ • Baro ×2 [AUS] │        └─┤  FLIR TZ20-R  │         │   │
│  │              │ • Airspeed [USA]│          │    [USA]      │         │   │
│  │              │ • LiDAR [ZAF]   │          └───────────────┘         │   │
│  │              │ • ADS-B [USA]   │                                    │   │
│  │              └─────────────────┘                                    │   │
│  │                       │                                             │   │
│  │              ┌────────┴────────┐                                    │   │
│  │              │   DATALINK      │                                    │   │
│  │              │  Doodle Labs    │                                    │   │
│  │              │    [USA]        │                                    │   │
│  │              └────────┬────────┘                                    │   │
│  │                       │                                             │   │
│  └───────────────────────┼─────────────────────────────────────────────┘   │
│                          │ RF (2.4 GHz, AES-256)                           │
│                          │                                                 │
│  ┌───────────────────────┴─────────────────────────────────────────────┐   │
│  │                    GROUND CONTROL STATION                           │   │
│  │                                                                     │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │   │
│  │   │  Datalink    │    │   Tablet     │    │    GCS       │         │   │
│  │   │ Doodle Labs  │────│  Getac F110  │────│  Software    │         │   │
│  │   │   [USA]      │    │   [TWN]      │    │   (QGC)      │         │   │
│  │   └──────────────┘    └──────────────┘    └──────────────┘         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  LEGEND: [USA]=United States [AUS]=Australia [CHE]=Switzerland            │
│          [DEU]=Germany [ZAF]=South Africa [TWN]=Taiwan [CZE]=Czech Rep    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Appendix B: Supply Chain Compliance Matrix

| Component | Manufacturer | HQ Location | Mfg Location | NDAA Status |
|-----------|--------------|-------------|--------------|-------------|
| Flight Controller | CubePilot | Australia | Australia | ✓ Compliant |
| GNSS | u-blox | Switzerland | Switzerland | ✓ Compliant |
| Forward Motor | KDE Direct | USA | USA | ✓ Compliant |
| VTOL Motors | KDE Direct | USA | USA | ✓ Compliant |
| All ESCs | KDE Direct | USA | USA | ✓ Compliant |
| Datalink | Doodle Labs | USA | USA | ✓ Compliant |
| EO/IR Gimbal | Teledyne FLIR | USA | USA | ✓ Compliant |
| Companion Computer | NVIDIA | USA | Taiwan | ✓ Compliant |
| Batteries | MaxAmps | USA | USA | ✓ Compliant |
| GCS Tablet | Getac | Taiwan | Taiwan | ✓ Compliant |
| Airspeed Sensor | TE Connectivity | USA | USA | ✓ Compliant |
| ADS-B/Remote ID | uAvionix | USA | USA | ✓ Compliant |
| Rangefinder | LightWare | South Africa | South Africa | ✓ Compliant |
| Power Distribution | Mauch | Germany | Germany | ✓ Compliant |
| Propellers (fwd) | Mejzlik | Czech Republic | Czech Republic | ✓ Compliant |
| Propellers (VTOL) | KDE Direct | USA | USA | ✓ Compliant |
| Servos | KST | Taiwan | Taiwan | ✓ Compliant |
| Antennas | Taoglas | Ireland | Ireland | ✓ Compliant |

### Appendix C: Acronyms

| Acronym | Definition |
|---------|------------|
| ADS-B | Automatic Dependent Surveillance-Broadcast |
| AES | Advanced Encryption Standard |
| AGL | Above Ground Level |
| BDA | Battle Damage Assessment |
| BEC | Battery Eliminator Circuit |
| BOM | Bill of Materials |
| C2 | Command and Control |
| CEP | Circular Error Probable |
| CDR | Critical Design Review |
| COA | Certificate of Authorization |
| DFARS | Defense Federal Acquisition Regulation Supplement |
| EO/IR | Electro-Optical/Infrared |
| ESC | Electronic Speed Controller |
| FAA | Federal Aviation Administration |
| FMEA | Failure Mode and Effects Analysis |
| GCS | Ground Control Station |
| GNSS | Global Navigation Satellite System |
| GPS | Global Positioning System |
| IMU | Inertial Measurement Unit |
| ISR | Intelligence, Surveillance, Reconnaissance |
| ITAR | International Traffic in Arms Regulations |
| LRIP | Low-Rate Initial Production |
| LOS | Line of Sight |
| LWIR | Long-Wave Infrared |
| MAVLink | Micro Air Vehicle Link |
| MGTOW | Maximum Gross Takeoff Weight |
| MIL-STD | Military Standard |
| MSL | Mean Sea Level |
| MTBF | Mean Time Between Failures |
| MTTR | Mean Time to Repair |
| NDAA | National Defense Authorization Act |
| NETD | Noise Equivalent Temperature Difference |
| NRE | Non-Recurring Engineering |
| NVMe | Non-Volatile Memory Express |
| PDB | Power Distribution Board |
| PDR | Preliminary Design Review |
| RTK | Real-Time Kinematic |
| RTL | Return to Launch |
| SBOM | Software Bill of Materials |
| SIGINT | Signals Intelligence |
| STANAG | Standardization Agreement (NATO) |
| sUAS | Small Unmanned Aircraft System |
| TRD | Technical Requirements Document |
| VIO | Visual-Inertial Odometry |
| VTOL | Vertical Takeoff and Landing |

---
