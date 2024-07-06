import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random Obstacle Car Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Car properties
CAR_WIDTH = 50
CAR_HEIGHT = 80
CAR_SPEED = 5

# Obstacle and collectible properties
OBSTACLE_SIZE = 50
COLLECTIBLE_RADIUS = 20
OBJECT_SPEED = 10

# Create car class
class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([CAR_WIDTH, CAR_HEIGHT], pygame.SRCALPHA)
        self.draw_car()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2  # Start in the middle of the screen
        self.rect.bottom = HEIGHT - 20

    def draw_car(self):
        # Car body
        pygame.draw.rect(self.image, BLUE, [0, 10, CAR_WIDTH, CAR_HEIGHT - 20])
        # Car roof
        pygame.draw.rect(self.image, BLUE, [5, 0, CAR_WIDTH - 10, 15])
        # Wheels
        pygame.draw.circle(self.image, BLACK, (10, 15), 8)
        pygame.draw.circle(self.image, BLACK, (CAR_WIDTH - 10, 15), 8)
        pygame.draw.circle(self.image, BLACK, (10, CAR_HEIGHT - 15), 8)
        pygame.draw.circle(self.image, BLACK, (CAR_WIDTH - 10, CAR_HEIGHT - 15), 8)
        # Windshield
        pygame.draw.rect(self.image, YELLOW, [5, 15, CAR_WIDTH - 10, 10])

    def update(self, move_left, move_right):
        if move_left:
            self.rect.x -= CAR_SPEED
        if move_right:
            self.rect.x += CAR_SPEED
        
        # Prevent the car from moving out of bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

# Create obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([OBSTACLE_SIZE, OBSTACLE_SIZE])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - OBSTACLE_SIZE)
        self.rect.y = -OBSTACLE_SIZE

    def update(self):
        self.rect.y += OBJECT_SPEED
        if self.rect.top > HEIGHT:
            self.kill()

# Create collectible class
class Collectible(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([COLLECTIBLE_RADIUS * 2, COLLECTIBLE_RADIUS * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (COLLECTIBLE_RADIUS, COLLECTIBLE_RADIUS), COLLECTIBLE_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - COLLECTIBLE_RADIUS * 2)
        self.rect.y = -COLLECTIBLE_RADIUS * 2

    def update(self):
        self.rect.y += OBJECT_SPEED
        if self.rect.top > HEIGHT:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

# Create car
car = Car()
all_sprites.add(car)

# Set up the game loop
clock = pygame.time.Clock()
running = True
score = 0
spawn_timer = 0

# Game loop
move_left = False
move_right = False

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_left = True
            elif event.key == pygame.K_RIGHT:
                move_right = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                move_left = False
            elif event.key == pygame.K_RIGHT:
                move_right = False

    # Spawn objects
    spawn_timer += 1
    if spawn_timer >= 60:
        if random.random() < 0.7:
            new_object = Obstacle()
            obstacles.add(new_object)
        else:
            new_object = Collectible()
            collectibles.add(new_object)
        all_sprites.add(new_object)
        spawn_timer = 0

    # Update
    car.update(move_left, move_right)
    obstacles.update()
    collectibles.update()

    # Check for collisions
    if pygame.sprite.spritecollide(car, obstacles, True):
        running = False

    collected = pygame.sprite.spritecollide(car, collectibles, True)
    score += (len(collected)) * 10
    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Draw score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
