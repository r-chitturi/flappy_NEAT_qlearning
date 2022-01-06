import random
import cv2
import torch
import numpy as np

import pygame
from pygame.surfarray import array3d
pygame.init()

from classes.background import Background
from classes.bird import Bird
from classes.pipe import Pipe

def pre_processing(image, w=84, h=84):
    image = image[:300, :, :]
    image = cv2.cvtColor(cv2.resize(image, (w, h)), cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return image[None, :, :].astype(np.float32)
    # cv2.imwrite("ori.jpg", image)
    # cv2.imwrite("color.jpg", image)
    # cv2.imwrite("bw.jpg", image)

SCREEN_WIDTH, SCREEN_HEIGHT = 500, 768
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FONT = pygame.font.Font('freesansbold.ttf', 72)
pygame.display.set_caption("Q-Learning - Flappy Bird")
clock = pygame.time.Clock() 


def display_score(score):
    score_img = FONT.render("{}".format(score), True, (255, 255, 255))
    SCREEN.blit(score_img, (SCREEN_WIDTH // 2, 60))

class Flappy:
    def __init__(self):
        self.bg = Background(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bird = Bird(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, "yellow")
        self.pipes = []
        self.score = 0    
        self.gameover = False
        self.FPS = 100000
        self.dt = 1 / 30
        
    def next_frame(self, action):
        pygame.event.pump()
        reward = 0.1
        terminal = False
        if action == 1:
            self.bird.jump()
        # else:
        #     reward += 0.001

        if len(self.pipes) == 0 or self.pipes[-1].right_x() < SCREEN_WIDTH - 300:
            bottom_y = random.randint(300, SCREEN_HEIGHT - 200)
            top_y = random.randint(100, bottom_y - 200)
            pipe = Pipe(SCREEN_WIDTH, bottom_y, top_y)
            self.pipes.append(pipe)

        # Update and draw the background.
        self.bg.update(self.dt)

        # Update and draw the birds.
        self.bird.update(self.dt)
        # Collisions
        for pipe in self.pipes:
            if pipe.collide(self.bird):
                reward = -1
                self.gameover = True
        if self.bird.rect.bottom < 0 or self.bird.rect.top > SCREEN_HEIGHT:
            reward = -1
            self.gameover = True
        terminal = True

        # Update and draw the pipes.
        for pipe in self.pipes:
            pipe.update(self.dt)

            if pipe.right_x() < SCREEN_WIDTH // 2 and not pipe.scored:
                self.score = 1
                pipe.scored = True
                reward = 1

            if pipe.right_x() < 0:
                self.pipes.remove(pipe)

        image = array3d(pygame.display.get_surface())
        SCREEN.fill((255, 255, 255))
        # self.bg.draw(SCREEN)
        self.bird.draw(SCREEN)
        # display_score(self.score)
        for pipe in self.pipes:
            pipe.draw(SCREEN)
        pygame.display.update()
        clock.tick(self.FPS)

        if self.gameover:
            self.__init__()

        return torch.from_numpy(pre_processing(image)), reward, terminal

if __name__ == "__main__":
    game = Flappy()
    while True:
        state, reward, done = game.next_frame(random.randint(0, 1))