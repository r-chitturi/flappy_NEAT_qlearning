import pygame
import os

class Pipe:
    pipes = []
    bottom_pipe_image = pygame.image.load(os.path.join("./assets/pipe", "pipe-bottom.png"))
    top_pipe_image = pygame.image.load(os.path.join("./assets/pipe", "pipe-top.png"))

    def __init__(self, x, bottom_y, top_y):
        self.bottom_pipe_rect = pygame.Rect(x, bottom_y, self.bottom_pipe_image.get_width(), self.bottom_pipe_image.get_height())
        self.top_pipe_rect = pygame.Rect(x, top_y - self.top_pipe_image.get_height(), self.top_pipe_image.get_width(), self.top_pipe_image.get_height())
        self.v = 180
        self.pipes.append(self)
        self.scored = False

    def update(self, dt):
        self.bottom_pipe_rect.x -= self.v * dt
        self.top_pipe_rect.x -= self.v * dt

    def draw(self, screen):
        screen.blit(self.bottom_pipe_image, (self.bottom_pipe_rect.x, self.bottom_pipe_rect.y))
        screen.blit(self.top_pipe_image, (self.top_pipe_rect.x, self.top_pipe_rect.y))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.top_pipe_image)
        bottom_pipe_mask = pygame.mask.from_surface(self.bottom_pipe_image)

        top_pipe_offset = (self.top_pipe_rect.left - bird.rect.left, self.top_pipe_rect.top - bird.rect.top)
        bottom_pipe_offset = (self.bottom_pipe_rect.left - bird.rect.left, self.bottom_pipe_rect.top - bird.rect.top)

        return bird_mask.overlap(top_pipe_mask, top_pipe_offset) or bird_mask.overlap(bottom_pipe_mask, bottom_pipe_offset)

    def right_x(self):
        return self.bottom_pipe_rect.right

    def top_pipe_y(self):
        return self.top_pipe_rect.bottom

    def bottom_pipe_y(self):
        return self.bottom_pipe_rect.top