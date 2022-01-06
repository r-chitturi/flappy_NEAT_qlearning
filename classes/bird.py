import pygame
import math
import os

class Bird:
    GRAVITY = 1800
    JUMP_VELOCITY = 600
    COLORS = ["blue", "green", "orange", "purple", "red", "yellow"]
    IMAGES = {color: pygame.image.load(os.path.join("./assets/bird", "bird-{}.png".format(color))) for color in COLORS}
    for color in IMAGES:
        IMAGES[color] = pygame.transform.scale(IMAGES[color], (IMAGES[color].get_width() * 3, IMAGES[color].get_height() * 3))
    MAX_ANGLE = 30
    MIN_ANGLE = -90
    ROT_V = 100
    birds = []
    
    def __init__(self, x, y, color):
        self.color = color
        self.image = self.IMAGES[color]
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        self.vy = 0
        self.angle = 0

    def update(self, dt):
        self.rect.y -= self.vy * dt
        self.vy -= self.GRAVITY * dt
        # Rotate
        self.angle -= self.ROT_V * dt
        if self.vy > 0 and self.angle < -90:
            self.angle = -90

    def jump(self):
        self.vy = self.JUMP_VELOCITY
        self.angle = self.MAX_ANGLE

    def rotate_image(self, image, angle):
        position = self.rect.center
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image.get_rect().center = position
        return rotated_image

    def draw(self, screen):
        rotated_image = self.rotate_image(self.image, self.angle)
        screen.blit(rotated_image, (self.rect.x, self.rect.y))

    def get_mask(self):
        rotated_image = self.rotate_image(self.image, self.angle)
        return pygame.mask.from_surface(rotated_image)