import pygame
import random
import math
import sys

# Ekran ayarları
FRAME_WIDTH = 600
FRAME_HEIGHT = 800
PLAYER_SPEED = 5
PLAYER_BULLET_SPEED = 8
ENEMY_BULLET_SPEED = 2
ENEMY_SPEED = 2
NUM_ENEMIES = 5
PLAYER_LIVES = 3

pygame.init()
screen = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))
pygame.display.set_caption("Touhou Style Bullet Hell - Boss and Power-Up")

clock = pygame.time.Clock()

# Müzik
def start_music():
    pygame.mixer.music.load("music.mp3")
    pygame.mixer.music.play(-1)

start_music()

# Resimler
background = pygame.image.load("image.png").convert()
background = pygame.transform.scale(background, (FRAME_WIDTH, FRAME_HEIGHT))

player_img = pygame.image.load("player1.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (40, 40))

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

bullet_img = pygame.image.load("bullet.png").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (20, 20))  # BÜYÜK mermiler

# Font
font = pygame.font.SysFont(None, 36)

# Oyuncu
player = pygame.Rect(FRAME_WIDTH // 2, FRAME_HEIGHT - 80, 40, 40)
player_lives = PLAYER_LIVES
score = 0

# Mermiler
player_bullets = []
enemy_bullets = []

# Düşmanlar
enemies = []
boss = None
boss_spawned = False

# Sayaçlar
kill_count = 0
power_up_ready = False
power_up_active = False

# Power-up bar ayarları
POWER_UP_THRESHOLD = 50
power_up_bar_width = 200

class Enemy:
    def __init__(self, x=None, y=None, is_boss=False):
        if x is None:
            self.x = random.randint(40, FRAME_WIDTH - 40)
        else:
            self.x = x
        if y is None:
            self.y = -40
        else:
            self.y = y
        self.is_boss = is_boss
        self.health = 5 if not is_boss else 50
        self.img = enemy_img
        self.rect = self.img.get_rect(center=(self.x, self.y))
        self.timer = 0

    def update(self):
        if self.is_boss:
            self.timer += 0.05
            self.x += math.cos(self.timer) * 2  # Boss hafif sağ-sol hareket yapar
        self.y += ENEMY_SPEED if not self.is_boss else ENEMY_SPEED / 2
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.img, self.rect)

def spawn_enemy():
    if len(enemies) < NUM_ENEMIES and not boss_spawned:
        enemies.append(Enemy())

def fire_enemy_bullets(enemy):
    for angle in range(0, 360, 90 if not enemy.is_boss else 30):  # Boss daha yoğun atar
        rad = math.radians(angle)
        dx = math.cos(rad) * ENEMY_BULLET_SPEED
        dy = math.sin(rad) * ENEMY_BULLET_SPEED
        bullet = {"rect": bullet_img.get_rect(center=enemy.rect.center), "dx": dx, "dy": dy}
        enemy_bullets.append(bullet)

def reset_game():
    global player, player_lives, score, player_bullets, enemy_bullets, enemies, boss, kill_count, boss_spawned, power_up_ready, power_up_active
    player = pygame.Rect(FRAME_WIDTH // 2, FRAME_HEIGHT - 80, 40, 40)
    player_lives = PLAYER_LIVES
    score = 0
    player_bullets = []
    enemy_bullets = []
    enemies = []
    boss = None
    kill_count = 0
    boss_spawned = False
    power_up_ready = False
    power_up_active = False
    start_music()

# Ana döngü
running = True
enemy_spawn_timer = 0
enemy_fire_timer = 0

while running:
    clock.tick(60)
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Oyuncu Kontrolleri
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] and player.right < FRAME_WIDTH:
        player.x += PLAYER_SPEED
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN] and player.bottom < FRAME_HEIGHT:
        player.y += PLAYER_SPEED
    if keys[pygame.K_SPACE]:
        if len(player_bullets) < 10 or power_up_active:  # Power-up aktifse sınır yok
            if not power_up_active:
                bullet = {"rect": pygame.Rect(player.centerx - 2, player.top, 4, 10)}
                player_bullets.append(bullet)
            else:  # Spread Shot
                bullet1 = {"rect": pygame.Rect(player.centerx - 10, player.top, 4, 10)}
                bullet2 = {"rect": pygame.Rect(player.centerx, player.top, 4, 10)}
                bullet3 = {"rect": pygame.Rect(player.centerx + 10, player.top, 4, 10)}
                player_bullets.extend([bullet1, bullet2, bullet3])

    # Power-up barı
    pygame.draw.rect(screen, (100, 100, 100), (FRAME_WIDTH//2 - power_up_bar_width//2, 10, power_up_bar_width, 20))
    current_width = min(kill_count / POWER_UP_THRESHOLD, 1.0) * power_up_bar_width
    pygame.draw.rect(screen, (0, 255, 0), (FRAME_WIDTH//2 - power_up_bar_width//2, 10, current_width, 20))
    if kill_count >= POWER_UP_THRESHOLD:
        power_up_ready = True

    # Oyuncu Mermileri
    for bullet in player_bullets[:]:
        bullet["rect"].y -= PLAYER_BULLET_SPEED
        if bullet["rect"].bottom < 0:
            player_bullets.remove(bullet)

    # Düşman Spawn
    if not boss_spawned:
        spawn_enemy()

    for enemy in enemies[:]:
        enemy.update()
        enemy.draw(screen)
        if enemy.rect.top > FRAME_HEIGHT:
            enemies.remove(enemy)

    if boss:
        boss.update()
        boss.draw(screen)
        if boss.rect.top > FRAME_HEIGHT:
            reset_game()

    # Düşman Mermileri
    enemy_fire_timer += 1
    if enemy_fire_timer > 90:
        for enemy in enemies:
            fire_enemy_bullets(enemy)
        if boss:
            fire_enemy_bullets(boss)
        enemy_fire_timer = 0

    for bullet in enemy_bullets[:]:
        bullet["rect"].x += bullet["dx"]
        bullet["rect"].y += bullet["dy"]
        screen.blit(bullet_img, bullet["rect"])
        if bullet["rect"].top > FRAME_HEIGHT or bullet["rect"].bottom < 0 or bullet["rect"].left > FRAME_WIDTH or bullet["rect"].right < 0:
            enemy_bullets.remove(bullet)

    # Çarpışmalar
    for bullet in player_bullets[:]:
        targets = enemies + ([boss] if boss else [])
        for enemy in targets:
            if bullet["rect"].colliderect(enemy.rect):
                try:
                    player_bullets.remove(bullet)
                    enemy.health -= 1
                    if enemy.health <= 0:
                        if enemy in enemies:
                            enemies.remove(enemy)
                        else:
                            boss = None
                        kill_count += 1
                        score += 10
                        if kill_count == 30 and not boss_spawned:
                            boss = Enemy(x=FRAME_WIDTH//2, y=100, is_boss=True)
                            boss_spawned = True
                except:
                    pass

    for bullet in enemy_bullets[:]:
        if bullet["rect"].colliderect(player):
            enemy_bullets.remove(bullet)
            player_lives -= 1
            if player_lives <= 0:
                reset_game()

    # Çizim
    screen.blit(player_img, player)

    for bullet in player_bullets:
        pygame.draw.rect(screen, (255, 0, 0), bullet["rect"])

    # Skor ve Can
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255))
    kill_text = font.render(f"Kills: {kill_count}", True, (255, 255, 0))

    screen.blit(score_text, (10, 40))
    screen.blit(lives_text, (10, 70))
    screen.blit(kill_text, (10, 10))

    # Power-up Etkinleştirme
    if power_up_ready and not power_up_active:
        power_up_text = font.render("Press ENTER for Power-Up!", True, (255, 0, 255))
        screen.blit(power_up_text, (FRAME_WIDTH//2 - 150, FRAME_HEIGHT//2))

    if keys[pygame.K_RETURN] and power_up_ready:
        power_up_active = True
        power_up_ready = False
        kill_count = 0  # Barı sıfırla

    pygame.display.flip()

pygame.quit()
sys.exit()
