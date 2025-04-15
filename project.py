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
pygame.display.set_caption("Touhou Like GUI with Background and Music")

clock = pygame.time.Clock()

# Müzik
pygame.mixer.music.load("music.mp3")  # Buraya müzik dosya adını yaz
pygame.mixer.music.play(-1)  # Sonsuz döngüde çal

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

# Oyuncu
player = pygame.Rect(FRAME_WIDTH // 2, FRAME_HEIGHT - 60, 40, 40)
player_lives = PLAYER_LIVES

# Mermiler
bullets = []

# Düşmanlar
enemies = [pygame.Rect(random.randint(0, FRAME_WIDTH-40), random.randint(-150, -40), 40, 40) for _ in range(NUM_ENEMIES)]

score = 0

# Ana döngü
running = True
while running:
    clock.tick(60)  # 60 FPS

    # Olaylar
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Tuşlar
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
        if len(bullets) < 100:
            bullet = pygame.Rect(player.centerx - 2, player.top, 4, 10)
            bullets.append(bullet)

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
                running = False
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
    screen.blit(background, (0, 0))  # Arka planı çiz

    screen.blit(player_img, player)  # Oyuncu sprite'ı çiz

    for bullet in bullets:
        pygame.draw.rect(screen, (255, 0, 0), bullet)

    for enemy in enemies:
        screen.blit(enemy_img, enemy)  # Düşman sprite'ı çiz

    # Skor ve canları çiz
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255))

    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))

    pygame.display.flip()

# Oyun bitti
pygame.quit()
sys.exit()
