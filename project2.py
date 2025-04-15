import pygame
import random
import sys

# Ekran boyutları
FRAME_WIDTH = 600
FRAME_HEIGHT = 400
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED = 2
NUM_ENEMIES = 5
PLAYER_LIVES = 3

pygame.init()

screen = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))
pygame.display.set_caption("Touhou Like GUI - Settings Menu")

clock = pygame.time.Clock()

# Müzik
def start_music():
    pygame.mixer.music.load("music.mp3")
    pygame.mixer.music.play(-1)

start_music()

# Arka plan
background = pygame.image.load("image.png").convert()
background = pygame.transform.scale(background, (FRAME_WIDTH, FRAME_HEIGHT))

# Oyuncu ve düşman görselleri
player_sprites = [
    pygame.image.load("player1.png").convert_alpha(),
    pygame.image.load("player2.png").convert_alpha()
]
for i in range(len(player_sprites)):
    player_sprites[i] = pygame.transform.scale(player_sprites[i], (40, 40))

current_player_sprite = 0  # Başlangıç sprite'ı

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

# Fontlar
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Oyuncu
player = pygame.Rect(FRAME_WIDTH // 2, FRAME_HEIGHT - 60, 40, 40)
player_lives = PLAYER_LIVES

# Mermiler
bullets = []

# Düşmanlar
enemies = [pygame.Rect(random.randint(0, FRAME_WIDTH-40), random.randint(-150, -40), 40, 40) for _ in range(NUM_ENEMIES)]

score = 0
fire_mode = 1  # 1: Tekli, 2: Çiftli, 3: Üçlü
game_over = False
paused = False

# Menü Butonları
menu_buttons = [
    {"text": "Resume Game", "rect": pygame.Rect(200, 100, 200, 40)},
    {"text": "Change Character", "rect": pygame.Rect(200, 150, 200, 40)},
    {"text": "Volume Up", "rect": pygame.Rect(200, 200, 200, 40)},
    {"text": "Volume Down", "rect": pygame.Rect(200, 250, 200, 40)},
    {"text": "Main Menu", "rect": pygame.Rect(200, 300, 200, 40)}
]

# Fonksiyonlar
def reset_game():
    global player, player_lives, bullets, enemies, score, game_over, fire_mode, paused
    player = pygame.Rect(FRAME_WIDTH // 2, FRAME_HEIGHT - 60, 40, 40)
    player_lives = PLAYER_LIVES
    bullets = []
    enemies = [pygame.Rect(random.randint(0, FRAME_WIDTH-40), random.randint(-150, -40), 40, 40) for _ in range(NUM_ENEMIES)]
    score = 0
    fire_mode = 1
    game_over = False
    paused = False
    start_music()  # müzik yeniden başlasın

def draw_menu():
    screen.fill((30, 30, 30))  # Menü arka planı

    title = big_font.render("SETTINGS", True, (255, 255, 255))
    screen.blit(title, (FRAME_WIDTH // 2 - 100, 30))

    for button in menu_buttons:
        pygame.draw.rect(screen, (70, 70, 70), button["rect"])
        text = font.render(button["text"], True, (255, 255, 255))
        screen.blit(text, (button["rect"].x + 10, button["rect"].y + 5))

def change_character():
    global current_player_sprite
    current_player_sprite = (current_player_sprite + 1) % len(player_sprites)

# Ana döngü
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if paused:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, button in enumerate(menu_buttons):
                    if button["rect"].collidepoint(event.pos):
                        if idx == 0:  # Resume Game
                            paused = False
                        elif idx == 1:  # Change Character
                            change_character()
                        elif idx == 2:  # Volume Up
                            pygame.mixer.music.set_volume(min(pygame.mixer.music.get_volume() + 0.1, 1.0))
                        elif idx == 3:  # Volume Down
                            pygame.mixer.music.set_volume(max(pygame.mixer.music.get_volume() - 0.1, 0.0))
                        elif idx == 4:  # Main Menu
                            reset_game()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.time.wait(200)  # Hızlı basmayı engelle
        paused = not paused

    if not paused and not game_over:
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player.right < FRAME_WIDTH:
            player.x += PLAYER_SPEED
        if keys[pygame.K_UP] and player.top > 0:
            player.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and player.bottom < FRAME_HEIGHT:
            player.y += PLAYER_SPEED
        if keys[pygame.K_SPACE]:
            if len(bullets) < 100:
                if fire_mode == 1:
                    bullets.append(pygame.Rect(player.centerx - 2, player.top, 4, 10))
                elif fire_mode == 2:
                    bullets.append(pygame.Rect(player.centerx - 10, player.top, 4, 10))
                    bullets.append(pygame.Rect(player.centerx + 6, player.top, 4, 10))
                elif fire_mode == 3:
                    bullets.append(pygame.Rect(player.centerx - 15, player.top, 4, 10))
                    bullets.append(pygame.Rect(player.centerx, player.top, 4, 10))
                    bullets.append(pygame.Rect(player.centerx + 15, player.top, 4, 10))

        # Mermileri güncelle
        for bullet in bullets[:]:
            bullet.y -= BULLET_SPEED
            if bullet.bottom < 0:
                bullets.remove(bullet)

        # Düşmanları güncelle
        for enemy in enemies[:]:
            enemy.y += ENEMY_SPEED
            if enemy.top > FRAME_HEIGHT:
                enemy.x = random.randint(0, FRAME_WIDTH-40)
                enemy.y = random.randint(-100, -40)

        # Çarpışmalar
        enemies_to_remove = []
        bullets_to_remove = []

        for enemy in enemies:
            if player.colliderect(enemy):
                player_lives -= 1
                enemies_to_remove.append(enemy)
                if player_lives == 0:
                    game_over = True
            for bullet in bullets:
                if bullet.colliderect(enemy):
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
                    score += 1

        for bullet in bullets_to_remove:
            if bullet in bullets:
                bullets.remove(bullet)

        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)
                enemies.append(pygame.Rect(random.randint(0, FRAME_WIDTH-40), random.randint(-100, -40), 40, 40))

    # Ekranı çiz
    if paused:
        draw_menu()
    else:
        screen.blit(background, (0, 0))
        if not game_over:
            screen.blit(player_sprites[current_player_sprite], player)

            for bullet in bullets:
                pygame.draw.rect(screen, (255, 0, 0), bullet)

            for enemy in enemies:
                screen.blit(enemy_img, enemy)

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255))

            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (10, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()
