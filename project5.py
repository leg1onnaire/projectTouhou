import pygame
import random
import math
import sys

# Ekran boyutları
GAME_WIDTH = 400
PANEL_WIDTH = 200
SCREEN_WIDTH = GAME_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = 850

PLAYER_SPEED = 5
PLAYER_BULLET_SPEED = 8
ENEMY_BULLET_SPEED = 2
ENEMY_SPEED = 2
PLAYER_LIVES = 3

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Touhou Style Bullet Hell - Clean Boss Fight")

clock = pygame.time.Clock()

# Müzik
def start_music():
    pygame.mixer.music.load("music.mp3")
    pygame.mixer.music.play(-1)

start_music()

# Resimler
background = pygame.image.load("image.png").convert()
background = pygame.transform.scale(background, (GAME_WIDTH, SCREEN_HEIGHT))

player_img = pygame.image.load("player1.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (40, 40))

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

boss_img = pygame.image.load("boss.png").convert_alpha()
boss_img = pygame.transform.scale(boss_img, (60, 60))

bullet_img = pygame.image.load("bullet.png").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (20, 20))

# Fontlar
font = pygame.font.SysFont(None, 36)
jp_font = pygame.font.SysFont("MS Gothic", 28)

# Oyuncu
player = pygame.Rect(GAME_WIDTH // 2, SCREEN_HEIGHT - 120, 40, 40)
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
power_up_bar_width = 150

# Atış Modu
fire_mode = 1  # 1 = Tekli, 2 = Çiftli, 3 = Üçlü

# Boss HP için
boss_max_health = 50

class Enemy:
    def __init__(self, x=None, y=None, is_boss=False):
        if x is None:
            self.x = random.randint(40, GAME_WIDTH - 40)
        else:
            self.x = x
        if y is None:
            self.y = -40
        else:
            self.y = y
        self.is_boss = is_boss
        self.health = 5 if not is_boss else boss_max_health
        self.img = enemy_img if not is_boss else boss_img
        self.rect = self.img.get_rect(center=(self.x, self.y))
        self.timer = 0

    def update(self):
        if self.is_boss:
            self.timer += 0.03
            self.x = GAME_WIDTH // 2 + math.cos(self.timer) * 150  # Sağa sola büyük hareket
            self.y = 100 + math.sin(self.timer) * 30                # Hafif aşağı yukarı dalgalanma
        else:
            self.y += ENEMY_SPEED
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.img, self.rect)

def spawn_enemy():
    if len(enemies) < 5 and not boss_spawned:
        enemies.append(Enemy())

def fire_enemy_bullets(enemy):
    if enemy.is_boss:
        for angle in range(0, 360, 30):  # Boss her yöne mermi atar
            rad = math.radians(angle)
            dx = math.cos(rad) * ENEMY_BULLET_SPEED
            dy = math.sin(rad) * ENEMY_BULLET_SPEED
            bullet = {"rect": bullet_img.get_rect(center=enemy.rect.center), "dx": dx, "dy": dy}
            enemy_bullets.append(bullet)
    else:
        bullet = {"rect": bullet_img.get_rect(center=enemy.rect.center), "dx": 0, "dy": ENEMY_BULLET_SPEED}
        enemy_bullets.append(bullet)

def reset_game():
    global player, player_lives, score, player_bullets, enemy_bullets, enemies, boss, kill_count, boss_spawned, power_up_ready, power_up_active, fire_mode
    player = pygame.Rect(GAME_WIDTH // 2, SCREEN_HEIGHT - 120, 40, 40)
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
    fire_mode = 1
    start_music()

# Ana döngü
running = True
enemy_spawn_timer = 0
enemy_fire_timer = 0

while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    # Oyun alanı
    screen.blit(background, (0, 0))

    # Bilgi paneli
    pygame.draw.rect(screen, (20, 20, 20), (GAME_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] and player.right < GAME_WIDTH - player.width:
        player.x += PLAYER_SPEED
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN] and player.bottom < SCREEN_HEIGHT:
        player.y += PLAYER_SPEED

    if keys[pygame.K_SPACE]:
        if len(player_bullets) < 10 or power_up_active:
            if fire_mode == 1:
                bullet = {"rect": pygame.Rect(player.centerx - 2, player.top, 4, 10)}
                player_bullets.append(bullet)
            elif fire_mode == 2:
                bullet1 = {"rect": pygame.Rect(player.centerx - 10, player.top, 4, 10)}
                bullet2 = {"rect": pygame.Rect(player.centerx + 6, player.top, 4, 10)}
                player_bullets.extend([bullet1, bullet2])
            elif fire_mode == 3:
                bullet1 = {"rect": pygame.Rect(player.centerx - 15, player.top, 4, 10)}
                bullet2 = {"rect": pygame.Rect(player.centerx, player.top, 4, 10)}
                bullet3 = {"rect": pygame.Rect(player.centerx + 15, player.top, 4, 10)}
                player_bullets.extend([bullet1, bullet2, bullet3])

    if keys[pygame.K_n]:
        fire_mode += 1
        if fire_mode > 3:
            fire_mode = 1
        pygame.time.wait(200)

    # Oyuncu mermileri
    for bullet in player_bullets[:]:
        bullet["rect"].y -= PLAYER_BULLET_SPEED
        if bullet["rect"].bottom < 0:
            player_bullets.remove(bullet)

    # Eğer boss spawn olmadıysa normal düşmanlar doğsun
    if not boss_spawned:
        spawn_enemy()

    for enemy in enemies[:]:
        enemy.update()
        enemy.draw(screen)
        if enemy.rect.top > SCREEN_HEIGHT:
            enemies.remove(enemy)

    if boss:
        boss.update()
        boss.draw(screen)

    # Düşman mermileri
    enemy_fire_timer += 1
    if enemy_fire_timer > 40:
        if not boss_spawned:
            for enemy in enemies:
                fire_enemy_bullets(enemy)
        if boss:
            fire_enemy_bullets(boss)
        enemy_fire_timer = 0

    for bullet in enemy_bullets[:]:
        bullet["rect"].x += bullet["dx"]
        bullet["rect"].y += bullet["dy"]
        screen.blit(bullet_img, bullet["rect"])
        if bullet["rect"].top > SCREEN_HEIGHT or bullet["rect"].bottom < 0 or bullet["rect"].left > GAME_WIDTH or bullet["rect"].right < 0:
            enemy_bullets.remove(bullet)

    # Çarpışmalar
    for bullet in player_bullets[:]:
        # Mermiler birbirini imha edebilir
        for ebullet in enemy_bullets[:]:
            if bullet["rect"].colliderect(ebullet["rect"]):
                try:
                    player_bullets.remove(bullet)
                    enemy_bullets.remove(ebullet)
                except:
                    pass

        # Oyuncu mermisi düşmana çarparsa
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
                            boss_spawned = False
                        kill_count += 1
                        score += 10
                        if kill_count == 30 and not boss_spawned:
                            boss = Enemy(x=GAME_WIDTH//2, y=100, is_boss=True)
                            enemies.clear()  # Boss spawn olunca tüm küçük düşmanları temizle
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

    # Bilgi Paneli
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255))
    kills_text = font.render(f"Kills: {kill_count}", True, (255, 255, 255))

    screen.blit(score_text, (GAME_WIDTH + 20, 50))
    screen.blit(lives_text, (GAME_WIDTH + 20, 90))
    screen.blit(kills_text, (GAME_WIDTH + 20, 130))

    # Boss HP Bar
    if boss:
        hp_ratio = boss.health / boss_max_health
        pygame.draw.rect(screen, (255, 0, 0), (GAME_WIDTH + 20, 200, 160 * hp_ratio, 20))
        hp_label = font.render("Boss HP", True, (255, 255, 255))
        screen.blit(hp_label, (GAME_WIDTH + 20, 170))

    # Japonca yazı
    jp_text = jp_font.render("東方弾幕 - 弾幕地獄", True, (255, 255, 255))
    screen.blit(jp_text, (GAME_WIDTH//2 - 100, SCREEN_HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
