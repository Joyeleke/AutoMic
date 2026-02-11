AutoMic Kinematics & System Design

1. System Overview

The AutoMic is a Cable-Driven Parallel Robot (CDPR) designed to position a microphone within a 3D space using four coordinated winches. The system uses an Inverse Kinematics model based on 3D Euclidean geometry to translate target spatial coordinates $(x, y, z)$ into specific motor step commands.

2. Physical Geometry (The Frame)

The motor anchor points are defined in an Imperial (Feet) coordinate system.

Origin $(0,0,0)$: Front-Left floor corner.

X-Axis: Width (Left $\to$ Right).

Y-Axis: Depth (Front $\to$ Back).

Motor Coordinates $(x, y, z)$:

Motor 1 (Center High): [6.43, 6.79, 7.93]

Located at the geometric center of the frame.

Motor 2 (Back Right): [12.25, 12.17, 4.25]

Motor 3 (Back Left): [0.75, 12.17, 4.25]

Motor 4 (Front Center): [6.43, 0.00, 4.25]

3. Drive Train Physics

We derived the system's "Atomic Unit" (Inches per Microstep) from the physical hardware specifications.

A. Hardware Specs

Drum Diameter: $104 \text{ mm}$ (Inner spool diameter)

Motor Resolution: $20,000 \text{ steps/revolution}$

Cable Thickness: Neglected for initial model.

B. The Calculation

Metric Circumference:

$$C_{mm} = \pi \times 104 \text{ mm} \approx 326.726 \text{ mm}$$

Imperial Conversion:

$$C_{in} = \frac{326.726}{25.4} \approx 12.8632 \text{ inches}$$

Step Constant Derivation:
This constant defines linear cable travel per single motor step.

$$Step\_Size = \frac{12.8632 \text{ inches}}{20,000 \text{ steps}} \approx 0.00064316 \text{ in/step}$$

4. Kinematic Logic (The Algorithm)

The software does not store absolute cable lengths. Instead, it calculates the Delta (change in length) needed to move from Position A to Position B.

Step 1: 3D Euclidean Distance

For each motor $i$ at position $(Mx, My, Mz)$ and a Target at $(Tx, Ty, Tz)$, we calculate the total straight-line cable length required:

$$L_i = \sqrt{(Tx - Mx)^2 + (Ty - My)^2 + (Tz - Mz)^2}$$

Step 2: Calculate Delta

We compare the New Target Length against the Current calibrated Length.

$$\Delta L = L_{new} - L_{current}$$

Positive $\Delta$: The target is further away. Motor must unspool (Steps > 0).

Negative $\Delta$: The target is closer. Motor must spool in (Steps < 0).

Step 3: Step Conversion

We convert the physical delta into a digital command using the constant derived in Section 3.

$$Command_{steps} = \frac{\Delta L}{0.00064316}$$

5. Coordinated Motion (Speed Integration)

To ensure safely coordinated movement, the system uses a Speed Scaling algorithm. This ensures all motors start and stop simultaneously, maintaining tension and geometry.

The Algorithm:

Calculate All Deltas:
Determine the absolute steps needed for all 4 motors: $|S_1|, |S_2|, |S_3|, |S_4|$.

Find the "Pacer":
Identify the maximum number of steps any single motor has to move.

$$S_{max} = \max(|S_1|, |S_2|, |S_3|, |S_4|)$$

Set Pacer Speed:
Assign the user's requested speed ($V_{target}$) to the motor moving the furthest.

Scale Other Speeds:
Calculate the speed for every other motor $i$ proportionally:

$$V_i = V_{target} \times \frac{|S_i|}{S_{max}}$$

Example:

Motor 1 moves 10,000 steps (Pacer).

Motor 2 moves 5,000 steps.

Target Speed is 2,000 steps/sec.

Result: Motor 1 runs at 2,000 steps/sec. Motor 2 runs at 1,000 steps/sec. Both finish in exactly 5 seconds.

6. Simulation Tool

An HTML visualization tool ([kinematic.html](kinematic.html)) is provided to verify this math in real-time.

Features: Live 3D rendering of the asymmetric frame.

Verification: Displays real-time calculations for Target Length, Delta Inches, and Step Counts.

Usage: Enter $(x,y,z)$ coordinates to see the exact resulting motor commands before running hardware.