import pygame
import random
import sys


pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.display.set_caption("Flappy Bird AI")

SCREEN_WIDTH, SCREEN_HEIGHT = 500, 800
FPS = 60


BIRD_FLAP_IMGS = [pygame.transform.scale2x(pygame.image.load('assets/Game Objects/yellowbird-downflap.png')),
                  pygame.transform.scale2x(pygame.image.load(
                      'assets/Game Objects/yellowbird-midflap.png')),
                  pygame.transform.scale2x(pygame.image.load('assets/Game Objects/yellowbird-upflap.png'))]
BACKGROUND_IMG = pygame.transform.scale2x(
    pygame.image.load('assets/Game Objects/background-day.png'))
BASE_IMG = pygame.transform.scale2x(
    pygame.image.load('assets/Game Objects/base.png'))
PIPE_IMG = pygame.transform.scale2x(
    pygame.image.load('assets/Game Objects/pipe-green.png'))
FONT = pygame.font.SysFont('Alatsi-Regular.ttf', 50)

GRAVITY = 0.4
JUMP_STRENGTH = -7
PIPE_SPEED = -5
GAME_SPEED = 5
PIPE_SPACING = 400


SOUNDS = {
    'die': pygame.mixer.Sound('assets/Sound Effects/die.wav'),
    'hit': pygame.mixer.Sound('assets/Sound Effects/hit.wav'),
    'point': pygame.mixer.Sound('assets/Sound Effects/point.wav'),
    'swoosh': pygame.mixer.Sound('assets/Sound Effects/swoosh.wav'),
    'wing': pygame.mixer.Sound('assets/Sound Effects/wing.wav')
}


class Bird:
    def __init__(self, x, y):
        self.images = BIRD_FLAP_IMGS
        self.animation_time = 5
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 0
        self.flapped = False

    def update(self):
        self.velocity += GRAVITY
        if self.flapped:
            self.flapped = False
            self.velocity = JUMP_STRENGTH

        self.rect.y += self.velocity
        self.animate()
        self.mask = pygame.mask.from_surface(self.image)

    def animate(self):
        self.current_image += 1
        if self.current_image >= len(self.images) * self.animation_time:
            self.current_image = 0
        self.image = self.images[self.current_image // self.animation_time]
        self.image = pygame.transform.rotate(self.image, -self.velocity * 3)
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        self.flapped = True
        SOUNDS['wing'].play()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    GAP = 200

    def __init__(self):
        self.x = SCREEN_WIDTH + 10
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randint(50, 300)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x += PIPE_SPEED

    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.top))
        screen.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.rect.left, self.top - bird.rect.top)
        bottom_offset = (self.x - bird.rect.left, self.bottom - bird.rect.top)

        top_point = bird_mask.overlap(top_mask, top_offset)
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if top_point or bottom_point:
            return True
        return False


class Base:
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= GAME_SPEED
        self.x2 -= GAME_SPEED
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMG, (self.x1, self.y))
        screen.blit(self.IMG, (self.x2, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)


def draw_window(screen, bird, pipes, base, score, high_score):
    screen.blit(BACKGROUND_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(screen)
    base.draw(screen)
    bird.draw(screen)
    display_score(score, high_score, screen)
    pygame.display.update()


def display_score(score, high_score, screen):
    score_surface = FONT.render(f"Score: {score}", True, (255, 255, 255))
    high_score_surface = FONT.render(
        f"High Score: {high_score}", True, (255, 255, 255))

    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
    high_score_rect = high_score_surface.get_rect(
        center=(SCREEN_WIDTH//2, 100))

    screen.blit(score_surface, score_rect)
    screen.blit(high_score_surface, high_score_rect)


def draw_game_over(screen):
    game_over_img = pygame.image.load('assets/UI/gameover.png')
    game_over_rect = game_over_img.get_rect(
        center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(game_over_img, game_over_rect)
    pygame.display.update()


def check_collision(pipes, bird, base):
    for pipe in pipes:
        if pipe.collide(bird):
            SOUNDS['hit'].play()
            return True

    if bird.rect.bottom >= base.y:
        base_mask = base.get_mask()
        bird_mask = bird.get_mask()
        offset = (0, base.y - bird.rect.top)
        collision_point = bird_mask.overlap(base_mask, offset)
        if collision_point:
            SOUNDS['hit'].play()
            return True

    if bird.rect.top <= 0:
        SOUNDS['hit'].play()
        return True

    return False


def draw_welcome_screen(screen):
    welcome_img = pygame.image.load('assets/UI/message.png')
    welcome_rect = welcome_img.get_rect(
        center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(welcome_img, welcome_rect)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False


def read_high_score():
    try:
        with open("high_score.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0


def update_high_score(new_score, high_score):
    if new_score > high_score:
        with open("high_score.txt", "w") as file:
            file.write(str(new_score))
        return new_score
    return high_score


def wait_for_restart(screen):
    draw_game_over(screen)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
    return False


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    high_score = read_high_score()
    draw_welcome_screen(screen)

    while True:
        bird = Bird(230, 350)
        base = Base(730)
        pipes = [Pipe()]
        score = 0
        running = True
        add_pipe = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.jump()

            bird.update()
            base.move()

            for pipe in pipes:
                pipe.move()
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    pipes.remove(pipe)
                if not pipe.passed and pipe.x < bird.rect.centerx:
                    pipe.passed = True
                    score += 1
                    SOUNDS['point'].play()
                    add_pipe = True

            if add_pipe and pipes[-1].x < SCREEN_WIDTH - PIPE_SPACING:
                pipes.append(Pipe())
                add_pipe = False

            if check_collision(pipes, bird, base):
                SOUNDS['die'].play()
                high_score = update_high_score(score, high_score)
                if not wait_for_restart(screen):
                    pygame.quit()
                    sys.exit()
                break

            draw_window(screen, bird, pipes, base, score, high_score)
            clock.tick(FPS)


__name__ == "__main__" and main()
