# AutoMic Kinematics & System Design



## 1. System Overview

The **AutoMic** is a specialized robotic system designed to position a microphone in 3D space using four coordinated winches. It employs a **Cable-Driven Parallel Robot (CDPR)** architecture, where the end-effector (microphone) is suspended by cables tensioned by stepper motors.

The core "Kinematics Engine" translates a desired 3D spatial coordinate $(x, y, z)$ into precise digital step commands for each of the four motors.

---

## 2. Physical Geometry (The Frame)

The system operates within a defined 3D coordinate space. The geometry is **asymmetric** to accommodate the physical room constraints.

**Coordinate System:**
*   **Units:** Feet (Imperial)
*   **Origin $(0,0,0)$:** Front-Left corner of the floor.
*   **X-Axis:** Room Width (Left $\to$ Right)
*   **Y-Axis:** Room Depth (Front $\to$ Back)
*   **Z-Axis:** Height (Floor $\to$ Ceiling)

### Motor Coordinates

| Motor ID | Position | Coordinates $(x, y, z)$ | Description |
| :--- | :--- | :--- | :--- |
| **Motor 1** | Center High | `[6.43, 6.79, 7.93]` | Primary lift point, near the ceiling center. |
| **Motor 2** | Back Right | `[12.25, 12.17, 4.25]` | Mid-height anchor in the back corner. |
| **Motor 3** | Back Left | `[0.75, 12.17, 4.25]` | Mid-height anchor in the back corner. |
| **Motor 4** | Front Center | `[6.43, 0.00, 4.25]` | Mid-height anchor on the opposite wall. |

---

## 3. Drive Train Physics

To convert "Feet of Travel" into "Motor Steps," we derive the system's **Atomic Unit** based on the hardware specifications.

### Hardware Specifications
*   **Drum Diameter ($D$):** $104 \text{ mm}$ (Inner spool diameter)
*   **Motor Resolution ($R$):** $20,000$ steps/revolution (Microstepping enabled)

### The Derivation

1.  **Metric Circumference ($C_{mm}$):**
    $$C_{mm} = \pi \times D = \pi \times 104 \approx 326.726 \text{ mm}$$

2.  **Imperial Circumference ($C_{in}$):**
    $$C_{in} = \frac{C_{mm}}{25.4} \approx 12.8632 \text{ inches}$$

3.  **Step Constant ($\lambda$):**
    This constant represents the linear travel per single motor step.
    $$\lambda = \frac{C_{in}}{R} = \frac{12.8632}{20,000} \approx \mathbf{0.00064316} \text{ in/step}$$

---

## 4. Inverse Kinematics (The Algorithm)

The software does not track absolute cable spooling. Instead, it calculates the **Delta** ($\Delta$) required to transition from the `Current` position to the `Target` position.

### Step 1: 3D Euclidean Distance
For each motor $i$ located at $(M_x, M_y, M_z)$ and the target at $(T_x, T_y, T_z)$, we calculate the straight-line cable length required:

$$L_{new} = \sqrt{(T_x - M_x)^2 + (T_y - M_y)^2 + (T_z - M_z)^2}$$

### Step 2: Calculate Delta
We compare the **Current Cable Length** (tracked in software) against the **New Required Length**.

$$\Delta L = L_{current} - L_{new}$$

*   **Positive (+) $\Delta$:** $L_{current} > L_{new}$. The cable needs to get shorter. **Action: REEL IN.**
*   **Negative (-) $\Delta$:** $L_{current} < L_{new}$. The cable needs to get longer. **Action: RELEASE.**

### Step 3: Step Conversion
Convert the physical measurement (feet $\to$ inches) and then to steps:

$$Steps = \frac{\Delta L_{ft} \times 12}{\lambda} = \frac{\Delta L_{in}}{0.00064316}$$

---

## 5. The "Pacer" Algorithm (Speed Scaling)

To prevent the microphone from swinging or cables going slack, all motors must **start** and **finish** their movements at the exact same moment.

Since each motor travels a different distance, they cannot simply run at the same speed. We use a **Speed Scaling** algorithm.

### Logic
1.  **Calculate All Steps:** Determine absolute required steps for all 4 motors: $|S_1|, |S_2|, |S_3|, |S_4|$.
2.  **Make the Pacer:** Identify the motor moving the furthest distance.
    $$S_{max} = \max(|S_1|, |S_2|, |S_3|, |S_4|)$$
3.  **Set Pacer Speed:** The "Pacer" motor runs at the User's Target Speed ($V_{target}$).
4.  **Scale Others:** All other motors run at a fraction of that speed, proportional to their distance relative to the Pacer.

$$V_i = V_{target} \times \frac{|S_i|}{S_{max}}$$

### Example
*   **Target Speed:** 5.0 rps
*   **Motor 1 (Pacer):** Moves 10,000 steps. $\to$ Speed = **5.0 rps**
*   **Motor 2:** Moves 5,000 steps (50% of max). $\to$ Speed = **2.5 rps**

**Result:** Both motors finish their move in exactly 2,000 time units. The system moves in a straight 3D vector.

---

## 6. Simulation Tool

An HTML visualization tool ([kinematic.html](kinematic.html)) is provided to verify this math in real-time.

*   **Features:** Live 3D rendering of the asymmetric frame.
*   **Verification:** Displays real-time calculations for Target Length, Delta Inches, and Step Counts.
*   **Usage:** Enter $(x, y, z)$ coordinates to see the exact resulting motor commands before running hardware.