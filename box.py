import pygame


# Modified Box class
class Box:
    def __init__(self, weight, width=30, x=0):  # Set a common speed
        self.weight = weight
        self.width = width  # Constant size
        self.color = (30, 190, 30)
        self.x = x
        self.y = 300
        self.speed = 0.9
        self.picked = False

    def update(self):
        self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.width, self.width))

    def get_rect(self):
        return self.x, self.y, self.width, self.width
