import pygame
import sys


# Modified Box class
class Gripper:
    def __init__(self, weight, width=10, x=0, y=0):  # Set a common speed
        self.weight = weight
        self.width = width  # Constant size
        self.color = (100, 190, 200)
        self.x = x
        self.y = y
        self.grabbed = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.width, self.width))

    def get_rect(self):
        return self.x, self.y, self.width, self.width
