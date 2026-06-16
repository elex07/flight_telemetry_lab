import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class Quaternion:
    def __init__(self, w=1.0, x=0.0, y=0.0, z=0.0):
        self.w, self.x, self.y, self.z = w, x, y, z

    def normalize(self):
        mag = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if mag == 0: return
        self.w /= mag
        self.x /= mag
        self.y /= mag
        self.z /= mag

    def multiply(self, q):
        w = self.w*q.w - self.x*q.x - self.y*q.y - self.z*q.z
        x = self.w*q.x + self.x*q.w + self.y*q.z - self.z*q.y
        y = self.w*q.y - self.x*q.z + self.y*q.w + self.z*q.x
        z = self.w*q.z + self.x*q.y - self.y*q.x + self.z*q.w
        return Quaternion(w, x, y, z)

    def to_matrix(self):
        self.normalize()
        x, y, z, w = self.x, self.y, self.z, self.w
        return [
            1 - 2*y**2 - 2*z**2,     2*x*y - 2*z*w,     2*x*z + 2*y*w, 0.0,
                  2*x*y + 2*z*w, 1 - 2*x**2 - 2*z**2,     2*y*z - 2*x*w, 0.0,
                  2*x*z - 2*y*w,     2*y*z + 2*x*w, 1 - 2*x**2 - 2*y**2, 0.0,
                            0.0,               0.0,               0.0, 1.0
        ]

    @staticmethod
    def from_axis_angle(axis, angle_deg):
        angle_rad = math.radians(angle_deg)
        sin_half = math.sin(angle_rad / 2.0)
        ax, ay, az = axis
        mag = math.sqrt(ax**2 + ay**2 + az**2)
        if mag > 0: ax, ay, az = ax/mag, ay/mag, az/mag
        return Quaternion(math.cos(angle_rad / 2.0), ax * sin_half, ay * sin_half, az * sin_half)


def draw_shaded_cylinder(radius, height, sides=16):
    glBegin(GL_QUAD_STRIP)
    for i in range(sides + 1):
        angle = 2.0 * math.pi * i / sides
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glNormal3f(math.cos(angle), 0.0, math.sin(angle))
        glVertex3f(x, -height/2, z)
        glVertex3f(x, height/2, z)
    glEnd()

def draw_shaded_cone(radius, height, sides=16):
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, height, 0.0)
    for i in range(sides + 1):
        angle = 2.0 * math.pi * i / sides
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glNormal3f(math.cos(angle), 0.5, math.sin(angle))
        glVertex3f(x, 0.0, z)
    glEnd()

def draw_solid_rocket():
    # Hull
    glColor3f(0.85, 0.85, 0.85)
    draw_shaded_cylinder(0.3, 2.0)
    # Nose Cone
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glColor3f(0.9, 0.1, 0.1)
    draw_shaded_cone(0.3, 0.6)
    glPopMatrix()
    # Asymmetric Fins (Makes tracking spatial orientation easy)
    glBegin(GL_TRIANGLES)
    # Right Fin (Bright Yellow)
    glColor3f(1.0, 0.8, 0.0)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(0.3, -1.0, 0.0)
    glVertex3f(0.8, -1.0, 0.0)
    glVertex3f(0.3, -0.4, 0.0)
    # Left Fin (Dark Grey)
    glColor3f(0.2, 0.2, 0.2)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-0.3, -1.0, 0.0)
    glVertex3f(-0.8, -1.0, 0.0)
    glVertex3f(-0.3, -0.4, 0.0)
    # Front Navigation Fin (Bright Cyan)
    glColor3f(0.0, 0.8, 1.0)
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, -1.0, 0.3)
    glVertex3f(0.0, -1.0, 0.8)
    glVertex3f(0.0, -0.4, 0.3)
    glEnd()

def init_gl(w, h):
    glClearColor(0.05, 0.07, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Powerful specular light to clearly highlight body rotation
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 10.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def main():
    pygame.init()
    w, h = 1200, 700
    pygame.display.set_mode((w, h), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Real-World Flight Test: Euler Gimbal Lock vs Quaternion Control")
    init_gl(w, h)

    # System 1: Euler Parameters
    euler_pitch, euler_yaw, euler_roll = 0.0, 0.0, 0.0

    # System 2: Quaternion Parameters
    quat_state = Quaternion()

    altitude = -3.5
    clock = pygame.time.Clock()

    print("\n=== FLIGHT TEST INSTRUCTIONS ===")
    print("STEP 1: Test basic controls (Arrow keys + A/D). Both rockets turn smoothly.")
    print("STEP 2: Press SPACEBAR to enter 'Launch State' (Pitches both rockets up exactly 90°).")
    print("STEP 3: Now try to ROLL using the A and D keys.")
    print("=================================\n")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Execute a perfect 90 degree pitch up into the lock zone
                    euler_pitch = 90.0
                    euler_yaw, euler_roll = 0.0, 0.0
                    quat_state = Quaternion.from_axis_angle((1, 0, 0), 90.0)

        # Ascent sequence loop
        altitude += 0.012
        if altitude > 4.0: altitude = -4.0

        keys = pygame.key.get_pressed()
        rate = 2.0  # Angular speed degrees per frame

        # --- PROCESS CONTROLS VIA LOCAL FLIGHT ENGINES ---
        if keys[K_UP]:    # Pitch Up
            euler_pitch += rate
            quat_state = quat_state.multiply(Quaternion.from_axis_angle((1, 0, 0), rate))
        if keys[K_DOWN]:  # Pitch Down
            euler_pitch -= rate
            quat_state = quat_state.multiply(Quaternion.from_axis_angle((1, 0, 0), -rate))
            
        if keys[K_LEFT]:  # Yaw Left
            euler_yaw += rate
            # In local space, yawing means spinning around the object's current vertical Y axis
            quat_state = quat_state.multiply(Quaternion.from_axis_angle((0, 1, 0), rate))
        if keys[K_RIGHT]: # Yaw Right
            euler_yaw -= rate
            quat_state = quat_state.multiply(Quaternion.from_axis_angle((0, 1, 0), -rate))
            
        if keys[K_a]:     # Roll Counter-Clockwise
            euler_roll += rate
            # In local space, rolling means spinning down the barrel of the cylinder (Z axis)
            quat_state = quat_state.multiply(Quaternion.from_axis_angle((0, 0, 1), rate))
        if keys[K_d]:     # Roll Clockwise
            euler_roll -= rate
            quat_state = quat_state.multiply(Quaternion.from_axis_angle((0, 0, 1), -rate))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -8.5)

        # ----------------------------------------------------
        # SYSTEM A: EULER SHUTTLE (LEFT)
        # ----------------------------------------------------
        glPushMatrix()
        glTranslatef(-2.2, altitude, 0.0)
        
        # Real-world tracking bug: The fixed sequence order kills a degree of freedom
        glRotatef(euler_yaw, 0, 1, 0)
        glRotatef(euler_pitch, 1, 0, 0)
        glRotatef(euler_roll, 0, 0, 1)
        
        draw_solid_rocket()
        glPopMatrix()

        # ----------------------------------------------------
        # SYSTEM B: QUATERNION SHUTTLE (RIGHT)
        # ----------------------------------------------------
        glPushMatrix()
        glTranslatef(2.2, altitude, 0.0)
        
        # Smooth continuous mapping matrix transformation
        glMultMatrixf(quat_state.to_matrix())
        
        draw_solid_rocket()
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()