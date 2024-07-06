import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 400
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set display mode here


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)

# Car properties
CAR_WIDTH = 130
CAR_HEIGHT = 130
CAR_SPEED = 20

# Obstacle and collectible properties
OBSTACLE_SIZE = 70
COLLECTIBLE_SIZE = 50
OBJECT_SPEED = 15

# Load images
def load_image(name, size=None):
    path = os.path.join("assets", name)
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# Load game assets
road_img = load_image("eroad_lane5.png", (WIDTH, HEIGHT + 100))
car_img = load_image("car.png", (CAR_WIDTH, CAR_HEIGHT))
stone_img = load_image("stone2.png", (OBSTACLE_SIZE, OBSTACLE_SIZE))
coin_img = load_image("coin.png", (COLLECTIBLE_SIZE, COLLECTIBLE_SIZE))

road_img_vertical = pygame.transform.rotate(road_img, 5)


class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = car_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20

    def update(self, move_left, move_right):
        if move_left:
            self.rect.x -= CAR_SPEED
        if move_right:
            self.rect.x += CAR_SPEED
        
        # Prevent the car from moving out of bounds
        if self.rect.left < 50:
            self.rect.left = 50
        if self.rect.right > WIDTH - 50:
            self.rect.right = WIDTH - 50

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = stone_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WIDTH - 50 - OBSTACLE_SIZE)
        self.rect.y = -OBSTACLE_SIZE

    def update(self):
        self.rect.y += OBJECT_SPEED
        if self.rect.top > HEIGHT:
            self.kill()

class Collectible(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WIDTH - 50 - COLLECTIBLE_SIZE)
        self.rect.y = -COLLECTIBLE_SIZE

    def update(self):
        self.rect.y += OBJECT_SPEED
        if self.rect.top > HEIGHT:
            self.kill()

class CarGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Realistic Car Game")

        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.spawn_timer = 0
        self.road_y = 0

        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()

        self.car = Car()
        self.all_sprites.add(self.car)

    def get_game_state(self):
        closest_obstacle = min(self.obstacles, key=lambda o: o.rect.y, default=None)
        closest_collectible = min(self.collectibles, key=lambda c: c.rect.y, default=None)

        obstacle_distance = math.dist(self.car.rect.center, closest_obstacle.rect.center) if closest_obstacle else HEIGHT
        collectible_distance = math.dist(self.car.rect.center, closest_collectible.rect.center) if closest_collectible else HEIGHT

        num_obstacles = len(self.obstacles)
        num_collectibles = len(self.collectibles)

        obstacle_relative_x = (closest_obstacle.rect.centerx - self.car.rect.centerx) / WIDTH if closest_obstacle else 0
        obstacle_relative_y = (closest_obstacle.rect.centery - self.car.rect.centery) / HEIGHT if closest_obstacle else 0
        collectible_relative_x = (closest_collectible.rect.centerx - self.car.rect.centerx) / WIDTH if closest_collectible else 0
        collectible_relative_y = (closest_collectible.rect.centery - self.car.rect.centery) / HEIGHT if closest_collectible else 0

        state = [
            self.car.rect.centerx / WIDTH,
            self.car.rect.centery / HEIGHT,
            obstacle_distance / HEIGHT,
            collectible_distance / HEIGHT,
            num_obstacles,
            num_collectibles,
            obstacle_relative_x,
            obstacle_relative_y,
            collectible_relative_x,
            collectible_relative_y
        ]
        
        return state

    def reset(self):
        self.running = True
        self.spawn_timer = 0
        self.score = 0
        self.all_sprites.empty()
        self.obstacles.empty()
        self.collectibles.empty()
        self.car = Car()
        self.all_sprites.add(self.car)

    def take_action(self, action):
        # 0: Do nothing, 1: Move left, 2: Move right
        move_left = action == 1
        move_right = action == 2
        self.car.update(move_left, move_right)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def game_step(self, action):
        previous_car_pos = self.car.rect.center
        self.take_action(action)
        current_car_pos = self.car.rect.center

        # Handle events
        self.handle_events()

        # Spawn objects
        self.spawn_timer += 1
        if self.spawn_timer >= 40:
            if random.random() < 0.7:
                new_object = Obstacle()
                self.obstacles.add(new_object)
            else:
                new_object = Collectible()
                self.collectibles.add(new_object)
            self.all_sprites.add(new_object)
            self.spawn_timer = 0

        # Update objects
        self.obstacles.update()
        self.collectibles.update()

        # Initialize reward
        reward = 0

        # Check for collisions and calculate rewards
        for obstacle in self.obstacles:
            prev_dist = math.dist(previous_car_pos, obstacle.rect.center)
            curr_dist = math.dist(current_car_pos, obstacle.rect.center)
            if curr_dist > prev_dist:
                reward += 1  # Small reward for moving away from obstacles
            
            if self.car.rect.colliderect(obstacle.rect):
                reward -= 10  # High negative reward for hitting an obstacle
                self.running = False
                obstacle.kill()

        collected = []

        for collectible in self.collectibles:
            prev_dist = math.dist(previous_car_pos, collectible.rect.center)
            curr_dist = math.dist(current_car_pos, collectible.rect.center)
            if curr_dist < prev_dist:
                reward += 1  # Small positive reward for moving towards collectibles
            
            if self.car.rect.colliderect(collectible.rect):
                reward += 10  # High positive reward for collecting
                collected.append(collectible)
                collectible.kill()

        self.score += len(collected)

        # Penalize for being close to screen edges
        if self.car.rect.left < 70 or self.car.rect.right > WIDTH - 70:
            reward -= 2

        # Draw everything
        self.screen.fill(BLACK)
        
        # Draw scrolling road
        self.road_y = (self.road_y + OBJECT_SPEED) % HEIGHT
        self.screen.blit(road_img, (0, self.road_y - HEIGHT))
        self.screen.blit(road_img, (0, self.road_y))

        self.all_sprites.draw(self.screen)

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        self.clock.tick(60)

        return self.get_game_state(), reward, self.score, not self.running

# Main game loop
def main():
    game = CarGame()
    while game.running:
        action = random.randint(0, 2)  # Replace with your AI agent's action selection
        state, reward, score, done = game.game_step(action)
        if done:
            game.reset()

if __name__ == "__main__":
    main()