import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Set colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Game settings
FPS = 60
PADDLE_SPEED = 7
BALL_SPEED = 5
AI_SPEED = 5
WINNING_SCORE = 5

class Paddle:
    def __init__(self, x, y):
        self.width = 20
        self.height = 100
        self.x = x
        self.y = y
        self.speed = PADDLE_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, win):
        pygame.draw.rect(win, WHITE, self.rect)

    def move_up(self):
        if self.y > 0:
            self.y -= self.speed
            self.rect.y = self.y

    def move_down(self):
        if self.y + self.height < HEIGHT:
            self.y += self.speed
            self.rect.y = self.y

    def reset_position(self):
        self.y = HEIGHT // 2 - self.height // 2
        self.rect.y = self.y

class Ball:
    def __init__(self, x, y):
        self.radius = 15
        self.x = x
        self.y = y
        self.speed_x = BALL_SPEED
        self.speed_y = random.choice([-BALL_SPEED//2, BALL_SPEED//2])
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)

    def draw(self, win):
        pygame.draw.circle(win, WHITE, (int(self.x), int(self.y)), self.radius)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Update rect position
        self.rect.center = (int(self.x), int(self.y))

    def bounce_y(self):
        self.speed_y *= -1

    def bounce_x(self):
        self.speed_x *= -1
        # Slightly increase speed after each hit (max speed limit)
        if abs(self.speed_x) < 8:
            if self.speed_x > 0:
                self.speed_x += 0.5
            else:
                self.speed_x -= 0.5

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_x = BALL_SPEED if random.choice([True, False]) else -BALL_SPEED
        self.speed_y = random.choice([-BALL_SPEED//2, BALL_SPEED//2])
        self.rect.center = (int(self.x), int(self.y))

    def check_wall_collision(self):
        # Top and bottom walls
        if self.y - self.radius <= 0 or self.y + self.radius >= HEIGHT:
            self.bounce_y()

    def check_paddle_collision(self, paddle):
        if self.rect.colliderect(paddle.rect):
            # Calculate where ball hit the paddle (for angle variation)
            hit_pos = (self.y - paddle.y) / paddle.height
            self.speed_y = (hit_pos - 0.5) * 8  # Adjust angle based on hit position
            self.bounce_x()
            
            # Move ball slightly away from paddle to prevent sticking
            if self.speed_x > 0:
                self.x = paddle.rect.left - self.radius - 1
            else:
                self.x = paddle.rect.right + self.radius + 1

class Game:
    def __init__(self):
        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        self.player = Paddle(50, HEIGHT // 2 - 50)
        self.ai = Paddle(WIDTH - 70, HEIGHT // 2 - 50)
        self.ball = Ball(WIDTH // 2, HEIGHT // 2)
        
        self.game_over = False
        self.winner = ""

    def handle_player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move_down()

    def update_ai(self):
        # Simple AI that follows the ball
        paddle_center = self.ai.y + self.ai.height // 2
        
        if paddle_center < self.ball.y - 30:
            if self.ai.y + self.ai.height < HEIGHT:
                self.ai.y += AI_SPEED
                self.ai.rect.y = self.ai.y
        elif paddle_center > self.ball.y + 30:
            if self.ai.y > 0:
                self.ai.y -= AI_SPEED
                self.ai.rect.y = self.ai.y

    def update_ball(self):
        if not self.game_over:
            self.ball.move()
            self.ball.check_wall_collision()
            self.ball.check_paddle_collision(self.player)
            self.ball.check_paddle_collision(self.ai)

            # Check for scoring
            if self.ball.x < 0:
                self.ai_score += 1
                self.ball.reset()
                if self.ai_score >= WINNING_SCORE:
                    self.game_over = True
                    self.winner = "AI Wins!"
                    
            elif self.ball.x > WIDTH:
                self.player_score += 1
                self.ball.reset()
                if self.player_score >= WINNING_SCORE:
                    self.game_over = True
                    self.winner = "Player Wins!"

    def draw_dashed_line(self):
        # Draw center line
        for i in range(0, HEIGHT, 20):
            if i % 40 == 0:
                pygame.draw.rect(win, WHITE, (WIDTH//2 - 2, i, 4, 15))

    def draw_scores(self):
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        
        win.blit(player_text, (WIDTH//4 - player_text.get_width()//2, 50))
        win.blit(ai_text, (3*WIDTH//4 - ai_text.get_width()//2, 50))

    def draw_instructions(self):
        if not self.game_over:
            inst_text = self.small_font.render("Use ↑↓ or W/S keys to move", True, WHITE)
            win.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, HEIGHT - 40))

    def draw_game_over(self):
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            win.blit(overlay, (0, 0))
            
            # Winner text
            winner_text = self.font.render(self.winner, True, GREEN)
            win.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 50))
            
            # Restart instruction
            restart_text = self.small_font.render("Press SPACE to play again or ESC to quit", True, WHITE)
            win.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = ""
        self.player.reset_position()
        self.ai.reset_position()
        self.ball.reset()

    def draw(self):
        win.fill(BLACK)
        
        # Draw game elements
        self.draw_dashed_line()
        self.player.draw(win)
        self.ai.draw(win)
        self.ball.draw(win)
        self.draw_scores()
        self.draw_instructions()
        self.draw_game_over()
        
        pygame.display.flip()

    def run(self):
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()
            
            # Update game state
            if not self.game_over:
                self.handle_player_input()
                self.update_ai()
                self.update_ball()
            
            # Draw everything
            self.draw()
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
