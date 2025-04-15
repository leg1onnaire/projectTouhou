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
pygame.display.set_caption("Touhou Like GUI - Extended")

clock = pygame.time.Clock()

# Müzik
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1)
music_playing = True

# Arka plan
background = pygame.image.load("image.png").convert()
background = pygame.transform.scale(background, (FRAME_WIDTH, FRAME_HEIGHT))

# Oyuncu ve düşman görselleri
player_img = pygame.image.load("player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (40, 40))

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

# Font
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
fire_mode = 1  # 1: Tekli, 2: İkili, 3: Üçlü
game_over = False

# Restart butonu
restart_button = pygame.Rect(FRAME_WIDTH // 2 - 60, FRAME_HEIGHT // 2 + 50, 120, 40)

def reset_game():
    global player, player_lives, bullets, enemies, score, game_over, fire_mode
    player = pygame.Rect(FRAME_WIDTH // 2, FRAME_HEIGHT - 60, 40, 40)
    player_lives = PLAYER_LIVES
    bullets = []
    enemies = [pygame.Rect(random.randint(0, FRAME_WIDTH-40), random.randint(-150, -40), 40, 40) for _ in range(NUM_ENEMIES)]
    score = 0
    fire_mode = 1
    game_over = False

def draw_restart_screen():
    screen.blit(background, (0, 0))
    game_over_text = big_font.render("GAME OVER", True, (255, 0, 0))
    restart_text = font.render("Restart", True, (255, 255, 255))
    
    screen.blit(game_over_text, (FRAME_WIDTH // 2 - 150, FRAME_HEIGHT // 2 - 100))
    pygame.draw.rect(screen, (0, 0, 0), restart_button)
    screen.blit(restart_text, (restart_button.x + 15, restart_button.y + 5))

    pygame.display.flip()

# Ana döngü
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        if keys[pygame.K_ESCAPE]:
            if music_playing:
                pygame.mixer.music.pause()
                music_playing = False
            else:
                pygame.mixer.music.unpause()
                music_playing = True

        if keys[pygame.K_n]:
            fire_mode += 1
            if fire_mode > 3:
                fire_mode = 1
            pygame.time.wait(200)  # Çok hızlı basınca hemen değişmesin

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

    if not game_over:
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
    screen.blit(background, (0, 0))

    if not game_over:
        screen.blit(player_img, player)

        for bullet in bullets:
            pygame.draw.rect(screen, (255, 0, 0), bullet)

        for enemy in enemies:
            screen.blit(enemy_img, enemy)

        # Skor ve canları çiz
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255))

        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
    else:
        draw_restart_screen()

    pygame.display.flip()

pygame.quit()
sys.exit()
