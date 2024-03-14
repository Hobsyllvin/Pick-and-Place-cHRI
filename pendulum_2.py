import pygame
import math

# Constants
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
PI = math.pi
scale_factor = 0.01 # This factor is used in order to scale from pixels to meters
                    # But without using the actual conversion, since it was too fast
                    # This ratio can be adjusted to make the velocity of the pendulum faster or slower (the smaller, the faster)

class Pendulum:
    def __init__(self, length, angle, angular_velocity=0.0, bob_mass=1.0):
        self.length = length
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.bob_mass = bob_mass

    def update(self, dt):
        gravity = 9.81  # gravitational constant
        angular_acceleration = (-gravity / (self.length*scale_factor)) * math.sin(self.angle)
        self.angular_velocity += angular_acceleration * dt
        self.angle += self.angular_velocity * dt

    def tension_force_components(self):
        g = 9.81
        tension = (self.bob_mass * g) + (self.bob_mass * self.length * self.angular_velocity ** 2)
        tension_x = tension * math.sin(self.angle)
        tension_y = tension * math.cos(self.angle)
        return [tension_x, tension_y]

    def get_bob_mass_coordinates(self, screen, pivot):
         #Calculate the position of the pendulum's bob
         x = pivot[0] + self.length * math.sin(self.angle)
         y = pivot[1] + self.length * math.cos(self.angle)
         return [x, y]