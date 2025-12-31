# Multi-Frame Super-Resolution for MWIR Aerial Imaging

## Mathematical Recovery Process for Target Identification at 8,000 ft AGL

### Teledyne FLIR Neutrino LC – CZ 15-300

---

## Executive Summary

This document presents a mathematical framework for achieving reliable target identification from 8,000 ft AGL using the Teledyne FLIR Neutrino LC CZ 15-300 MWIR camera with computational super-resolution enhancement.

**Findings:**

- Native 300mm focal length is required for vehicle identification at 8,000 ft without computational enhancement.
- With reliable 2× super-resolution, identification capability is achieved at 150mm focal length, providing wider field of view for target acquisition.
- The Neutrino LC's excellent SNR (~36 dB for ΔT = 2°C scenes) supports robust super-resolution reconstruction.
- IMU-camera synchronization better than 1 ms is required for accurate motion estimation.
- Real-time processing at 10 Hz output is achievable on embedded GPU platforms (e.g., NVIDIA Jetson Orin).
- Atmospheric turbulence is the primary limiting factor at these ranges, requiring lucky imaging and patch-based processing.

---

## Glossary of  Terms

| Term | Definition |
|------|------------|
| **IFOV** | Instantaneous Field of View—the angular extent subtended by a single pixel. |
| **GSD** | Ground Sample Distance—the physical size on the ground that one pixel represents. |
| **NEdT** | Noise Equivalent Temperature Difference—the minimum temperature difference the sensor can detect. |
| **MTF** | Modulation Transfer Function—a measure of how well the system preserves contrast at different spatial frequencies. |
| **Fried Parameter (r₀)** | Atmospheric coherence length—the diameter over which wavefront distortion remains correlated. |
| **Isoplanatic Angle (θ₀)** | The angular region over which atmospheric distortion is approximately uniform, allowing a single correction to apply. |
| **Johnson Criteria** | Empirically-derived standards specifying how many resolution cycles across a target are needed for detection, recognition, and identification tasks. |
| **Nyquist Frequency** | The maximum spatial frequency that can be sampled without aliasing, equal to 1/(2 × pixel pitch). |
| **MAP Estimation** | Maximum A Posteriori estimation—a Bayesian approach that finds the most probable solution given observed data and prior assumptions. |
| **Regularization** | Mathematical constraints added to inverse problems to prevent noise amplification and ensure stable solutions. |

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

These manufacturer specifications assume a 2.3m × 2.3m standard NATO target with ΔT = 2°C thermal contrast.

---

## 2. Problem Statement

**Objective:** Achieve reliable target identification from 8,000 ft AGL (2,438 m slant range) using multi-frame super-resolution to computationally enhance the native sensor resolution.

** Question:** Can we reliably identify targets (vehicles, persons, objects) at 8,000 ft when the native optical resolution may be insufficient?

**Approach:** Exploit sub-pixel motion between frames to reconstruct imagery at higher resolution than any single frame contains, effectively trading temporal samples for spatial resolution.

---

## 3. Johnson Criteria Analysis

### 3.1 Required Cycles for Task Performance

The Johnson Criteria, developed empirically at the U.S. Army Night Vision Laboratory in the 1950s, define the minimum resolvable cycles (line pairs) across a target's critical dimension needed to perform specific tasks with 50% probability.

| Task | Cycles Across Target (N50) |
|------|---------------------------|
| Detection | 1.0 ± 0.25 |
| Orientation | 1.4 ± 0.35 |
| Recognition | 4.0 ± 0.8 |
| Identification | 6.4 ± 1.5 |

A "cycle" consists of one line pair (one light bar plus one dark bar). For thermal imaging, this translates to one hot-cold transition pair across the target.

### 3.2 IFOV Calculation

The Instantaneous Field of View (IFOV) determines the angular extent each pixel subtends:

$$\text{IFOV} = \frac{\text{Pixel Pitch}}{\text{Focal Length}} = \frac{p}{f}$$

This relationship shows that longer focal lengths yield smaller IFOVs, enabling finer angular resolution. For the Neutrino LC CZ 15-300:

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
- $p$ = 15 µm (pixel pitch).
- $R$ = 2,438 m (slant range at 8,000 ft).
- $f$ = focal length.

| Focal Length | GSD (m) | GSD (cm) |
|--------------|---------|----------|
| 15 mm | 2.438 | 243.8 |
| 50 mm | 0.731 | 73.1 |
| 100 mm | 0.366 | 36.6 |
| 200 mm | 0.183 | 18.3 |
| 300 mm | 0.122 | 12.2 |

### 3.4 Target Resolution Requirements

For identification (6.4 cycles), assuming Nyquist sampling (2.5 pixels per cycle for robust detection):

$$\text{Pixels Required} = 6.4 \times 2.5 = 16 \text{ pixels across target}$$

**Example: Vehicle Identification (2m critical dimension)**

| Focal Length | GSD (cm) | Pixels on 2m Target | Identification Capable? |
|--------------|----------|---------------------|------------------------|
| 15 mm | 243.8 | 0.8 | No |
| 50 mm | 73.1 | 2.7 | No |
| 100 mm | 36.6 | 5.5 | No |
| 200 mm | 18.3 | 10.9 | Marginal |
| 300 mm | 12.2 | 16.4 | Yes |

**Critical Finding:** At 8,000 ft AGL with native resolution, full zoom (300mm) is required for vehicle identification. Super-resolution can relax this requirement significantly.

---

## 4. Super-Resolution Theory

### 4.1 Fundamental Principle

Traditional imaging captures a single snapshot, limited by the sensor's pixel count. Multi-frame super-resolution exploits sub-pixel shifts between frames to reconstruct a higher-resolution image than any single frame contains. When the camera moves by fractional pixel amounts between exposures, each frame samples different points in the continuous scene, providing complementary information.

Given $K$ low-resolution frames $\{y_1, y_2, ..., y_K\}$, each is related to the high-resolution image $x$ by:

$$y_k = D \cdot B \cdot M_k \cdot x + n_k$$

Where:
- $D$ = decimation (downsampling) matrix.
- $B$ = blur kernel (optical PSF plus motion blur).
- $M_k$ = motion/warp matrix for frame $k$.
- $n_k$ = noise in frame $k$.

The super-resolution problem inverts this model to recover $x$ from the observed $\{y_k\}$.

### 4.2 Information-Theoretic Basis

The achievable resolution gain depends on several factors:

1. **Sub-pixel shift diversity:** Frames must sample different phase positions relative to the pixel grid.
2. **Signal-to-noise ratio:** Higher SNR enables more aggressive reconstruction without noise amplification.
3. **Number of frames:** More frames provide more constraints on the solution.
4. **Motion model accuracy:** Errors in $M_k$ estimation create reconstruction artifacts.

**Theoretical Maximum Gain:** For $K$ frames with uniformly distributed sub-pixel shifts:

$$\text{Resolution Gain} \leq \sqrt{K}$$

In practice, 2× linear improvement (4× pixel count) is reliably achievable with 10-30 frames under good conditions. Real-world factors such as correlated noise, non-ideal shift distributions, and motion model errors typically limit gains to 1.5-2× in operational systems.

### 4.3 Cramér-Rao Lower Bound

The Cramér-Rao Lower Bound (CRLB) provides the minimum variance achievable for any unbiased estimator of the super-resolved image:

$$\text{Var}(\hat{x}) \geq \frac{\sigma_n^2}{K \cdot \text{MTF}^2(f)}$$

Where:
- $\sigma_n^2$ = noise variance.
- $K$ = number of frames.
- $\text{MTF}(f)$ = system modulation transfer function at spatial frequency $f$.

This bound shows that resolution enhancement becomes increasingly difficult at high spatial frequencies where MTF approaches zero. The CRLB assumes unbiased estimation; regularized methods (Section 7.3) introduce controlled bias to reduce variance, often achieving better overall performance.

---

## 5. System MTF Characterization

### 5.1 MTF Components

The system MTF is the product of all contributing factors:

$$\text{MTF}_{\text{system}} = \text{MTF}_{\text{optics}} \times \text{MTF}_{\text{detector}} \times \text{MTF}_{\text{atmosphere}} \times \text{MTF}_{\text{motion}}$$

Each component independently degrades spatial frequency content, and their cumulative effect determines the system's resolving power. Understanding each component enables targeted improvements.

*[Figure recommended: Plot showing individual MTF components and their product versus spatial frequency.]*

### 5.2 Optical MTF

Diffraction-limited MTF for a circular aperture follows:

$$\text{MTF}_{\text{diff}}(\nu) = \frac{2}{\pi}\left[\cos^{-1}\left(\frac{\nu}{\nu_c}\right) - \frac{\nu}{\nu_c}\sqrt{1 - \left(\frac{\nu}{\nu_c}\right)^2}\right]$$

Where cutoff frequency is:
$$\nu_c = \frac{D}{\lambda \cdot f} = \frac{1}{\lambda \cdot F/\#}$$

This equation shows that MTF rolls off gradually, reaching zero at the cutoff frequency where diffraction prevents any contrast transfer.

For f/4 at λ = 4.0 µm (mid-MWIR):
$$\nu_c = \frac{1}{4.0 \, \mu m \times 4} = 62.5 \text{ cycles/mm}$$

### 5.3 Detector MTF

The finite pixel size acts as a spatial averaging filter, described by the pixel aperture MTF (sinc function):

$$\text{MTF}_{\text{pixel}}(\nu) = \text{sinc}\left(\frac{\nu \cdot p}{1}\right) = \frac{\sin(\pi \nu p)}{\pi \nu p}$$

At Nyquist frequency ($\nu_{Nyquist} = \frac{1}{2p} = 33.3$ cycles/mm for 15 µm pixels):

$$\text{MTF}_{\text{pixel}}(\nu_{Nyquist}) = \text{sinc}(0.5) \approx 0.64$$

This 36% contrast loss at Nyquist is inherent to sampled imaging systems and cannot be recovered without super-resolution techniques.

### 5.4 Atmospheric MTF

For thermal imaging through atmosphere, turbulence degrades resolution according to:

$$\text{MTF}_{\text{atm}}(\nu) = \exp\left[-3.44\left(\frac{\lambda \cdot \nu \cdot R}{r_0}\right)^{5/3}\right]$$

This equation shows exponential decay with turbulence strength (smaller $r_0$), limiting high-frequency content. The formula assumes long-exposure averaging; at 60 Hz frame rates, individual frames may show better instantaneous resolution but with spatially-varying distortion.

Where $r_0$ is the Fried parameter (atmospheric coherence length), representing the diameter over which the wavefront remains correlated.

**Fried Parameter Estimation:**

$$r_0 = \left[0.423 \cdot k^2 \cdot \sec(\zeta) \cdot \int_0^L C_n^2(z) \, dz\right]^{-3/5}$$

Typical values:
- Good conditions (stable atmosphere): $r_0$ = 10-20 cm.
- Moderate conditions: $r_0$ = 5-10 cm.
- Poor conditions (strong turbulence): $r_0$ = 2-5 cm.

### 5.5 Motion MTF

For linear motion during exposure, the blur kernel produces:

$$\text{MTF}_{\text{motion}}(\nu) = \text{sinc}(\nu \cdot v \cdot t_{exp})$$

Where:
- $v$ = angular velocity (rad/s).
- $t_{exp}$ = exposure time.

**Design Rule:** Keep motion blur < 0.5 pixels during exposure to preserve high-frequency content.

For 15 µm pixels at 300mm focal length:
$$\theta_{pixel} = \frac{15 \, \mu m}{300 \, mm} = 50 \, \mu rad$$

Maximum allowable angular rate for 1/60s exposure:
$$\omega_{max} = \frac{0.5 \times 50 \, \mu rad}{1/60 \, s} = 1.5 \text{ mrad/s} = 0.086 \text{ °/s}$$

This is a stringent requirement, highlighting the need for stabilization or computational motion compensation.

---

## 6. IMU-Fused Motion Estimation

### 6.1 Motion Model

Platform motion between frames consists of rotation and translation components:

$$\mathbf{M}_k = \mathbf{R}(\theta_k) \cdot \mathbf{T}(t_k) + \mathbf{v}_k$$

Where:
- $\mathbf{R}(\theta_k)$ = rotation matrix (roll, pitch, yaw).
- $\mathbf{T}(t_k)$ = translation vector.
- $\mathbf{v}_k$ = residual vibration/jitter.

At 8,000 ft range, translation produces negligible parallax (sub-pixel shift requires meters of platform movement), so rotation dominates the inter-frame motion model.

### 6.2 IMU Integration

Gyroscope data provides angular rates $\boldsymbol{\omega}(t) = [\omega_x, \omega_y, \omega_z]^T$ in the sensor frame.

Rotation between frames $k$ and $k+1$:

$$\boldsymbol{\theta}_{k \to k+1} = \int_{t_k}^{t_{k+1}} \boldsymbol{\omega}(t) \, dt$$

For small angles, the rotation matrix approximates as:

$$\mathbf{R} \approx \mathbf{I} + [\boldsymbol{\theta}]_\times$$

Where $[\boldsymbol{\theta}]_\times$ is the skew-symmetric matrix of $\boldsymbol{\theta}$, defined as:

$$[\boldsymbol{\theta}]_\times = \begin{bmatrix} 0 & -\theta_z & \theta_y \\ \theta_z & 0 & -\theta_x \\ -\theta_y & \theta_x & 0 \end{bmatrix}$$

This matrix form converts the cross product operation into matrix multiplication, enabling efficient computation of rotated coordinates.

### 6.3 Image-to-IMU Alignment Refinement

IMU provides an initial motion estimate; image-based refinement corrects residual errors from gyro bias, drift, and timing uncertainty.

**Optimization objective:**

$$\hat{\mathbf{M}}_k = \arg\min_{\mathbf{M}_k} \sum_i \rho\left(\|I_k(\mathbf{M}_k \cdot \mathbf{p}_i) - I_{ref}(\mathbf{p}_i)\|^2\right)$$

Where:
- $I_k$, $I_{ref}$ = frame $k$ and reference frame intensities.
- $\mathbf{p}_i$ = feature/pixel locations.
- $\rho(\cdot)$ = robust loss function.

The robust loss function $\rho(\cdot)$ reduces sensitivity to outliers (occluded regions, moving objects). Common choices include the Huber loss (quadratic for small errors, linear for large) and Cauchy loss (heavy-tailed, more outlier-resistant), which prevent spurious matches from corrupting the motion estimate.

### 6.4 Time Synchronization Requirements

Synchronization error $\Delta t$ between camera and IMU causes angular error:
$$\theta_{error} = \omega \cdot \Delta t$$

For 1°/s rotation (17.45 mrad/s) and 0.5 pixel tolerance (25 µrad at 300mm):
$$\Delta t_{max} = \frac{25 \, \mu rad}{17.45 \text{ mrad/s}} \approx 1.4 \text{ ms}$$

**Requirement:** Camera-IMU synchronization must be better than 1 ms for sub-pixel motion estimation accuracy.

---

## 7. Super-Resolution Algorithm

### 7.1 Forward Model

The imaging process maps high-resolution scene $x$ to observed frames $\{y_k\}$:

$$y_k = H_k x + n_k$$

Where $H_k = D \cdot B \cdot W_k$ combines:
- $W_k$ = warp/motion operator for frame $k$.
- $B$ = blur operator (PSF).
- $D$ = downsampling operator.

This linear model enables tractable optimization approaches for reconstruction.

### 7.2 Maximum A Posteriori (MAP) Estimation

Reconstruct $x$ by minimizing:

$$\hat{x} = \arg\min_x \left\lbrace \sum_{k=1}^{K} \|y_k - H_k x\|^2 + \lambda \cdot R(x) \right\rbrace$$

Where:
- First term: data fidelity (how well the reconstruction explains observations).
- $R(x)$: regularization prior (encodes assumptions about the scene).
- $\lambda$: regularization weight (balances fidelity vs. smoothness).

The regularization term is essential—without it, noise amplification makes the solution unusable.

### 7.3 Regularization Options

**Total Variation (TV):**
$$R_{TV}(x) = \sum_i \|\nabla x_i\|_1$$

TV promotes piecewise-smooth solutions with sharp edges, making it well-suited for man-made objects (vehicles, structures). However, it can create staircase artifacts in smooth regions.

**Bilateral Total Variation (BTV):**
$$R_{BTV}(x) = \sum_i \sum_{m=-P}^{P} \sum_{n=-P}^{P} \alpha^{|m|+|n|} \|x_i - S_x^m S_y^n x_i\|_1$$

BTV considers multiple spatial shifts, better preserving fine detail and textures than standard TV. The decay factor $\alpha$ (typically 0.7-0.9) weights nearby pixels more heavily.

**Learned Prior (Deep Network):**
$$R_{learned}(x) = \|x - f_\theta(x)\|^2$$

Where $f_\theta$ is a denoising neural network trained on representative imagery. Deep learning approaches (e.g., SRGAN, EDSR adapted for MWIR) can capture complex image statistics but require training data and may hallucinate details not present in the input. For safety-critical applications, classical methods with understood failure modes may be preferred.

### 7.4 Iterative Solution

**Iterative Back-Projection (IBP):**

```
Initialize: x⁽⁰⁾ = bicubic upsampling of median frame
Set: β = 0.1 to 0.5 (learning rate), ε = 1e-4 (convergence threshold)

For iteration t = 1 to T_max:
    For each frame k:
        e_k = y_k - H_k x⁽ᵗ⁻¹⁾              # Compute residual error
        Δx_k = H_k^T e_k                     # Back-project error to HR grid
    
    # Compute regularization gradient (for BTV):
    ∇R = Σ_{m,n} α^{|m|+|n|} sign(x - S_x^m S_y^n x)
    
    # Update estimate:
    x⁽ᵗ⁾ = x⁽ᵗ⁻¹⁾ + β Σ_k Δx_k - λ∇R
    
    # Check convergence:
    If ||x⁽ᵗ⁾ - x⁽ᵗ⁻¹⁾||₂ / ||x⁽ᵗ⁻¹⁾||₂ < ε:
        Break

Output: x⁽ᵗ⁾
```

**Parameter Guidelines:**
- Learning rate $\beta$: Start with 0.1; increase to 0.3-0.5 if convergence is slow.
- Regularization weight $\lambda$: 0.01-0.1; higher values produce smoother results.
- Convergence typically occurs within 20-50 iterations.

**Potential Artifacts:** BTV regularization can produce ringing near high-contrast edges if $\lambda$ is too low. TV can create blocky artifacts in textured regions. Monitor convergence and visually inspect results during development.

### 7.5 Computational Complexity

Per iteration:
- Forward projection: $O(K \cdot N^2)$ where $N^2$ is HR image size.
- Back projection: $O(K \cdot N^2)$.
- Regularization gradient: $O(N^2)$.

Total: $O(T \cdot K \cdot N^2)$

For 2× super-resolution (1280×1024 output), 20 frames, 30 iterations:
$$\approx 30 \times 20 \times 1.3\text{M} = 780\text{M operations per frame}$$

This is achievable at ~10 Hz on embedded GPU platforms (e.g., NVIDIA Jetson Orin with ~200 TOPS INT8).

*[Figure recommended: Flowchart showing SR reconstruction pipeline from frame input through motion estimation, alignment, fusion, and output.]*

---

## 8. Atmospheric Compensation

### 8.1 Turbulence Effects

Atmospheric turbulence causes three distinct degradations:
1. **Blur:** Random wavefront distortion spreads point sources.
2. **Warping:** Spatially-varying image shift distorts geometry.
3. **Scintillation:** Intensity fluctuations corrupt radiometric accuracy.

These effects vary temporally, creating opportunities for exploitation through frame selection.

### 8.2 Lucky Imaging Integration

Lucky imaging exploits the fact that turbulence quality varies from frame to frame. Occasionally, atmospheric conditions align favorably, producing sharper instantaneous images.

**Implementation:**

1. **Quality metric:** Compute sharpness metric for each frame.
   $$Q_k = \sum_{i,j} |\nabla I_k(i,j)|^2$$
   Higher gradient magnitude indicates sharper images with more preserved high-frequency content.

2. **Frame selection:** Use top 10-30% highest quality frames for reconstruction.

3. **Weighted fusion:** Weight frames by quality in SR reconstruction.
   $$\hat{x} = \arg\min_x \sum_k w_k \|y_k - H_k x\|^2$$
   Where $w_k \propto Q_k$.

This approach sacrifices some frames but significantly improves output quality in turbulent conditions.

### 8.3 Isoplanatic Patch Processing

The isoplanatic angle $\theta_0$ defines the region over which atmospheric distortion is approximately uniform. When the camera's field of view exceeds $\theta_0$, different image regions experience different distortions, requiring localized processing.

**Isoplanatic angle estimation:**
$$\theta_0 \approx 0.31 \frac{r_0}{h}$$

For $r_0$ = 10 cm and $h$ = 2,438 m:
$$\theta_0 \approx 12.7 \, \mu rad \approx 0.25 \text{ pixels at 300mm}$$

This extremely small value indicates that atmospheric correlation is very limited at these ranges—effectively, each pixel experiences nearly independent distortion.

**Patch-Based Processing:**

1. Divide image into patches (typically 32×32 or 64×64 pixels based on computational trade-offs).
2. Estimate motion independently per patch.
3. Reconstruct patches separately with local motion models.
4. Blend overlapping regions using weighted averaging (e.g., raised cosine window) to avoid boundary artifacts.

For 64×64 pixel patches on a 640×512 image with 50% overlap, this yields approximately 150 patches per frame.

---

## 9. Implementation Pipeline

### 9.1 Real-Time Architecture

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

*[Figure recommended: Detailed block diagram with data rates, buffer sizes, and processing modules.]*

### 9.2 Timing Budget (Target: 100ms per output frame)

| Stage | Time (ms) | Notes |
|-------|-----------|-------|
| Frame acquisition (20 frames) | 333 | Overlapped with processing. |
| IMU integration | 2 | Lightweight numerical integration. |
| Image-based refinement | 15 | Sparse feature matching. |
| SR reconstruction (30 iter) | 70 | GPU-accelerated. |
| Post-processing | 8 | Sharpening, histogram adjustment. |
| Output formatting | 5 | Bit depth conversion, encoding. |
| **Total (excluding acquisition)** | **100 ms** | Achieved through pipelining. |

### 9.3 Memory Requirements

| Buffer | Size | Notes |
|--------|------|-------|
| Input frame buffer (20 × 640×512 × 16-bit) | 13.1 MB | Circular buffer. |
| HR reconstruction (1280×1024 × 32-bit) | 5.2 MB | Floating point workspace. |
| Motion matrices (20 × 3×3 × 64-bit) | 2.9 KB | Negligible. |
| Algorithm workspace | ~20 MB | Intermediate buffers. |
| **Total** | **~40 MB** | Well within embedded GPU capacity. |

---

## 10. Performance Projections

### 10.1 Resolution Enhancement

With reliable 2× super-resolution (conservative estimate accounting for real-world degradations):

| Focal Length | Native GSD (cm) | Enhanced GSD (cm) | Pixels on 2m Target (Enhanced) |
|--------------|-----------------|-------------------|--------------------------------|
| 100 mm | 36.6 | 18.3 | 10.9 |
| 150 mm | 24.4 | 12.2 | 16.4 |
| 200 mm | 18.3 | 9.15 | 21.9 |
| 300 mm | 12.2 | 6.1 | 32.8 |

** Finding:** With 2× super-resolution, 150mm focal length achieves identification capability equivalent to native 300mm, enabling wider field of view for initial target acquisition.

*[Figure recommended: Bar chart comparing native vs. enhanced pixels-on-target across focal lengths.]*

### 10.2 Johnson Criteria Compliance (8,000 ft AGL, 2m Vehicle)

| Configuration | Native Cycles | Enhanced Cycles (2×) | Identification Capable? |
|---------------|---------------|----------------------|------------------------|
| 100mm native | 2.7 | 5.4 | Marginal (recognition only). |
| 150mm native | 4.1 | 8.2 | Yes. |
| 200mm native | 5.5 | 10.9 | Yes (robust). |
| 300mm native | 8.2 | 16.4 | Yes (significant margin). |

### 10.3 SNR Requirements

Super-resolution performance depends strongly on input SNR. Below are expected gains based on empirical studies:

| SNR (dB) | Expected Resolution Gain | Quality Assessment |
|----------|-------------------------|---------------------|
| < 15 | 1.2–1.4× | Poor—noise dominates. |
| 15–20 | 1.4–1.7× | Acceptable for detection. |
| 20–25 | 1.7–2.0× | Good for recognition. |
| > 25 | 2.0× | Excellent for identification. |

**Neutrino LC SNR Estimate** (scene ΔT = 2°C, NEdT = 30 mK):
$$\text{SNR} = \frac{\Delta T}{\text{NEdT}} = \frac{2000 \text{ mK}}{30 \text{ mK}} \approx 67 \approx 36 \text{ dB}$$

This excellent SNR provides substantial margin for robust super-resolution. Note that full NETD characterization includes integration time effects; the above is a first-order approximation.

### 10.4 Sensitivity Analysis

Performance degrades under non-ideal conditions:

| Condition | Impact | Mitigation |
|-----------|--------|------------|
| Strong turbulence ($r_0$ < 5 cm) | 30-50% resolution loss | Lucky imaging, shorter exposures. |
| Low scene contrast (ΔT < 0.5°C) | Reduced SNR, 1.5× gain limit | Longer integration, frame averaging. |
| Rapid platform motion (> 2°/s) | Motion blur, alignment errors | Faster shutter, gimbal stabilization. |
| Non-uniform sub-pixel shifts | Reduced diversity, <1.8× gain | Deliberate dither, longer burst. |

---

## 11. Validation Protocol

### 11.1 Ground Truth Requirements

1. **Resolution targets:** Place calibrated bar targets at known distances.
   - 4-bar MRTD targets sized for 8,000 ft equivalent angular extent.
   - Minimum Resolvable Temperature Difference (MRTD) characterization across spatial frequencies.

2. **Reference imagery:** Acquire simultaneous imagery from a calibrated reference system with known, higher resolution.

3. **Controlled motion:** Use precision gimbal to generate known sub-pixel shift sequences for algorithm validation.

### 11.2 Metrics

**MTF Measurement:**
$$\text{MTF}(f) = \frac{\text{Contrast at frequency } f}{\text{Contrast at DC}}$$

Measure using slanted-edge or Siemens star targets.

**Effective Resolution:**
- MTF50: Frequency at which MTF = 0.5 (commonly reported benchmark).
- MTF30: Frequency at which MTF = 0.3 (practical resolution limit).

**Super-Resolution Gain:**
$$G_{SR} = \frac{\text{MTF50}_{\text{enhanced}}}{\text{MTF50}_{\text{native}}}$$

### 11.3 Acceptance Criteria

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Resolution gain (MTF50 ratio) | ≥ 1.8× | Conservative 2× target with margin. |
| Artifact level | < 5% false edge rate | Prevents spurious detections. |
| Temporal consistency | < 2% frame-to-frame variation | Ensures stable video output. |
| Processing latency | < 150 ms | Maintains operational relevance. |

---

## 12. Hardware Integration Checklist

### 12.1 Camera Interface

- [ ] Camera Link or GigE interface configured and tested.
- [ ] 14-bit or 16-bit raw data capture enabled (avoid lossy compression).
- [ ] Hardware trigger output connected to IMU for synchronization.
- [ ] NUC (Non-Uniformity Correction) tables loaded and verified.
- [ ] Frame rate set to 60 Hz with confirmed stable timing.
- [ ] Gain and integration time optimized for expected scene radiance.

### 12.2 IMU Requirements

- [ ] Sample rate ≥ 800 Hz (1 kHz preferred).
- [ ] Gyro bias stability < 1°/hr for long-term accuracy.
- [ ] Accelerometer noise < 100 µg/√Hz.
- [ ] Hardware timestamp synchronization verified < 1 ms.
- [ ] Rigid mounting to camera body (shared mechanical reference).
- [ ] Calibration performed for misalignment angles.

### 12.3 Processing Hardware

- [ ] GPU compute capability ≥ 7.0 (NVIDIA Jetson Orin NX recommended).
- [ ] Memory bandwidth ≥ 100 GB/s for real-time throughput.
- [ ] Storage: NVMe SSD for raw data logging (≥ 500 MB/s write).
- [ ] Power budget: 25-40W for compute module.
- [ ] Thermal management verified for operational environment.

### 12.4 Software Stack

- [ ] CUDA/TensorRT for GPU acceleration.
- [ ] OpenCV for image processing primitives.
- [ ] Eigen for linear algebra operations.
- [ ] Custom SR kernel optimized for 640×512 → 1280×1024.
- [ ] Logging and telemetry for performance monitoring.
- [ ] Graceful degradation modes for edge cases.

---

## 13. Summary

### 13.1  Parameters

| Parameter | Value |
|-----------|-------|
| Operating Altitude | 8,000 ft AGL (2,438 m). |
| Target Focal Length | 150–300 mm. |
| Native GSD @ 300mm | 12.2 cm. |
| Enhanced GSD @ 300mm (2× SR) | 6.1 cm. |
| Frame Rate | 60 Hz input, 10 Hz output. |
| Processing Latency | < 100 ms. |
| Resolution Gain | 2× (target), 1.8× (minimum acceptable). |

### 13.2 Operational Envelope

**Identification Capable:**
- Focal length ≥ 150mm with 2× super-resolution.
- Focal length ≥ 300mm without super-resolution.
- Scene ΔT ≥ 1°C for adequate SNR.
- Platform angular rate < 2°/s for motion blur control.
- Atmospheric conditions: $r_0$ > 5 cm.

**Degraded Performance Expected:**
- Strong atmospheric turbulence ($r_0$ < 5 cm).
- Low scene contrast (ΔT < 0.5°C).
- Rapid platform motion (> 5°/s).
- Partial sensor obscuration or contamination.

**System Failure Modes:**
- Complete loss of IMU data: Fall back to image-only alignment (slower, less robust).
- Severe turbulence: Lucky imaging may reject >90% of frames, reducing output rate.
- Insufficient sub-pixel diversity: Algorithm converges to interpolated (not super-resolved) result.

### 13.3 Workflow Summary

1. **Acquire:** Capture 20-30 frames at 60 Hz (333-500 ms burst).
2. **Estimate Motion:** Integrate IMU data, refine with image-based alignment.
3. **Quality Select:** Rank frames by sharpness, weight or reject low-quality frames.
4. **Reconstruct:** MAP estimation with BTV regularization (20-50 iterations).
5. **Validate:** Check convergence, flag low-confidence regions.
6. **Output:** Enhanced frame at 10 Hz with metadata.

---

## Appendix A: Mathematical Notation Reference

| Symbol | Definition | Units |
|--------|------------|-------|
| $p$ | Pixel pitch. | µm |
| $f$ | Focal length. | mm |
| $R$ | Slant range. | m |
| $\lambda$ | Wavelength. | µm |
| $r_0$ | Fried parameter (atmospheric coherence length). | cm |
| $\theta_0$ | Isoplanatic angle (region of uniform distortion). | µrad |
| $\tau_0$ | Coherence time (turbulence temporal correlation). | ms |
| $C_n^2$ | Refractive index structure constant. | m⁻²/³ |
| IFOV | Instantaneous Field of View. | µrad |
| GSD | Ground Sample Distance. | cm |
| NEdT | Noise Equivalent Temperature Difference. | mK |
| MTF | Modulation Transfer Function. | dimensionless |
| SNR | Signal-to-Noise Ratio. | dB |

---

## Appendix B: Quick Reference Calculations

### B.1 IFOV Calculator

```
IFOV (µrad) = Pixel Pitch (µm) × 1000 / Focal Length (mm)

Example: 15 µm pixel, 300 mm focal length
IFOV = 15 × 1000 / 300 = 50 µrad
```

### B.2 GSD Calculator

```
GSD (m) = IFOV (rad) × Range (m)
GSD (m) = Pixel Pitch (m) × Range (m) / Focal Length (m)

Example: 15 µm pixel, 300 mm focal length, 2438 m range
GSD = (15×10⁻⁶) × 2438 / 0.3 = 0.122 m = 12.2 cm
```

### B.3 Pixels on Target

```
Pixels = Target Size (m) / GSD (m)

Example: 2 m vehicle, 12.2 cm GSD
Pixels = 2 / 0.122 = 16.4 pixels
```

### B.4 Johnson Criteria Check

```
Cycles on Target = Pixels on Target / 2.5

Identification requires ≥ 6.4 cycles.
Recognition requires ≥ 4.0 cycles.
Detection requires ≥ 1.0 cycle.

Example: 16.4 pixels → 16.4 / 2.5 = 6.6 cycles → Identification capable.
```

### B.5 Maximum Angular Rate for Motion Blur Control

```
ω_max (rad/s) = (Blur tolerance in pixels) × IFOV / Exposure time

Example: 0.5 pixel blur tolerance, 50 µrad IFOV, 1/60 s exposure
ω_max = 0.5 × 50×10⁻⁶ / (1/60) = 1.5 mrad/s = 0.086 °/s
```

---

## Appendix C: References

1. Johnson, J. (1958). "Analysis of Image Forming Systems." *Proceedings of the Image Intensifier Symposium*, U.S. Army Engineer Research and Development Laboratories.

2. Fried, D. L. (1966). "Optical Resolution Through a Randomly Inhomogeneous Medium for Very Long and Very Short Exposures." *Journal of the Optical Society of America*, 56(10), 1372-1379.

3. Park, S. C., Park, M. K., & Kang, M. G. (2003). "Super-Resolution Image Reconstruction: A Technical Overview." *IEEE Signal Processing Magazine*, 20(3), 21-36.

4. Farsiu, S., Robinson, M. D., Elad, M., & Milanfar, P. (2004). "Fast and Robust Multiframe Super Resolution." *IEEE Transactions on Image Processing*, 13(10), 1327-1344.

5. Holst, G. C. (2008). *Electro-Optical Imaging System Performance* (5th ed.). SPIE Press.

6. Vollmerhausen, R. H., & Driggers, R. G. (2000). *Analysis of Sampled Imaging Systems*. SPIE Press.

7. Roggemann, M. C., & Welsh, B. M. (1996). *Imaging Through Turbulence*. CRC Press.

8. Teledyne FLIR. (2022). "Neutrino IS Series Datasheet." Document 425-0065-00.

---

*Document Version: 1.1*  
*Date: December 2025*  
*Platform: Teledyne FLIR Neutrino LC – CZ 15-300 (425-0065-00)*  
*Application: High-Altitude MWIR Imaging with Computational Enhancement*
