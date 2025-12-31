# Robotics & UAS Engineering Master Study Guide

This guide covers the full stack of robotics engineering, from the physics of hardware to high-level path planning.

---

## 1. Mechanics: Kinematics & Dynamics
*The physics of how robots move.*

### 1.1 Kinematics (Geometry of Motion)
Kinematics describes motion without considering the forces that cause it.

* **Rigid Body Transformations:**
    * Rotation Matrices ($SO(3)$) and Homogeneous Transformation Matrices ($SE(3)$).
    * Quaternions (crucial for UAS to avoid gimbal lock).
* **Forward Kinematics (FK):**
    * Computing the end-effector position from joint angles.
    * **Tools:** Denavit-Hartenberg (DH) Parameters, Product of Exponentials (PoE).
* **Inverse Kinematics (IK):**
    * Computing joint angles required to reach a specific position.
    * **Analytical Solutions:** Closed-form geometry (fast, specific to robot).
    * **Numerical Solutions:** Jacobian pseudo-inverse, Newton-Raphson methods.
* **Differential Kinematics:**
    * **The Jacobian Matrix ($J$):** Mapping joint velocities to end-effector velocities: $\dot{x} = J(q)\dot{q}$.
    * Singularities (configurations where mobility is lost).

### 1.2 Dynamics (Forces & Torques)
Dynamics relates forces/torques to motion. Essential for high-speed control and UAS stability.

* **Newton-Euler Formulation:**
    * Recursive calculation of forces/torques link-by-link. Good for simulation efficiency.
* **Lagrangian Formulation:**
    * Energy-based approach: $L = T - V$ (Kinetic - Potential Energy).
    * The Standard Dynamics Equation:
        $$M(q)\ddot{q} + C(q, \dot{q})\dot{q} + G(q) = \tau$$
        * $M(q)$: Mass/Inertia Matrix.
        * $C(q, \dot{q})$: Coriolis and Centrifugal terms.
        * $G(q)$: Gravity vector.
        * $\tau$: Joint torques.
* **UAS Specifics:**
    * Aerodynamic drag, thrust coefficients, rotor inertia.

---

## 2. Control Theory
*The brain that keeps the system stable.*

### 2.1 Classical Control

* **PID (Proportional-Integral-Derivative):**
    * **P:** Errors based on current position.
    * **I:** Accumulates past errors (removes steady-state error).
    * **D:** Predicts future errors based on rate of change (adds damping).
    * **Tuning:** Ziegler-Nichols method, manual tuning.

### 2.2 Modern & Optimal Control

* **State Space Representation:**
    * $\dot{x} = Ax + Bu$
    * $y = Cx + Du$
* **LQR (Linear Quadratic Regulator):**
    * Optimizes a cost function minimizing error and energy expenditure.
    * Solving the Riccati Equation.
* **MPC (Model Predictive Control):**
    * Optimization over a finite time horizon while handling **constraints** (e.g., "don't hit the wall," "max motor voltage").
    * Computationally heavy but powerful for dynamic maneuvers.

---

## 3. Estimation & Sensor Fusion
*Determining where you are when sensors are noisy.*

### 3.1 Probability Foundations

* Bayes Rule.
* Gaussian Distributions.

### 3.2 Filters

* **Kalman Filter (KF):** Optimal estimation for linear systems with Gaussian noise.
* **Extended Kalman Filter (EKF):** Linearizes non-linear systems (standard for years in GPS/IMU fusion).
* **Unscented Kalman Filter (UKF):** Uses sigma points; better for highly non-linear dynamics.
* **Particle Filters:** Monte Carlo localization (good for global localization, computationally expensive).

### 3.3 Sensor Fusion Examples

* **IMU + GPS:** Fusing high-frequency relative data (IMU) with low-frequency absolute data (GPS).
* **Visual-Inertial Odometry (VIO):** Fusing camera feed with accelerometer/gyro data.

---

## 4. Perception
*Interpreting the world through sensors.*

### 4.1 Sensors

* **Lidar:** Time-of-flight laser ranging (2D vs. 3D).
* **Stereo Cameras:** Calculating depth from disparity (similar to human eyes).
* **RGB-D:** Projected light patterns (e.g., RealSense, Kinect).

### 4.2 Data Processing

* **Point Clouds:** Voxel grids, Octrees.
* **PCL (Point Cloud Library):** Filtering, segmentation, surface reconstruction.
* **Computer Vision (OpenCV):**
    * Feature extraction (SIFT, ORB, FAST).
    * Optical Flow (tracking motion between frames).
    * Deep Learning for Object Detection (YOLO, SSD).

---

## 5. SLAM (Simultaneous Localization & Mapping)
*Building a map while figuring out where you are within it.*

* **Frontend (Visual Odometry):** Feature matching between frames to estimate motion.
* **Backend (Optimization):**
    * **Loop Closure:** Recognizing a previously visited location to correct drift.
    * **Pose Graph Optimization:** Minimizing error across the entire trajectory graph (e.g., g2o, GTSAM).
* **Major Algorithms:**
    * *Visual:* ORB-SLAM3, PTAM.
    * *Lidar:* GMapping (2D), Cartographer (2D/3D), LIO-SAM.

---

## 6. Motion Planning
*Deciding how to get from A to B.*

### 6.1 Search-Based Planning (Discrete)

* **Dijkstra's Algorithm:** Guaranteed shortest path, visits all nodes.
* **A\* (A-Star):** Uses heuristics to guide the search (faster than Dijkstra).

### 6.2 Sampling-Based Planning (Continuous)

* **RRT (Rapidly-exploring Random Trees):** Good for high-dimensional spaces (like robotic arms).
* **RRT\*:** An optimizing variant that rewires the tree to find shorter paths over time.

### 6.3 Trajectory Optimization

* **Minimum Snap Trajectories:** Generating smooth paths for quadrotors to minimize mechanical stress.
* **Dynamic Window Approach (DWA):** Local obstacle avoidance.

---

## 7. Grasping & Manipulation
*Interacting with physical objects.*

* **Contact Mechanics:**
    * Friction cones (Coulomb friction).
    * Soft vs. Hard finger contacts.
* **Grasp Analysis:**
    * **Force Closure:** Can the gripper resist external forces/torques?
    * **Form Closure:** Is the object strictly geometrically constrained?
* **Manipulation Planning:** Pick-and-place logic, approach vectors.

---

## 8. Real-Time Systems & Software
*The infrastructure that runs the code.*

### 8.1 ROS 2 (Robot Operating System)

* **Middleware:** DDS (Data Distribution Service) for communication.
* **Core Concepts:** Nodes, Topics (Pub/Sub), Services (Req/Res), Actions.
* **Tools:** RViz (Visualization), Gazebo (Simulation), TF2 (Coordinate transforms).

### 8.2 Embedded & RTOS

* **RTOS (Real-Time Operating System):** FreeRTOS, ChibiOS.
    * Priority-based preemptive scheduling.
    * Hard Real-Time vs. Soft Real-Time requirements.
* **Communication Protocols:** UART, I2C, SPI, CAN Bus (critical for automotive/robotics).

---

## 9. Hardware Fundamentals
*The physical components.*

### 9.1 Actuators

* **BLDC (Brushless DC Motors):** High efficiency, high RPM (Drones).
* **Stepper Motors:** High precision, open-loop control (3D printers, Arms).
* **Servo Motors:** Integrated gearbox and pot for position control.

### 9.2 Drivers & Power

* **H-Bridge:** Circuit to switch polarity (forward/reverse).
* **ESC (Electronic Speed Controller):** Generates 3-phase AC for BLDC motors.
* **Power Distribution:** Voltage regulation (Buck/Boost converters), LiPo battery safety.

---

## 10. Recommended Learning Path & Resources

### Phase 1: The Basics (Months 1-2)

* **Focus:** Python/C++, Linear Algebra, Basic Arduino hardware.
* **Resource:** *Probabilistic Robotics* (Thrun) - Chapters 1-3.

### Phase 2: Simulation & Control (Months 3-4)

* **Focus:** ROS 2, Gazebo, PID, Kinematics.
* **Resource:** *Modern Robotics* (Lynch & Park) - Video lectures available on YouTube.

### Phase 3: Advanced Autonomy (Months 5-6)

* **Focus:** SLAM, Perception, MPC.
* **Resource:** "Cyrill Stachniss" YouTube Channel (SLAM/Photogrammetry).
