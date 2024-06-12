#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <time.h>
#include <conio.h>

// Define constants for screen dimensions and frame boundaries
#define SCREEN_WIDTH 80
#define SCREEN_HEIGHT 25
#define FRAME_WIDTH 60
#define FRAME_HEIGHT 20
#define NUM_BULLETS 100
#define NUM_ENEMIES 5  // Number of enemies

// Player structure with an added symbol for representation
struct Player {
    int x, y;
    char symbol;
};

// Bullet structure
struct Bullet {
    int x, y;
    int active;
    char symbol;
};

// Enemy structure
struct Enemy {
    int x, y;
    int active;
    char symbol;
    int health;  // Added health property for enemies
};

// Function prototypes
void drawFrameBorder();
void updatePlayer(struct Player *player, char input);
void updateBullets(struct Bullet bullets[], int numBullets, int *remainingBullets, time_t *lastBulletTime);
void fireBullet(struct Bullet bullets[], int numBullets, struct Player player, int *remainingBullets);
void updateEnemies(struct Enemy enemies[], int numEnemies, struct Bullet bullets[], int numBullets, int *score);
void drawGame(const struct Player *player, const struct Bullet bullets[], int numBullets,
              const struct Enemy enemies[], int numEnemies, int score, int remainingBullets);
void showSplashScreen();

int main() {
    // Show splash screen
    showSplashScreen();

    // Draw the static frame border
    drawFrameBorder();

    struct Player player = {FRAME_WIDTH / 2, FRAME_HEIGHT / 2, 'P'}; // Initial player position at the center

    struct Bullet bullets[NUM_BULLETS];
    for (int i = 0; i < NUM_BULLETS; i++) {
        bullets[i] = (struct Bullet){0, 0, 0, '*'};
    }

    struct Enemy enemies[NUM_ENEMIES];
    for (int i = 0; i < NUM_ENEMIES; i++) {
        enemies[i] = (struct Enemy){rand() % FRAME_WIDTH, 0, 1, 'E', 1};  // Initialize enemies at random positions
    }

    int remainingBullets = NUM_BULLETS;
    int score = 0;
    time_t lastBulletTime = time(NULL);

    char input;
    int gameRunning = 1;

    // Game loop
    while (gameRunning) {
        if (kbhit()) {
            input = getch(); // Get keyboard input

            if (input == ' ') {
                // Fire a bullet when spacebar is pressed
                fireBullet(bullets, NUM_BULLETS, player, &remainingBullets);
            } else if (input == 'q') {
                // Quit the game when 'q' is pressed
                break;
            } else {
                // Update player position within the frame
                updatePlayer(&player, input);
            }
        }

        updateBullets(bullets, NUM_BULLETS, &remainingBullets, &lastBulletTime);
        updateEnemies(enemies, NUM_ENEMIES, bullets, NUM_BULLETS, &score);
        drawGame(&player, bullets, NUM_BULLETS, enemies, NUM_ENEMIES, score, remainingBullets);

        // Add a delay to control the game loop speed (you may adjust this based on your preference)
        Sleep(50); // Adjust this value for game speed
    }

    return 0;
}


void drawFrameBorder() {
    system("cls"); // Clear screen (Windows-specific)

    for (int i = 0; i < SCREEN_WIDTH; i++) {
        printf("!");
    }
    printf("\n");

    for (int i = 0; i < FRAME_HEIGHT; i++) {
        printf("!");
        for (int j = 0; j < FRAME_WIDTH; j++) {
            printf(" ");
        }
        printf("!\n");
    }

    for (int i = 0; i < SCREEN_WIDTH; i++) {
        printf("!");
    }
    printf("\n");
}

void updatePlayer(struct Player *player, char input) {
    // Update player position based on input
    switch (input) {
        case 'w':
            player->y -= 2; // Move 2 steps up
            break;
        case 's':
            player->y += 2; // Move 2 steps down
            break;
        case 'a':
            player->x -= 2; // Move 2 steps left
            break;
        case 'd':
            player->x += 2; // Move 2 steps right
            break;
    }

    // Ensure player stays within the frame
    player->x = (player->x < 0) ? 0 : (player->x >= FRAME_WIDTH) ? FRAME_WIDTH - 1 : player->x;
    player->y = (player->y < 0) ? 0 : (player->y >= FRAME_HEIGHT) ? FRAME_HEIGHT - 1 : player->y;
}

void updateBullets(struct Bullet bullets[], int numBullets, int *remainingBullets, time_t *lastBulletTime) {
    time_t currentTime = time(NULL);

    for (int i = 0; i < numBullets; i++) {
        // Move active bullets
        if (bullets[i].active) {
            bullets[i].y--; // Bullets move up
            // Check if bullet is out of bounds
            if (bullets[i].y < 0) {
                bullets[i].active = 0; // Deactivate bullet
                (*remainingBullets)--; // Decrease the remaining bullets
            }
        }
    }

    // Ensure remaining bullets don't go below zero
    *remainingBullets = (*remainingBullets < 0) ? 0 : *remainingBullets;

    // Check if all bullets are depleted
    if (*remainingBullets == 0) {
        // Check if 10 seconds have elapsed since the last bullet was depleted
        if (currentTime - *lastBulletTime >= 10) {
            // Refill bullets to 100
            *remainingBullets = NUM_BULLETS;
            *lastBulletTime = currentTime;
        }
    }
}

void fireBullet(struct Bullet bullets[], int numBullets, struct Player player, int *remainingBullets) {
    for (int i = 0; i < numBullets; i++) {
        if (!bullets[i].active && *remainingBullets > 0) {
            // If bullet is not active and there are remaining bullets, reset it to the player's position and set it as active
            bullets[i] = (struct Bullet){player.x, player.y - 1, 1, '*'};
            (*remainingBullets)--; // Decrease the remaining bullets
            break;
        }
    }
}

void updateEnemies(struct Enemy enemies[], int numEnemies, struct Bullet bullets[], int numBullets, int *score) {
    // Move enemies downward
    for (int i = 0; i < numEnemies; i++) {
        if (enemies[i].active) {
            enemies[i].y += 1; // Move enemy 1 step downward
            // Check if enemy is out of bounds
            if (enemies[i].y >= FRAME_HEIGHT) {
                // Respawn enemy at random position above the frame
                enemies[i] = (struct Enemy){rand() % FRAME_WIDTH, rand() % (FRAME_HEIGHT / 2), 1, 'E', 1};
            }
        }
    }

    // Check for bullet-enemy collisions
    for (int i = 0; i < numBullets; i++) {
        if (bullets[i].active) {
            for (int j = 0; j < numEnemies; j++) {
                if (enemies[j].active && bullets[i].x == enemies[j].x && bullets[i].y == enemies[j].y) {
                    // Bullet hit an active enemy
                    bullets[i].active = 0; // Deactivate bullet
                    enemies[j].health--; // Decrease enemy health
                    if (enemies[j].health <= 0) {
                        // Enemy destroyed
                        enemies[j].active = 0; // Deactivate enemy
                        (*score)++; // Increase score
                    }
                }
            }
        }
    }
}


void drawGame(const struct Player *player, const struct Bullet bullets[], int numBullets,
              const struct Enemy enemies[], int numEnemies, int score, int remainingBullets) {
    // Create a grid representing the frame
    char frameGrid[FRAME_HEIGHT][FRAME_WIDTH];

    // Initialize the frame grid with empty spaces
    for (int i = 0; i < FRAME_HEIGHT; i++) {
        for (int j = 0; j < FRAME_WIDTH; j++) {
            frameGrid[i][j] = ' ';
        }
    }

    // Place the player symbol on the frame grid
    frameGrid[player->y][player->x] = player->symbol;

    // Place the bullet symbols on the frame grid and update their position
    for (int i = 0; i < numBullets; i++) {
        if (bullets[i].active && bullets[i].y >= 0) {
            frameGrid[bullets[i].y][bullets[i].x] = bullets[i].symbol;
        }
    }

    // Place the enemy symbols on the frame grid and update their position
    for (int i = 0; i < numEnemies; i++) {
        if (enemies[i].active && enemies[i].y < FRAME_HEIGHT) {
            frameGrid[enemies[i].y][enemies[i].x] = enemies[i].symbol;
        }
    }

    // Set the cursor position to the top-left corner of the frame
    COORD coord;
    coord.X = 0;
    coord.Y = 0;
    SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord);

    // Print the frame grid to the console
    for (int i = 0; i < FRAME_HEIGHT; i++) {
        for (int j = 0; j < FRAME_WIDTH; j++) {
            printf("%c", frameGrid[i][j]);
        }
        printf("\n");
    }

    // Print the remaining bullets, score, and instructions
    printf("Remaining Bullets: %d\tScore: %d\n", remainingBullets, score);
    printf("Controls: WASD to move, Spacebar to shoot, Q to quit\n");
}

void showSplashScreen() {
    system("cls"); // Clear screen (Windows-specific)
    printf("Welcome to the basic Touhou-like game! Press Enter to start\n");
    while (getchar() != '\n'); // Wait for Enter key
}
// Main function that runs the game loop until the user quits or all enemies are defeated