import pygame
import random
import numpy as np

# Define colors
COLORS = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]

class Figure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.figures = [
            [[1, 5, 9, 13], [4, 5, 6, 7]],
            [[4, 5, 9, 10], [2, 6, 5, 9]],
            [[6, 7, 9, 10], [1, 5, 6, 10]],
            [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
            [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
            [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
            [[1, 2, 5, 6]],
        ]
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(COLORS) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

class Tetris:
    level = 2
    score = 0
    state = "start"

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = np.zeros((height, width), dtype=int)
        self.figure = None

    def new_figure(self):
        self.figure = Figure(3, 0)

    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                       j + self.figure.x > self.width - 1 or \
                       j + self.figure.x < 0 or \
                       self.field[i + self.figure.y][j + self.figure.x] > 0:
                        return True
        return False

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

    def draw_board(self, screen):
        screen.fill((255, 255, 255))
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, (128, 128, 128), [100 + 20 * j, 60 + 20 * i, 20, 20], 1)
                if self.field[i][j]:
                    pygame.draw.rect(screen, COLORS[self.field[i][j]],
                                     [101 + 20 * j, 61 + 20 * i, 18, 19])

        if self.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.figure.image():
                        pygame.draw.rect(screen, COLORS[self.figure.color],
                                         [101 + 20 * (j + self.figure.x),
                                          61 + 20 * (i + self.figure.y),
                                          18, 19])

        font = pygame.font.SysFont('Calibri', 25, True, False)
        text = font.render("Score: " + str(self.score), True, (0, 0, 0))
        screen.blit(text, [0, 0])
        if self.state == "gameover":
            font1 = pygame.font.SysFont('Calibri', 65, True, False)
            text_game_over = font1.render("Game Over", True, (255, 125, 0))
            text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))
            screen.blit(text_game_over, [20, 200])
            screen.blit(text_game_over1, [25, 265])

        pygame.display.flip()

def main():
    pygame.init()
    size = (400, 500)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Tetris")

    done = False
    clock = pygame.time.Clock()
    game = Tetris(20, 10)
    counter = 0
    pressing_down = False

    while not done:
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (25 // game.level // 2) == 0 or pressing_down:
            if game.state == "start":
                game.go_down()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                if event.key == pygame.K_LEFT:
                    game.go_side(-1)
                if event.key == pygame.K_RIGHT:
                    game.go_side(1)
                if event.key == pygame.K_SPACE:
                    game.freeze()
                if event.key == pygame.K_ESCAPE:
                    game = Tetris(20, 10)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        game.draw_board(screen)
        clock.tick(25)

    pygame.quit()

if __name__ == "__main__":
    main()