import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 120
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Keybinds
keybinds = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "heal": pygame.K_h,
    "attack": pygame.K_e
}

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPG Game")
clock = pygame.time.Clock()

# Load Textures
player_texture = pygame.image.load("Player16x16.png")
sword_texture = pygame.image.load("sword.png")
sword2_texture = pygame.image.load("sword_ii_0.png")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_texture, (40, 40))
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.health = 100
        self.speed = 300  # pixels per second
        self.inventory = []
        self.equipped = None
        self.attack_cooldown = 0
        self.score = 0

    def update(self, keys, dt):
        move = pygame.math.Vector2(0, 0)
        if keys[keybinds["up"]]: move.y -= self.speed * dt
        if keys[keybinds["down"]]: move.y += self.speed * dt
        if keys[keybinds["left"]]: move.x -= self.speed * dt
        if keys[keybinds["right"]]: move.x += self.speed * dt

        self.pos += move
        self.pos.x = max(0, min(WIDTH, self.pos.x))
        self.pos.y = max(0, min(HEIGHT, self.pos.y))
        self.rect.center = self.pos

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self):
        self.attack_cooldown = 20

    def draw_health_bar(self, surface):
        pygame.draw.rect(surface, RED, (10, 10, 200, 20))
        pygame.draw.rect(surface, GREEN, (10, 10, 200 * (self.health / 100), 20))

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 50 + level * 10  # pixels per second
        self.health = 30 + level * 10

    def update(self, player, dt):
        direction = player.pos - self.pos
        if direction.length_squared() != 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt
            self.rect.center = self.pos

    def draw_health_bar(self, surface):
        bar_width = 30
        bar_height = 5
        fill = (self.health / 100) * bar_width
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, max(0, fill), bar_height))

# Item class
class Item(pygame.sprite.Sprite):
    def __init__(self, name, texture):
        super().__init__()
        self.image = pygame.transform.scale(texture, (30, 30))
        self.rect = self.image.get_rect(center=(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)))
        self.name = name

# Game setup
player = Player()
all_sprites = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
items = pygame.sprite.Group()

level = 1
font = pygame.font.SysFont(None, 36)

sword_spawned = False
def spawn_enemies(level):
    for _ in range(level + 2):
        enemy = Enemy(level)
        all_sprites.add(enemy)
        enemies.add(enemy)

def spawn_items():
    global sword_spawned
    if not sword_spawned:
        sword = Item("Sword", sword_texture)
        items.add(sword)
        all_sprites.add(sword)
        sword_spawned = True

def draw_fps():
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
    screen.blit(fps_text, (WIDTH - 120, 10))

def game_over_screen(score):
    screen.fill(BLACK)
    text1 = font.render("YOU DIED - Press R to Restart", True, RED)
    text2 = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(text1, (WIDTH//2 - 200, HEIGHT//2 - 20))
    screen.blit(text2, (WIDTH//2 - 100, HEIGHT//2 + 20))
    pygame.display.flip()

# Main loop
running = True
game_over = False
spawn_enemies(level)
spawn_items()

while running:
    dt = clock.tick(FPS) / 1000  # Delta time in seconds
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player = Player()
                all_sprites = pygame.sprite.Group(player)
                enemies = pygame.sprite.Group()
                items = pygame.sprite.Group()
                level = 1
                game_over = False
                sword_spawned = False
                spawn_enemies(level)
                spawn_items()
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == keybinds["attack"]:
                    if player.attack_cooldown == 0 and player.equipped == "Sword":
                        player.attack()
                        for enemy in enemies:
                            if player.rect.colliderect(enemy.rect):
                                enemy.health -= 25
                                player.health = min(100, player.health + 5)
                                player.score += 10
                if event.key == keybinds["heal"]:
                    player.health = min(100, player.health + 20)

    if not game_over:
        player.update(keys, dt)
        for enemy in enemies:
            enemy.update(player, dt)

        for enemy in list(enemies):
            if enemy.health <= 0:
                enemy.kill()

        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                player.health -= 10 * dt  # scaled by time

        for item in items:
            if player.rect.colliderect(item.rect):
                player.inventory.append(item.name)
                if not player.equipped:
                    player.equipped = item.name
                item.kill()

        if not enemies:
            level += 1
            spawn_enemies(level)
            spawn_items()

        if player.health <= 0:
            game_over = True
            continue

        screen.fill(BLACK)
        all_sprites.draw(screen)

        for enemy in enemies:
            enemy.draw_health_bar(screen)

        player.draw_health_bar(screen)

        inventory_text = font.render(f"Inventory: {player.inventory}", True, WHITE)
        equip_text = font.render(f"Equipped: {player.equipped}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(inventory_text, (10, 40))
        screen.blit(equip_text, (10, 70))
        screen.blit(level_text, (10, 100))
        screen.blit(score_text, (10, 130))

        draw_fps()
        pygame.display.flip()
    else:
        game_over_screen(player.score)

pygame.quit()
