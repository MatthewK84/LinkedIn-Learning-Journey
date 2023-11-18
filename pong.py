import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Set colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle class
class Paddle:
    WIDTH, HEIGHT = 20, 100
    
    def __init__(self, x, y):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)

    def draw(self, win):
        pygame.draw.rect(win, WHITE, self.rect)

    def move(self, y):
        self.y = y
        self.rect.y = y

# Initialize paddles
player = Paddle(50, HEIGHT // 2 - Paddle.HEIGHT // 2)
opponent = Paddle(WIDTH - 50 - Paddle.WIDTH, HEIGHT // 2 - Paddle.HEIGHT // 2)

# Ball class
class Ball:
    MAX_VEL = 5
    RADIUS = 15

    def __init__(self, x, y):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.rect = pygame.Rect(x - self.RADIUS, y - self.RADIUS, self.RADIUS*2, self.RADIUS*2)
        self.x_vel = self.MAX_VEL
        self.y_vel = random.choice([-self.MAX_VEL, self.MAX_VEL])

    def draw(self, win):
        pygame.draw.circle(win, WHITE, (self.x, self.y), self.RADIUS)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.rect.x = self.x
        self.rect.y = self.y

# Initialize ball
ball = Ball(WIDTH // 2, HEIGHT // 2)

def handle_paddle_movement(paddle):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and paddle.y - paddle.HEIGHT // 2 > 0:
        paddle.move(paddle.y - 4)
    if keys[pygame.K_DOWN] and paddle.y + paddle.HEIGHT // 2 < HEIGHT:
        paddle.move(paddle.y + 4)

# Call handle_paddle_movement function
handle_paddle_movement(player)
handle_paddle_movement(opponent)

def handle_ball_movement(ball, player, opponent):
    ball.move()

    # Ball collision with top and bottom
    if ball.y + ball.RADIUS >= HEIGHT or ball.y - ball.RADIUS <= 0:
        ball.y_vel *= -1

    # Ball collision with paddles
    if ball.rect.colliderect(player.rect) or ball.rect.colliderect(opponent.rect):
        ball.x_vel *= -1

    # Score updates and resetting ball
    if ball.x < 0:
        # Opponent scores
        ball.__init__(WIDTH // 2, HEIGHT // 2)
    elif ball.x > WIDTH:
        # Player scores
        ball.__init__(WIDTH // 2, HEIGHT // 2)

def draw(win, player, opponent, ball):
    win.fill(BLACK)
    player.draw(win)
    opponent.draw(win)
    ball.draw(win)
    pygame.display.update()

    # Score variables
player_score = 0
opponent_score = 0
font = pygame.font.SysFont("comicsans", 50)

def draw(win, paddles, ball, player_score, opponent_score):
    win.fill(BLACK)
    
    # Draw paddles, ball, and scores
    for paddle in paddles:
        paddle.draw(win)
    ball.draw(win)

    player_score_text = font.render(f"{player_score}", 1, WHITE)
    opponent_score_text = font.render(f"{opponent_score}", 1, WHITE)
    win.blit(player_score_text, (WIDTH//4 - player_score_text.get_width()//2, 20))
    win.blit(opponent_score_text, (WIDTH * (3/4) - opponent_score_text.get_width()//2, 20))

    pygame.display.update()

    def main():
        global player_score, opponent_score

        clock = pygame.time.Clock()

    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(60)  # 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, player)
        handle_ball_movement(ball, player, opponent)
        draw(win, [player, opponent], ball, player_score, opponent_score)

    pygame.quit()


def main():
    global player_score, opponent_score

    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(60)  # 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, player)
        handle_ball_movement(ball, player, opponent)
        draw(win, [player, opponent], ball, player_score, opponent_score)

if __name__ == "__main__":
    main()

# Path: pong.py