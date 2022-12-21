import pygame
import random
import sys

from pygame.sprite import Sprite, Group

from config import config

class Bird(Sprite):
    def __init__(self, config):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(config.BIRD_IMAGE).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = config.SCREEN_WIDTH//2
        self.rect[1] = config.SCREEN_HEIGHT//2

        self.init_speed = config.BIRD_SPEED
        self.speed = config.BIRD_SPEED
        self.acc = config.BIRD_ACCELERATION
    
    def update(self):
        self.rect[1] += self.speed
        self.speed += self.acc

    def jump(self):
        self.speed = -self.init_speed

class Floor(Sprite):
    def __init__(self, config, floor_start):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(config.FLOOR_IMAGE).convert_alpha()
        self.image = pygame.transform.scale(self.image, (config.FLOOR_WIDTH, config.FLOOR_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = config.FLOOR_SPEED
        self.scree_width = config.SCREEN_WIDTH
        self.floor_start = floor_start
        self.rect = self.image.get_rect()
        self.rect[0] = floor_start
        self.rect[1] = config.SCREEN_HEIGHT - config.FLOOR_HEIGHT
    
    def update(self):
        self.rect[0] -= self.speed
        if self.rect[0] <= self.floor_start - self.scree_width:
            self.rect[0] = self.floor_start

class Pipe(Sprite):
    def __init__(self, config, pipe_start, pip_size, upsidedown):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(config.PIPE_IMAGE).convert_alpha()
        self.image = pygame.transform.scale(self.image, (config.PIPE_WIDTH, config.PIPE_HEIGHT))
        self.speed = config.PIPE_SPEED
        self.rect = self.image.get_rect()
        self.rect[0] = pipe_start
        self.rect[3] = pip_size
        
        if upsidedown:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = 0
            self.image = pygame.transform.scale(self.image, (config.PIPE_WIDTH, pip_size))
        else:
            self.rect[1] = config.SCREEN_HEIGHT - pip_size
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self):
        self.rect[0] -= self.speed

def generate_pipe_pairs(config, pipe_start):
    size = random.randint(config.PIPE_HEIGHT_MIN, config.PIPE_HEIGHT_MAX)
    pipe = Pipe(config, pipe_start, size, False)
    pipe2 = Pipe(config, pipe_start, config.SCREEN_HEIGHT - config.PIPE_GAP - size, True)
    return [pipe, pipe2]

def is_pipe_out(pipe):
    return pipe.rect[0] + pipe.rect[3] < 0

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    screen_image = pygame.image.load(config.SCREEN_IMAGE)
    screen_image = pygame.transform.scale(screen_image, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    game_over_font = pygame.font.SysFont(pygame.font.get_default_font(), 60)
    score_font = pygame.font.SysFont(pygame.font.get_default_font(), 60)

    clock = pygame.time.Clock()

    bird = Bird(config)
    bird_group = Group([bird])

    floor = Floor(config, 0)
    floor_gorup = Group([floor])

    pipe_group = Group([generate_pipe_pairs(config, config.SCREEN_WIDTH), generate_pipe_pairs(config, 2*config.SCREEN_WIDTH)])
    
    is_playing = True
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if not is_playing:
                        bird = Bird(config)
                        bird_group = Group([bird])
                        pipe_group = Group([generate_pipe_pairs(config, config.SCREEN_WIDTH), generate_pipe_pairs(config, 2*config.SCREEN_WIDTH)])
                        is_playing = True
                        score = 0
                    bird.jump()

        # drawing
        screen.blit(screen_image, (0, 0))
        bird_group.draw(screen)
        pipe_group.draw(screen)
        floor_gorup.draw(screen)

        if is_playing:
            if is_pipe_out(pipe_group.sprites()[0]):
                pipe_group.remove(pipe_group.sprites()[0])
                pipe_group.remove(pipe_group.sprites()[0])
                pipes = generate_pipe_pairs(config, config.SCREEN_WIDTH + config.PIPE_WIDTH)
                pipe_group.add(pipes)
                score += 1
            
            # updating
            bird_group.update()
            floor_gorup.update()
            pipe_group.update()
            score_txt = score_font.render(str(score), True, (255,255,255))
            screen.blit(score_txt, (config.SCREEN_WIDTH - score_txt.get_width() - 20, 0 + score_txt.get_width()//2))

            if pygame.sprite.groupcollide(bird_group, floor_gorup, False, False, pygame.sprite.collide_mask) or pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask):
                is_playing = False
        else:
            game_over_txt = game_over_font.render("GAME OVER", True, (255,0,0))
            score_txt = score_font.render(str(score), True, (255,255,255))
            screen.blit(game_over_txt, (config.SCREEN_WIDTH//2 -  game_over_txt.get_width()//2, config.SCREEN_HEIGHT//2 - game_over_txt.get_height()//2))
            screen.blit(score_txt, (config.SCREEN_WIDTH//2 -  score_txt.get_width()//2, config.SCREEN_HEIGHT//2 - score_txt.get_height()//2 + 60))
        clock.tick(config.GAME_FPS)
        pygame.display.update()
