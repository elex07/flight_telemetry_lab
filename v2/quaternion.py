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


def draw_shaded_cylinder(radius, height, sides=16):
    """Generates a solid cylinder with explicit surface normals for shading."""
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
    """Generates a solid cone for the rocket nose tip."""
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
    """Renders rocket assemblies with solid faces."""
    # 1. Main Stage Hull (Silver Gray)
    glColor3f(0.75, 0.78, 0.8)
    draw_shaded_cylinder(0.35, 2.0)
    
    # 2. Command Nose Module (Crimson Nose Tip)
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glColor3f(0.85, 0.15, 0.15)
    draw_shaded_cone(0.35, 0.7)
    glPopMatrix()
    
    # 3. Dynamic Fins (Deep Charcoal)
    glColor3f(0.15, 0.15, 0.18)
    glBegin(GL_TRIANGLES)
    # Port Wing Fin
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-0.35, -1.0, 0.0)
    glVertex3f(-0.85, -1.0, 0.0)
    glVertex3f(-0.35, -0.3, 0.0)
    
    # Starboard Wing Fin
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(0.35, -1.0, 0.0)
    glVertex3f(0.85, -1.0, 0.0)
    glVertex3f(0.35, -0.3, 0.0)
    
    # Central Stabilizer Vent (Tracks Orientation Roll Axis)
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, -1.0, 0.35)
    glVertex3f(0.0, -1.0, 0.85)
    glVertex3f(0.0, -0.3, 0.35)
    glEnd()


def init_gl_context(width, height):
    """Sets up the explicit viewport state to guarantee rendering context."""
    glClearColor(0.08, 0.12, 0.18, 1.0) # Dark gray-blue sky background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Light Vector Allocation
    glLightfv(GL_LIGHT0, GL_POSITION, [4.0, 5.0, 6.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.25, 0.25, 0.25, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.75, 0.75, 0.75, 1.0])

    # Explicit Matrix Modes Pipeline
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    pygame.init()
    width, height = 1100, 650
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Telemetry Matrix Evaluation")
    
    init_gl_context(width, height)

    # Initial Structural Values
    euler_pitch, euler_yaw, euler_roll = 0.0, 0.0, 0.0
    quat_orientation = Quaternion()

    # Launch Parameters
    altitude = -3.5
    rate_of_climb = 0.015
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Point both rockets straight up to trigger the lock zone
                    euler_pitch = 90.0
                    euler_yaw, euler_roll = 0.0, 0.0
                    quat_orientation = Quaternion.from_axis_angle((1, 0, 0), 90.0)

        # Loop altitude to keep rockets inside frame limits
        altitude += rate_of_climb
        if altitude > 4.5:
            altitude = -4.5

        # Flight Input Vector Control Tracking
        keys = pygame.key.get_pressed()
        step = 2.0

        if keys[K_UP]:
            euler_pitch += step
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((1, 0, 0), step))
        if keys[K_DOWN]:
            euler_pitch -= step
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((1, 0, 0), -step))
        if keys[K_LEFT]:
            euler_yaw += step
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((0, 1, 0), step))
        if keys[K_RIGHT]:
            euler_yaw -= step
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((0, 1, 0), -step))
        if keys[K_a]:
            euler_roll += step
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((0, 0, 1), step))
        if keys[K_d]:
            euler_roll -= step
            quat_orientation = quat_orientation.multiply(Quaternion.from_axis_angle((0, 0, 1), -step))

        # Core Frame Refresh
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Position Camera viewport out along negative Z line
        glTranslatef(0.0, 0.0, -9.0)

        # ----------------------------------------------------
        # SYSTEM EULER (LEFT)
        # ----------------------------------------------------
        glPushMatrix()
        glTranslatef(-2.2, altitude, 0.0)
        
        glRotatef(euler_yaw, 0, 1, 0)
        glRotatef(euler_pitch, 1, 0, 0)
        glRotatef(euler_roll, 0, 0, 1)
        
        draw_solid_rocket()
        glPopMatrix()

        # ----------------------------------------------------
        # SYSTEM QUATERNION (RIGHT)
        # ----------------------------------------------------
        glPushMatrix()
        glTranslatef(2.2, altitude, 0.0)
        
        glMultMatrixf(quat_orientation.to_matrix())
        
        draw_solid_rocket()
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()