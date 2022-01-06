import pygame, random
from classes.background import Background
from classes.bird import Bird
from classes.pipe import Pipe
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 500, 768
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FONT = pygame.font.Font('freesansbold.ttf', 72)
pygame.display.set_caption("NEAT - Flappy Bird")

flap_sound = pygame.mixer.Sound("./assets/bird/wing.mp3")
point_sound = pygame.mixer.Sound("./assets/point.mp3")

def display_score(score):
    score_img = FONT.render("{}".format(score), True, (255, 255, 255))
    SCREEN.blit(score_img, (SCREEN_WIDTH // 2, 60))

def main():
    run = True
    clock = pygame.time.Clock() 

    # Initialize a background.
    bg = Background(SCREEN_WIDTH, SCREEN_HEIGHT)

    Bird.birds = [Bird(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, "yellow")]

    score = 0

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        if len(Bird.birds) == 0:
            pygame.quit()

        dt = 1 / 60
        SCREEN.fill((255, 255, 255))

        if len(Pipe.pipes) == 0 or Pipe.pipes[-1].right_x() < SCREEN_WIDTH - 300:
            bottom_y = random.randint(300, SCREEN_HEIGHT - 200)
            top_y = random.randint(100, bottom_y - 200)
            pipe = Pipe(SCREEN_WIDTH, bottom_y, top_y)

        # Update and draw the background.
        bg.update(dt)
        bg.draw(SCREEN)

        # Update and draw the birds.
        for bird in Bird.birds:
            bird.update(dt)
            # Collisions
            for pipe in Pipe.pipes:
                if pipe.collide(bird):
                    Bird.birds.remove(bird)
                if bird.rect.bottom < 0 or bird.rect.top > SCREEN_HEIGHT:
                    Bird.birds.remove(bird)

            bird.draw(SCREEN)

        # Update and draw the pipes.
        for pipe in Pipe.pipes:
            pipe.update(dt)
            pipe.draw(SCREEN)

            if pipe.right_x() < SCREEN_WIDTH // 2 and not pipe.scored:
                score += 1
                pipe.scored = True
                point_sound.play()

        display_score(score)
        pygame.display.update()
        clock.tick(60)

        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in Bird.birds:
                        bird.jump()
                        flap_sound.play()

if __name__ == "__main__":
    main()