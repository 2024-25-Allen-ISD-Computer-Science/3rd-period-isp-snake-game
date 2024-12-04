import pygame
import time
import random

# Initialize pygame
pygame.init()

# Set display dimensions
width, height = 600, 400
display = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
dark_gray = (50, 50, 50)
light_green = (144, 238, 144)

# Game variables
snake_block = 10
snake_speed = 15
clock = pygame.time.Clock()
font_style = pygame.font.SysFont(None, 35)
score_font = pygame.font.SysFont(None, 35)

# Load sounds
pygame.mixer.init()
background_music = "background_music.mp3"  # Background music
food_sound = pygame.mixer.Sound("food.mp3")  # SFX for when the snake eats food
collision_sound = pygame.mixer.Sound("collision.mp3")  # SFX for obstacle-snake collision 
pygame.mixer.music.load(background_music)
pygame.mixer.music.set_volume(0.5)  # Decrease volume to 50%
pygame.mixer.music.play(-1)  # Loop the background music

# Function to display the score
def display_score(score):
    value = score_font.render("Score: " + str(score), True, yellow)
    display.blit(value, [0, 0])

# Function to display the snake
def draw_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(display, black, [x[0], x[1], snake_block, snake_block])

# Function to display messages on the screen
def display_message(msg, color, y_offset=0):
    mesg = font_style.render(msg, True, color)
    display.blit(mesg, [width / 6, height / 3 + y_offset])

# Function to draw obstacles
def draw_obstacles(obstacles):
    for obs in obstacles:
        pygame.draw.rect(display, red, obs)

# Maps with adjusted obstacles
maps = {
    "blue": {"background": blue, "obstacles": []},  # No obstacles
    "green": {"background": light_green, "obstacles": [
        pygame.Rect(100, 100, 400, 10),  # Horizontal bar
        pygame.Rect(200, 200, 10, 100)   # Vertical bar
    ]},
    "dark": {"background": dark_gray, "obstacles": [
        pygame.Rect(50, 50, 500, 10),    # Top horizontal bar
        pygame.Rect(50, 340, 500, 10),  # Bottom horizontal bar
        pygame.Rect(150, 150, 300, 10), # Middle horizontal bar
    ]}
}

# Main menu function
def main_menu():
    menu_active = True
    selected_map = None

    while menu_active:
        display.fill(blue)
        display_message("Welcome to Snake Game!", white, y_offset=-50)
        display_message("Press 1 for Blue Map", white, y_offset=0)
        display_message("Press 2 for Green Map", white, y_offset=50)
        display_message("Press 3 for Dark Map", white, y_offset=100)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_map = "blue"
                    menu_active = False
                elif event.key == pygame.K_2:
                    selected_map = "green"
                    menu_active = False
                elif event.key == pygame.K_3:
                    selected_map = "dark"
                    menu_active = False

    game_loop(selected_map)

# Main game function
def game_loop(selected_map):
    game_over = False
    game_close = False

    # Get map details
    map_details = maps[selected_map]
    background_color = map_details["background"]
    obstacles = map_details["obstacles"]

    # Starting position of the snake
    x1 = width / 2
    y1 = height / 2

    # Movement coordinates
    x1_change = 0
    y1_change = 0

    # Snake attributes
    snake_list = []
    snake_length = 1

    # Food coordinates
    foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

    # Main game loop
    while not game_over:

        while game_close:
            display.fill(background_color)
            display_message("You Lost! Press Q-Quit or C-Play Again", red)
            display_score(snake_length - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop(selected_map)

        # Handling keystrokes for movement
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        # Boundaries check
        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            pygame.mixer.Sound.play(collision_sound)
            game_close = True

        # Updating position
        x1 += x1_change
        y1 += y1_change
        display.fill(background_color)

        # Draw food and obstacles
        pygame.draw.rect(display, red, [foodx, foody, snake_block, snake_block])
        draw_obstacles(obstacles)

        # Snake movement
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Check for collision with itself
        for x in snake_list[:-1]:
            if x == snake_head:
                pygame.mixer.Sound.play(collision_sound)
                game_close = True

        # Check for collision with obstacles
        for obs in obstacles:
            if obs.collidepoint(x1, y1):
                pygame.mixer.Sound.play(collision_sound)
                game_close = True

        draw_snake(snake_block, snake_list)
        display_score(snake_length - 1)
        pygame.display.update()

        # Check if snake has eaten the food
        if x1 == foodx and y1 == foody:
            pygame.mixer.Sound.play(food_sound)
            foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
            snake_length += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Start the main menu
main_menu()
