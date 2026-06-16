import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class Quaternion:
    def __init__(self, w=1.0, x=0.0, y=0.0, z=0.0):
        self.w, self.x, self.y, self.z = w, x, y, z

    def multiply(self, q):
        w = self.w*q.w - self.x*q.x - self.y*q.y - self.z*q.z
        x = self.w*q.x + self.x*q.w + self.y*q.z - self.z*q.y
        y = self.w*q.y - self.x*q.z + self.y*q.w + self.z*q.x
        z = self.w*q.z + self.x*q.y - self.y*q.x + self.z*q.w
        return Quaternion(w, x, y, z)

    def to_matrix(self):
        mag = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        w, x, y, z = self.w/mag, self.x/mag, self.y/mag, self.z/mag
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

def draw_rocket():
    """Draws a simple rocket shape with a distinct 'front' fin to track spin."""
    glBegin(GL_LINES)
    # Cylinder frame vertices
    v = [
        (0.3, -1, 0.3), (-0.3, -1, 0.3), (-0.3, -1, -0.3), (0.3, -1, -0.3), # Base
        (0.3, 1, 0.3),  (-0.3, 1, 0.3),  (-0.3, 1, -0.3),  (0.3, 1, -0.3),  # Top
        (0, 1.8, 0),    # Nose tip
        (0, -1, 0.8)    # Directional Fin pointing forward (+Z)
    ]
    edges = [
        (0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), # Rings
        (0,4), (1,5), (2,6), (3,7), (4,8), (5,8), (6,8), (7,8), # Body & Tip
        (0,9), (1,9) # Fin attached to base
    ]
    for edge in edges:
        for vertex in edge: glVertex3fv(v[vertex])
    glEnd()

def main():
    pygame.init()
    display = (1000, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -8)

    # State for Left Rocket (Euler Angles)
    euler_pitch = 0.0
    euler_yaw = 0.0
    euler_roll = 0.0

    # State for Right Rocket (Quaternion)
    quat_orientation = Quaternion()

    clock = pygame.time.Clock()
    print("DEMO INSTRUCTIONS:")
    print("1. Press 'SPACEBAR' to instantly pitch both rockets up to 90 degrees.")
    print("2. Try using the Arrow Keys to Turn (Yaw) and the A/D keys to Roll.")
    print("3. Watch how the Left rocket loses a dimension of control!")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Instantly set both straight up to trigger the flaw state
                    euler_pitch = 90.0
                    euler_yaw = 0.0
                    euler_roll = 0.0
                    quat_orientation = Quaternion.from_axis_angle((1, 0, 0), 90.0)

        keys = pygame.key.get_pressed()
        speed = 2.0

        # Capture inputs
        # Pitch: Up/Down
        if keys[K_UP]:
            euler_pitch += speed
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((1, 0, 0), speed))
        if keys[K_DOWN]:
            euler_pitch -= speed
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((1, 0, 0), -speed))
        
        # Yaw: Left/Right
        if keys[K_LEFT]:
            euler_yaw += speed
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((0, 1, 0), speed))
        if keys[K_RIGHT]:
            euler_yaw -= speed
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((0, 1, 0), -speed))
            
        # Roll: A/D
        if keys[K_a]:
            euler_roll += speed
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((0, 0, 1), speed))
        if keys[K_d]:
            euler_roll -= speed
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((0, 0, 1), -speed))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # ------------------------------------
        # DRAW LEFT ROCKET (EULER ANGLES)
        # ------------------------------------
        glPushMatrix()
        glTranslatef(-2.2, 0.0, 0.0) # Position on left side
        
        # Standard Euler sequencing matrix transformations: Rotate Y, then X, then Z
        glRotatef(euler_yaw, 0, 1, 0)
        glRotatef(euler_pitch, 1, 0, 0)
        glRotatef(euler_roll, 0, 0, 1)
        
        glColor3f(1.0, 0.3, 0.3) # Red for danger/flawed math
        draw_rocket()
        glPopMatrix()

        # ------------------------------------
        # DRAW RIGHT ROCKET (QUATERNION)
        # ------------------------------------
        glPushMatrix()
        glTranslatef(2.2, 0.0, 0.0) # Position on right side
        
        # Apply the smooth quaternion rotation matrix
        glMultMatrixf(quat_orientation.to_matrix())
        
        glColor3f(0.3, 1.0, 0.3) # Green for working quaternion math
        draw_rocket()
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()