# Multi-Frame Super-Resolution for MWIR Aerial Imaging

## Mathematical Recovery Process for Object Identification at 8,000 ft AGL

### Teledyne FLIR Neutrino LC – CZ 15-300

---

## 1. System Specifications

### 1.1 Camera Parameters

| Parameter | Value |
|-----------|-------|
| Model | 425-0065-00 |
| Sensor Resolution | 640 × 512 pixels |
| Pixel Pitch | 15 µm |
| Spectral Band | 3.4 – 5.1 µm (MWIR) |
| Sensitivity (NEdT) | < 30 mK |
| EFL Zoom Range | 15 – 300 mm |
| Aperture | f/4 |
| Frame Rate | 60 Hz (adjustable 1–60 Hz) |
| HFOV Range | 1.8° – 35.5° |
| Output | CMOS (16-bit, 8-bit) |

### 1.2 Manufacturer DRI Specifications (NATO Standard)

| Task | Range (50% Probability) |
|------|-------------------------|
| Detection | 16.2 km |
| Recognition | 6.4 km |
| Identification | 5.0 km |

*Note: These are manufacturer specifications for a 2.3m × 2.3m standard NATO target with ΔT = 2°C.*

---

## 2. Problem Statement

**Objective**: Achieve reliable object identification from 8,000 ft AGL (2,438 m slant range) using multi-frame super-resolution to computationally enhance the native sensor resolution.

**Question**: Can we reliably identify targets (vehicles, persons, objects) at 8,000 ft when the native optical resolution may be insufficient?

---

## 3. Johnson Criteria Analysis

### 3.1 Required Cycles for Task Performance

| Task | Cycles Across Target (N50) |
|------|---------------------------|
| Detection | 1.0 ± 0.25 |
| Orientation | 1.4 ± 0.35 |
| Recognition | 4.0 ± 0.8 |
| Identification | 6.4 ± 1.5 |

A "cycle" consists of one line pair (one light bar + one dark bar). For thermal imaging, this translates to one hot-cold transition pair.

### 3.2 IFOV Calculation

The Instantaneous Field of View (IFOV) determines the angular extent each pixel subtends:

$$\text{IFOV} = \frac{\text{Pixel Pitch}}{\text{Focal Length}} = \frac{p}{f}$$

For the Neutrino LC CZ 15-300:

| Focal Length | IFOV (µrad) | IFOV (mrad) |
|--------------|-------------|-------------|
| 15 mm | 1000 | 1.000 |
| 50 mm | 300 | 0.300 |
| 100 mm | 150 | 0.150 |
| 200 mm | 75 | 0.075 |
| 300 mm | 50 | 0.050 |

### 3.3 Ground Sample Distance (GSD) at 8,000 ft AGL

The GSD represents the physical size each pixel covers on the ground:

$$\text{GSD} = \text{IFOV} \times R = \frac{p \times R}{f}$$

Where:
- $p$ = 15 µm (pixel pitch)
- $R$ = 2,438 m (slant range at 8,000 ft)
- $f$ = focal length

| Focal Length | GSD (m) | GSD (cm) |
|--------------|---------|----------|
| 15 mm | 2.438 | 243.8 |
| 50 mm | 0.731 | 73.1 |
| 100 mm | 0.366 | 36.6 |
| 200 mm | 0.183 | 18.3 |
| 300 mm | 0.122 | 12.2 |

### 3.4 Target Resolution Requirements

For identification (6.4 cycles), assuming Nyquist sampling (2.5 pixels per cycle):

$$\text{Pixels Required} = 6.4 \times 2.5 = 16 \text{ pixels across target}$$

**Example: Vehicle Identification (2m critical dimension)**

| Focal Length | GSD (cm) | Pixels on 2m Target | Identification Capable? |
|--------------|----------|---------------------|------------------------|
| 15 mm | 243.8 | 0.8 | No |
| 50 mm | 73.1 | 2.7 | No |
| 100 mm | 36.6 | 5.5 | No |
| 200 mm | 18.3 | 10.9 | Marginal |
| 300 mm | 12.2 | 16.4 | Yes |

**Finding**: At 8,000 ft AGL with native resolution, full zoom (300mm) is required for vehicle identification. Super-resolution can relax this requirement.

---

## 4. Super-Resolution Theory

### 4.1 Fundamentals

Multi-frame super-resolution exploits sub-pixel shifts between frames to reconstruct a higher-resolution image than any single frame contains.

Given $K$ low-resolution frames $\{y_1, y_2, y_K\}$, each related to the high-resolution image $x$ by:

$$y_k = D \cdot B \cdot M_k \cdot x + n_k$$

Where:
- $D$ = decimation (downsampling) matrix.
- $B$ = blur kernel (optical PSF + motion blur).
- $M_k$ = motion/warp matrix for frame $k$.
- $n_k$ = noise in frame $k$.

### 4.2 Information Theoretic Basis

Achievable resolution gain depends on:

1. **Sub-pixel shift diversity**: Frames must sample different phase positions.
2. **Signal-to-noise ratio**: Higher SNR enables more aggressive reconstruction.
3. **Number of frames**: More frames provide more constraints.
4. **Motion model accuracy**: Errors in $M_k$ create artifacts.

**Maximum Gain**: For $K$ frames with uniformly distributed sub-pixel shifts:

$$\text{Resolution Gain} \leq \sqrt{K}$$

In practice, 2× linear improvement (4× pixel count) is reliably achievable with 10-30 frames.

### 4.3 Cramér-Rao Lower Bound

The minimum variance achievable for super-resolution estimation:

$$\text{Var}(\hat{x}) \geq \frac{\sigma_n^2}{K \cdot \text{MTF}^2(f)}$$

Where:
- $\sigma_n^2$ = noise variance.
- $K$ = number of frames.
- $\text{MTF}(f)$ = system modulation transfer function at spatial frequency $f$.

This bounds the achievable resolution enhancement for a given noise level and frame count.

---

## 5. System MTF Characterization

### 5.1 MTF Components

The system MTF is the product of all contributing factors:

$$\text{MTF}_{\text{system}} = \text{MTF}_{\text{optics}} \times \text{MTF}_{\text{detector}} \times \text{MTF}_{\text{atmosphere}} \times \text{MTF}_{\text{motion}}$$

### 5.2 Optical MTF

Diffraction-limited MTF for a circular aperture:

$$\text{MTF}_{\text{diff}}(\nu) = \frac{2}{\pi}\left[\cos^{-1}\left(\frac{\nu}{\nu_c}\right) - \frac{\nu}{\nu_c}\sqrt{1 - \left(\frac{\nu}{\nu_c}\right)^2}\right]$$

Where cutoff frequency:
$$\nu_c = \frac{D}{\lambda \cdot f} = \frac{1}{\lambda \cdot F/}$$

For f/4 at λ = 4.0 µm (mid-MWIR):
$$\nu_c = \frac{1}{4.0 \mu m \times 4} = 62.5 \text{ cycles/mm}$$

### 5.3 Detector MTF

Pixel aperture MTF (sinc function):

$$\text{MTF}_{\text{pixel}}(\nu) = \text{sinc}\left(\frac{\nu \cdot p}{1}\right) = \frac{\sin(\pi \nu p)}{\pi \nu p}$$

At Nyquist frequency ($\nu_{Nyquist} = \frac{1}{2p} = 33.3$ cycles/mm for 15 µm pixels):

$$\text{MTF}_{\text{pixel}}(\nu_{Nyquist}) = \text{sinc}(0.5) \approx 0.64$$

### 5.4 Atmospheric MTF

For thermal imaging through atmosphere:

$$\text{MTF}_{\text{atm}}(\nu) = \exp\left[-3.44\left(\frac{\lambda \cdot \nu \cdot R}{r_0}\right)^{5/3}\right]$$

Where $r_0$ is the Fried parameter (atmospheric coherence length).

**Fried Parameter Estimation**:

$$r_0 = \left[0.423 \cdot k^2 \cdot \sec(\zeta) \cdot \int_0^L C_n^2(z) \, dz\right]^{-3/5}$$

Typical values:
- Good conditions (stable atmosphere): $r_0$ = 10-20 cm.
- Moderate conditions: $r_0$ = 5-10 cm.
- Poor conditions (strong turbulence): $r_0$ = 2-5 cm.

### 5.5 Motion MTF

For linear motion during exposure:

$$\text{MTF}_{\text{motion}}(\nu) = \text{sinc}(\nu \cdot v \cdot t_{exp})$$

Where:
- $v$ = angular velocity (rad/s).
- $t_{exp}$ = exposure time.

**Design Rule**: Keep motion blur < 0.5 pixels during exposure.

For 15 µm pixels at 300mm focal length:
$$\theta_{pixel} = \frac{15 \mu m}{300 mm} = 50 \mu rad$$

Maximum allowable angular rate for 1/60s exposure:
$$\omega_{max} = \frac{0.5 \times 50 \mu rad}{1/60 s} = 1.5 \text{ mrad/s} = 0.086 \text{ °/s}$$

---

## 6. IMU-Fused Motion Estimation

### 6.1 Motion Model

Platform motion between frames consists of:

$$\mathbf{M}_k = \mathbf{R}(\theta_k) \cdot \mathbf{T}(t_k) + \mathbf{v}_k$$

Where:
- $\mathbf{R}(\theta_k)$ = rotation matrix (roll, pitch, yaw).
- $\mathbf{T}(t_k)$ = translation vector.
- $\mathbf{v}_k$ = residual vibration/jitter.

### 6.2 IMU Integration

Gyroscope data provides angular rates $\boldsymbol{\omega}(t) = [\omega_x, \omega_y, \omega_z]^T$.

Rotation between frames $k$ and $k+1$:

$$\boldsymbol{\theta}_{k \to k+1} = \int_{t_k}^{t_{k+1}} \boldsymbol{\omega}(t) \, dt$$

For small angles, the rotation matrix:

$$\mathbf{R} \approx \mathbf{I} + [\boldsymbol{\theta}]_\times$$

Where $[\boldsymbol{\theta}]_\times$ is the skew-symmetric matrix of $\boldsymbol{\theta}$.

### 6.3 Image-to-IMU Alignment Refinement

IMU provides an initial estimate; image-based refinement corrects residual errors.

**Objective**:

$$\hat{\mathbf{M}}_k = \arg\min_{\mathbf{M}_k} \sum_i \rho\left(\|I_k(\mathbf{M}_k \cdot \mathbf{p}_i) - I_{ref}(\mathbf{p}_i)\|^2\right)$$

Where:
- $I_k$, $I_{ref}$ = frame $k$ and reference frame.
- $\mathbf{p}_i$ = feature/pixel locations.
- $\rho(\cdot)$ = robust loss function (Huber, Cauchy).

### 6.4 Time Synchronization Requirements

Synchronization error $\Delta t$ causes angular error:
$$\theta_{error} = \omega \cdot \Delta t$$

For 1° /s rotation and 0.5 pixel tolerance:
$$\Delta t_{max} = \frac{0.5 \times 50 \mu rad}{17.5 \text{ mrad/s}} \approx 1.4 \text{ ms}$$

**Requirement**: Camera-IMU synchronization better than 1 ms.

---

## 7. Super-Resolution Algorithm

### 7.1 Forward Model

The imaging process maps high-resolution scene $x$ to observed frames $\{y_k\}$:

$$y_k = H_k x + n_k$$

Where $H_k = D \cdot B \cdot W_k$ combines:
- $W_k$ = warp/motion operator for frame $k$.
- $B$ = blur operator (PSF).
- $D$ = downsampling operator.

### 7.2 Maximum A Posteriori (MAP) Estimation

Reconstruct $x$ by minimizing:

$$\hat{x} = \arg\min_x \left\{ \sum_{k=1}^{K} \|y_k - H_k x\|^2 + \lambda \cdot R(x) \right\}$$

Where:
- First term: data fidelity.
- $R(x)$: regularization prior.
- $\lambda$: regularization weight.

### 7.3 Regularization Options

**Total Variation (TV)**:
$$R_{TV}(x) = \sum_i \|\nabla x_i\|_1$$

Promotes piecewise-smooth solutions, good for edges.

**Bilateral Total Variation (BTV)**:
$$R_{BTV}(x) = \sum_i \sum_{m=-P}^{P} \sum_{n=-P}^{P} \alpha^{|m|+|n|} \|x_i - S_x^m S_y^n x_i\|_1$$

Better preserves fine detail.

**Learned Prior (Deep Network)**:
$$R_{learned}(x) = \|x - f_\theta(x)\|^2$$

Where $f_\theta$ is a denoising neural network.

### 7.4 Iterative Solution

**Iterative Back-Projection (IBP)**:

```
Initialize: x⁽⁰⁾ = bicubic upsampling of median frame
For iteration t = 1 to T:
    For each frame k:
        e_k = y_k - H_k x⁽ᵗ⁻¹⁾           # Compute residual
        Δx_k = H_k^T e_k                    # Back-project error
    x⁽ᵗ⁾ = x⁽ᵗ⁻¹⁾ + β ∑_k Δx_k - λ∇R(x⁽ᵗ⁻¹⁾)   # Update with regularization
```

**Convergence**: 20-50 iterations.

### 7.5 Computational Complexity

Per iteration:
- Forward projection: $O(K \cdot N^2)$ where $N^2$ is HR image size.
- Back projection: $O(K \cdot N^2)$.
- Regularization gradient: $O(N^2)$.

Total: $O(T \cdot K \cdot N^2)$

For 2× super-resolution (1280×1024 output), 20 frames, 30 iterations:
$$\approx 30 \times 20 \times 1.3\text{M} = 780\text{M operations per frame}$$

Achievable at ~10 Hz on embedded GPU (Jetson Orin).

---

## 8. Atmospheric Compensation

### 8.1 Turbulence Effects

Atmospheric turbulence causes:
1. **Blur**: Random wavefront distortion.
2. **Warping**: Spatially-varying image shift.
3. **Scintillation**: Intensity fluctuations.

### 8.2 Lucky Imaging Integration

Exploit temporal variation in turbulence quality:

1. **Quality metric**: Compute sharpness metric for each frame
   $$Q_k = \sum_{i,j} |\nabla I_k(i,j)|^2$$

2. **Frame selection**: Use the top 10-30% highest quality frames

3. **Weighted fusion**: Weight frames by quality in SR reconstruction
   $$\hat{x} = \arg\min_x \sum_k w_k \|y_k - H_k x\|^2$$

### 8.3 Isoplanatic Patch Processing

When the field of view exceeds the isoplanatic angle $\theta_0$:

1. Divide the image into patches smaller than $\theta_0$.
2. Estimate motion independently per patch.
3. Reconstruct patches separately.
4. Blend overlapping regions.

**Isoplanatic angle estimation**:
$$\theta_0 \approx 0.31 \frac{r_0}{h}$$

For $r_0$ = 10 cm and $h$ = 2,438 m:
$$\theta_0 \approx 12.7 \mu rad \approx 0.25 \text{ pixels at 300mm}$$

This is a small atmospheric correlation limited to these ranges.

---

## 9. Implementation Pipeline

### 9.1 Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Camera Input   │────▶│  Frame Buffer    │────▶│  Motion Est.    │
│  (60 Hz, 14-bit)│     │  (20-30 frames)  │     │  (IMU + Image)  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐     ┌────────▼────────┐
│  Enhanced Out   │◀────│  Post-Process    │◀────│  SR Algorithm   │
│  (10 Hz, 16-bit)│     │  (Sharpen, AGC)  │     │  (MAP + BTV)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### 9.2 Timing Budget (Target: 100ms per output frame)

| Stage | Time (ms) |
|-------|-----------|
| Frame acquisition (20 frames) | 333 ms (overlapped) |
| IMU integration | 2 |
| Image-based refinement | 15 |
| SR reconstruction (30 iter) | 70 |
| Post-processing | 8 |
| Output formatting | 5 |
| **Total** | **~100 ms** |

### 9.3 Memory Requirements

| Buffer | Size |
|--------|------|
| Input frame buffer (20 × 640×512 × 16-bit) | 13.1 MB |
| HR reconstruction (1280×1024 × 32-bit) | 5.2 MB |
| Motion matrices (20 × 3×3 × 64-bit) | 2.9 KB |
| Algorithm workspace | ~20 MB |
| **Total** | **~40 MB** |

---

## 10. Performance Projections

### 10.1 Resolution Enhancement

With reliable 2× super-resolution:

| Focal Length | Native GSD (cm) | Enhanced GSD (cm) | Pixels on 2m Target (Enhanced) |
|--------------|-----------------|-------------------|--------------------------------|
| 100 mm | 36.6 | 18.3 | 10.9 |
| 150 mm | 24.4 | 12.2 | 16.4 |
| 200 mm | 18.3 | 9.15 | 21.9 |
| 300 mm | 12.2 | 6.1 | 32.8 |

**Finding**: With 2× super-resolution, 150mm focal length achieves identification capability equivalent to native 300mm.

### 10.2 Johnson Criteria Compliance (8,000 ft AGL, 2m Vehicle)

| Configuration | Native Cycles | Enhanced Cycles (2×) | Identification Capable? |
|---------------|---------------|----------------------|------------------------|
| 100mm native | 2.7 | 5.4 | Marginal |
| 150mm native | 4.1 | 8.2 | Yes |
| 200mm native | 5.5 | 10.9 | Yes (robust) |
| 300mm native | 8.2 | 16.4 | Yes (significant margin) |

### 10.3 SNR Requirements

For reliable 2× super-resolution with MAP-BTV algorithm:

| SNR (dB) | Expected Resolution Gain | Quality |
|----------|-------------------------|---------|
| < 15 | 1.2–1.4× | Poor |
| 15–20 | 1.4–1.7× | Acceptable |
| 20–25 | 1.7–2.0× | Good |
| > 25 | 2.0× | Excellent |

**Neutrino LC SNR Estimate** (scene ΔT = 2°C, NEdT = 30 mK):
$$\text{SNR} = \frac{\Delta T}{\text{NEdT}} = \frac{2000 \text{ mK}}{30 \text{ mK}} \approx 67 \approx 36 \text{ dB}$$

This is excellent SNR for super-resolution.

---

## 11. Validation Protocol

### 11.1 Ground Truth

1. **Resolution targets**: Place calibrated bar targets at known distances.
   - 4-bar MRTD targets at 8,000 ft equivalent angular size.
   - Minimum Resolvable Temperature Difference (MRTD) characterization.

2. **Reference imagery**: Acquire simultaneous imagery froa m calibrated reference system

3. **Controlled motion**: Use a precision gimbal to generate known sub-pixel shifts

### 11.2 Metrics

**MTF Measurement**:
$$\text{MTF}(f) = \frac{\text{Contrast at frequency } f}{\text{Contrast at DC}}$$

**Effective Resolution**:
- MTF50: Frequency at which MTF = 0.5
- MTF30: Frequency at which MTF = 0.3

**Super-Resolution Gain**:
$$G_{SR} = \frac{\text{MTF50}_{\text{enhanced}}}{\text{MTF50}_{\text{native}}}$$

### 11.3 Acceptance Criteria

| Metric | Threshold |
|--------|-----------|
| Resolution gain (MTF50 ratio) | ≥ 1.8× |
| Artifact level | < 5% false edge rate |
| Temporal consistency | < 2% frame-to-frame variation |
| Processing latency | < 150 ms |

---

## 12. Hardware Integration Checklist

### 12.1 Camera Interface

- [ ] Camera Link or GigE interface configured.
- [ ] 14-bit or 16-bit raw data capture enabled.
- [ ] Hardware trigger output connected to IMU.
- [ ] NUC tables loaded and verified.
- [ ] Frame rate set to 60 Hz.

### 12.2 IMU Requirements

- [ ] Sample rate ≥ 800 Hz.
- [ ] Gyro bias stability < 1°/hr.
- [ ] Accelerometer noise < 100 µg/√Hz.
- [ ] Hardware timestamp synchronization < 1 ms.
- [ ] Rigid mounting to camera body.

### 12.3 Processing Hardware

- [ ] GPU compute capability ≥ 7.0 (Jetson Orin recommended).
- [ ] Memory bandwidth ≥ 100 GB/s.
- [ ] Storage: NVMe SSD for raw data logging.
- [ ] Power: 25-40W budget for compute module.

### 12.4 Software Stack

- [ ] CUDA/TensorRT for GPU acceleration.
- [ ] OpenCV for image processing primitives.
- [ ] Eigen for linear algebra.
- [ ] Custom SR kernel optimized for target resolution.

---

## 13. Summary

### 13.1 Parameters

| Parameter | Value |
|-----------|-------|
| Operating Altitude | 8,000 ft AGL (2,438 m) |
| Target Focal Length | 150–300 mm |
| Native GSD @ 300mm | 12.2 cm |
| Enhanced GSD @ 300mm (2× SR) | 6.1 cm |
| Frame Rate | 60 Hz input, 10 Hz output |
| Processing Latency | < 100 ms |
| Resolution Gain | 2× (target), 1.8× (minimum) |

### 13.2 Operational Envelope

**Identification Capable**:
- Focal length ≥ 150mm with 2× super-resolution.
- Focal length ≥ 300mm without super-resolution.
- Scene ΔT ≥ 1°C for adequate SNR.
- Platform angular rate < 2°/s for motion blur control.

**Degraded Performance Expected**:
- Strong atmospheric turbulence ($r_0$ < 5 cm).
- Low scene contrast (ΔT < 0.5°C).
- Rapid platform motion (> 5°/s).

### 13.3 Workflow Summary

1. **Acquire**: Capture 20-30 frames at 60 Hz (333-500 ms).
2. **Estimate Motion**: Integrate IMU, refine with image alignment.
3. **Quality Select**: Rank frames, weight by sharpness.
4. **Reconstruct**: MAP estimation with BTV regularization (30 iterations).
5. **Validate**: Check consistency, flag low-confidence regions.
6. **Output**: Enhanced frame at 10 Hz.

---

## Appendix A: Mathematical Notation Reference

| Symbol | Definition | Units |
|--------|------------|-------|
| $p$ | Pixel pitch | µm |
| $f$ | Focal length | mm |
| $R$ | Slant range | m |
| $\lambda$ | Wavelength | µm |
| $r_0$ | Fried parameter | cm |
| $\theta_0$ | Isoplanatic angle | µrad |
| $\tau_0$ | Coherence time | ms |
| $C_n^2$ | Refractive index structure constant | m^(-2/3) |
| IFOV | Instantaneous Field of View | µrad |
| GSD | Ground Sample Distance | cm |
| NEdT | Noise Equivalent Temperature Difference | mK |
| MTF | Modulation Transfer Function | dimensionless |
| SNR | Signal-to-Noise Ratio | dB |

---

## Appendix B: Quick Reference Calculations

### B.1 IFOV Calculator
```
IFOV (µrad) = Pixel Pitch (µm) × 1000 / Focal Length (mm)

Example: 15 µm / 300 mm = 50 µrad
```

### B.2 GSD Calculator
```
GSD (m) = IFOV (rad) × Range (m)
GSD (m) = Pixel Pitch (m) × Range (m) / Focal Length (m)

Example: (15×10⁻⁶ m) × (2438 m) / (0.3 m) = 0.122 m = 12.2 cm
```

### B.3 Pixels on Target
```
Pixels = Target Size (m) / GSD (m)

Example: 2 m / 0.122 m = 16.4 pixels
```

### B.4 Johnson Criteria Check
```
Cycles on Target = Pixels on Target / 2.5

Identification requires ≥ 6.4 cycles
Recognition requires ≥ 4.0 cycles
```

---

*Document Version: 1.1*
*Date: December 2025*
*Platform: Teledyne FLIR Neutrino LC – CZ 15-300 (425-0065-00)*
*Application: High-Altitude MWIR Imaging with Computational Enhancement*
