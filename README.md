## Flight Telemetry Lab: Euler Angles vs. Quaternions

This lab provides a visual proof of Gimbal Lock - a critical math failure that occurs in 3D physics, aerospace engineering, and video game engines when using standard angles (Pitch, Roll, Yaw).

Install packages :

	pip install pygame PyOpenGL
	
Run the v3 script:

	python quaternion.py

### Why Quaternions are better
After running the script, rocket simulation will appear in the pygame window.
Left rocket is rotating with Euler Angles and right rocket is rotating with Quaternions.
Press key A multiple times and analyze the rotation then press key D multiple times and analyze the rotation.
Now press SPACEBAR and again press key A multiple times and analyze the rotation then press key D multiple times and analyze the rotation.

The 3D rotation is one of the application of quaternions which can be achieved effortlessly by quaternions.
Quaternion solution was found by Hamilton in October 1843 when he was working on the problem of 3D algebra.
He had been working on the problem since many years, everyone was convinced that he is wasting his time on a solution which no one needs it, one day he was walking on the Broom bridge in Dublin and suddenly he got the solution in his mind. He carved the solution on the bridge by his pocket knife.

Today Quaternions are used widely in aviation, gaming, aeronautics and many other industries.
_________________________________________________________

This lab provides a visual proof of Gimbal Lock - a critical math failure that occurs in 3D physics, aerospace engineering, and video game engines when using standard angles (Pitch, Roll, Yaw).

### The Core Differences Between the Two Rockets

|Feature| Left Rocket (Red Nose Tip / Euler)|Right Rocket (Red Nose Tip / Quaternion)|
|-------|-----------------------------------|----------------------------------------|
|Math Framework|Uses 3 separate,independent angles (Y→X→Z).|Uses a single unified 4D complex number (w,x,y,z).|
|Coordinate Memory|Evaluates total rotation from a fixed,hardcoded global sequence.|Continuously accumulates changes relative to its current orientation.|
|Vulnerability|Suffers from Gimbal Lock. Losing a control axis at specific angles.|Immune. Retains full, independent control in all directions at all times.|
_________________________________________________________

### Flight Test Protocol: How to See the Difference

To witness the real-world mathematical failure - without it being a coding trick - follow these exact operational steps:

Phase A: The baseline test (Sanity Check)
1. Launch the script. Both rockets start facing forward, ascending smoothly.
2. Press Left or Right Arrow (Yaw). Notice how both turn left and right seamlessly.
3. Press A or D (Roll). Notice how both spin perfectly on their long cylinder axes like a drill bit. At this stage, they appear to function identically.

Phase B: Entering the Danger Zone
1. Press the SPACEBAR once. This commands both flight computers to pitch up exactly 90 degrees to point straight up at the sky.
2. Stop using the arrow keys. Leave them pointing straight up.

Phase C: The Breaking Point (Where to Concentrate)
1. Look closely at the asymmetric colored fins (Yellow, Cyan, Dark Grey) at the base of both rockets.
2. Hold down the A key or D key to command a Roll maneuver.
3. Observe the breakdown:
	The Right Rocket (Quaternion): It spins beautifully and smoothly on its center core axis. The colored fins rotate in a perfect circle around the hull.
	The Left Rocket (Euler): It fails to roll entirely. Instead of spinning around its body, it performs a horizontal Yaw swinging motion across your monitor screen.

_________________________________________________________

#### Why Does the Left Rocket Fail? (The Math Breakdown)

The problem with the left rocket is not a coding glitch; it is an absolute limitation of Euler Angles.

When calculating the left rocket's orientation, the engine multiplies three independent matrix transformations in a rigid sequence:

	Final Orientation  =  RotationYaw   ​×  RotationPitch​  ×  RotationRoll​

When the Pitch reaches exactly 90 degrees, the internal structure of the mathematical matrix collapses. Geometrically, the physical axis used to calculate Roll rotates so that it aligns perfectly on top of the axis used to calculate Yaw.

Because these two distinct mechanical axes are now occupying the exact same space, changing the roll variable inside the computer executes the exact same physical movement as changing the yaw variable. You have lost a dimension of control.
_________________________________________________________

#### How the Quaternion on the Right Fixed It

The right rocket completely avoids this failure because it doesn't use individual sequential steps (X, then Y, then Z).

A quaternion represents a 3D rotation by calculating a single, specific vector axis in space and an angle of rotation around that axis.

Instead of saving three separate tracking variables, the quaternion stores orientation as a unified, four-dimensional value (w,x,y,z) mapping onto a continuous hyper-sphere. When you press A or D while the right rocket points up, the math looks at its current 4D coordinate and multiplies it by a temporary change matrix:

			qnew   =  qcurrent  ×  qchange​

Because it updates its state dynamically based on its current placement rather than computing coordinates relative to a fixed global formula, it never encounters a boundary where axes merge. The right rocket always knows exactly which way its body is pointing, keeping its roll commands safely isolated from its yaw movements.

_________________________________________________________

> Pavitra Kanetkar

