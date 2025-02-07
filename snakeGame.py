import pygame
import time
import random
import math

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
forest_green = (34, 139, 34)
crimson = (220, 20, 60)
saddle_brown = (139, 69, 19)

# Game variables
snake_block = 10
snake_speed = 15
obstacle_speed = 2
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

# Volume settings
master_volume = 0.5
music_volume = 0.5
sfx_volume = 0.5

def display_score(score):
    value = score_font.render("Score: " + str(score), True, yellow)
    display.blit(value, [0, 0])

def display_high_score(score):
    value = score_font.render("High Score: " + str(score), True, yellow)
    display.blit(value, [width - 200, 0])

def draw_snake(snake_block, snake_list):
    for i, segment in enumerate(reversed(snake_list)):
        x, y = segment
        center_x, center_y = x + snake_block // 2, y + snake_block // 2
        if i == 0:  # Head
            # Draw head with eyes
            pygame.draw.ellipse(display, forest_green, [x, y, snake_block + 2, snake_block])
            eye_radius = snake_block // 5
            # Left Eye
            pygame.draw.circle(display, black, (center_x - 3, center_y - 3), eye_radius)
            # Right Eye
            pygame.draw.circle(display, black, (center_x + 3, center_y - 3), eye_radius)
        else:  # Body
            pygame.draw.ellipse(display, forest_green, [x + 1, y + 1, snake_block - 2, snake_block - 2])
        if i == len(snake_list) - 1:  # Tail Tapering
            pygame.draw.ellipse(display, forest_green, [x + 3, y + 3, snake_block - 4, snake_block - 4])

def draw_food(x, y):
    pygame.draw.ellipse(display, (0, 0, 0), [x - 5, y + 10, 20, 5])
    pygame.draw.circle(display, red, (x, y), 10)
    pygame.draw.ellipse(display, white, [x + 2, y - 4, 4, 2])
    pygame.draw.polygon(display, green, [(x + 5, y - 7), (x + 3, y - 12), (x + 10, y - 10)])
    pygame.draw.rect(display, black, [x - 1, y - 12, 2, 5])

def display_message(msg, color, y_offset=0, x_offset=width/6, underline=False):
    mesg = font_style.render(msg, True, color)
    display.blit(mesg, [x_offset, height / 3 + y_offset])

    if underline:
        underline_width = mesg.get_width()
        underline_height = 2  # Thickness of the underline
        underline_x = x_offset
        underline_y = height / 3 + y_offset + mesg.get_height()
        pygame.draw.line(display, color, (underline_x, underline_y), (underline_x + underline_width, underline_y), underline_height)

def draw_obstacles(obstacles):
    for obs in obstacles:
        brick_color = (139, 69, 19)
        mortar_color = (211, 211, 211)
        brick_width = 20
        brick_height = 10
        pygame.draw.rect(display, mortar_color, obs)
        rows = obs.height // brick_height
        cols = obs.width // brick_width
        for row in range(rows):
            for col in range(cols):
                x = obs.left + col * brick_width
                y = obs.top + row + brick_height
                offset = (row % 2) * (brick_width // 2)
                if x + offset + brick_width <= obs.right:
                    pygame.draw.rect(display, brick_color, pygame.Rect(x + offset, y, brick_width - 2, brick_height - 2))

def normalize_velocity(velocity, speed):
    magnitude = math.sqrt(velocity[0]**2 + velocity[1]**2)
    return [speed * velocity[0] / magnitude, speed * velocity[1] / magnitude]

def move_obstacles(obstacles, velocities):
    for i, obs in enumerate(obstacles):
        obs.x += velocities[i][0]  # Update x position
        obs.y += velocities[i][1]  # Update y position

        # Reverse direction if hitting boundaries
        if obs.left <= 0 or obs.right >= width:
            velocities[i][0] = -velocities[i][0]
        if obs.top <= 0 or obs.bottom >= height:
            velocities[i][1] = -velocities[i][1]

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

def draw_slider(label, x, y, value):
    pygame.draw.rect(display, white, [x, y, 200, 10])
    pygame.draw.rect(display, green, [x, y, int(value * 200), 10])
    text = font_style.render(label, True, white)
    display.blit(text, (x, y - 30))

def options_menu():
    global master_volume, music_volume, sfx_volume

    options_active = True
    while options_active:
        display.fill(blue)
        draw_slider("Master Volume", 200, 100, master_volume)
        draw_slider("Music Volume", 200, 150, music_volume)
        draw_slider("SFX Volume", 200, 200, sfx_volume)

        instructions = font_style.render("Press ESC to return to the main menu", True, yellow)
        display.blit(instructions, (50, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    options_active = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if 200 <= mouse_x <= 400:
                    if 100 <= mouse_y <= 110:
                        master_volume = (mouse_x - 200) / 200
                        pygame.mixer.music.set_volume(master_volume * music_volume)
                        food_sound.set_volume(master_volume * sfx_volume)
                        collision_sound.set_volume(master_volume * sfx_volume)
                    elif 150 <= mouse_y <= 160:
                        music_volume = (mouse_x - 200) / 200
                        pygame.mixer.music.set_volume(master_volume * music_volume)
                    elif 200 <= mouse_y <= 210:
                        sfx_volume = (mouse_x - 200) / 200
                        food_sound.set_volume(master_volume * sfx_volume)
                        collision_sound.set_volume(master_volume * sfx_volume)
# Function to show "How to Play" instructions
def how_to_play_screen():
    display.fill(blue)
    display_message("How to Play", white, y_offset=-75, x_offset = 225)
    display_message("Use WASD or Arrow Keys to move the snake.", white, y_offset=0, x_offset=25)
    display_message("Touch the big yellow object to turn into a ghost!", white, y_offset=50,x_offset=25)
    display_message("While a ghost, you can pass through obstacles.", white, y_offset=100,x_offset=25)
    display_message("Press ESC to return to the main menu.", white, y_offset=200,x_offset=25) 
    pygame.display.update()

    # Wait for the player to press ESC to return to the main menu
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    waiting = False
def main_menu():
    menu_active = True
    selected_map = None
    high_score = 0
    while menu_active:
        display.fill(blue)
        display_message("Welcome to Snake Game!", white, y_offset=-90, x_offset=150, underline=True)
        display_message("Press 1 for Blue Map", white, y_offset=-40, x_offset = 150)
        display_message("Press 2 for Green Map", white, y_offset=10, x_offset = 150)
        display_message("Press 3 for Dark Map", white, y_offset=60, x_offset = 150)
        display_message("Press O for Options", white, y_offset=110, x_offset = 150)
        display_message("Press H for How to Play", white, y_offset = 160, x_offset = 150)
        display_high_score(high_score)
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
                elif event.key == pygame.K_o:
                    options_menu()
                elif event.key == pygame.K_h:  
                    how_to_play_screen()
    game_loop(selected_map, high_score)

# Power-up variables
power_up_active = False
power_up_timer = 0
power_up_rect = None
power_up_creation_time = 0  # Timestamp when the power-up is created

# Function to draw the power-up
def draw_power_up(power_up_rect):
    pygame.draw.rect(display, yellow, power_up_rect)

# Function to generate a random power-up
def generate_power_up():
    if random.random() < 1/3:  # 1/3 chance of power-up generation
        power_up_x = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
        power_up_y = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
        return pygame.Rect(power_up_x, power_up_y, snake_block * 4, snake_block * 4)
    return None

# Function to draw the snake with ghostly effect when power-up is active
def draw_ghostly_snake(snake_block, snake_list):
    for x in snake_list:
        if power_up_active:  # If power-up is active, make snake look ghostly
            for i, segment in enumerate(reversed(snake_list)):
                x, y = segment
                center_x, center_y = x + snake_block // 2, y + snake_block // 2
                if i == 0:  # Head
                    # Draw head with eyes
                    pygame.draw.ellipse(display, white, [x, y, snake_block + 2, snake_block])
                    eye_radius = snake_block // 5
                    # Left Eye
                    pygame.draw.circle(display, blue, (center_x - 3, center_y - 3), eye_radius)
                    # Right Eye
                    pygame.draw.circle(display, blue, (center_x + 3, center_y - 3), eye_radius)
                else:  # Body
                    pygame.draw.ellipse(display, white, [x + 1, y + 1, snake_block - 2, snake_block - 2])
                if i == len(snake_list) - 1:  # Tail Tapering
                    pygame.draw.ellipse(display, white, [x + 3, y + 3, snake_block - 4, snake_block - 4])
        else:
            draw_snake(snake_block, snake_list)

# Achievement System
class AchievementSystem:
    def __init__(self):
        self.achievements = {
            "map_3_flawless": {"earned": False, "message": "Flawless on Map 3! +20 Shop Points", "points": 20},
            "score_100_total": {"earned": False, "message": "100 Total Score! +30 Shop Points", "points": 30}
        }
        self.total_score = 0
        self.achievement_display_time = 3  # Duration to display the achievement banner
        self.achievement_queue = []  # Queue for earned achievements
        self.current_achievement = None
        self.achievement_start_time = None

    def check_achievements(self, score, selected_map, alive):
        # Check "Flawless on Map 3" achievement
        if not self.achievements["map_3_flawless"]["earned"] and selected_map == "dark" and score >= 25 and alive:
            self.earn_achievement("map_3_flawless")

        # Track total score for "100 Total Score" achievement
        self.total_score += score
        if not self.achievements["score_100_total"]["earned"] and self.total_score >= 100:
            self.earn_achievement("score_100_total")

    def earn_achievement(self, achievement_key):
        if achievement_key in self.achievements:
            self.achievements[achievement_key]["earned"] = True
            self.achievement_queue.append(self.achievements[achievement_key]["message"])
            print(f"Achievement Unlocked: {self.achievements[achievement_key]['message']}")  # Debug message

    def update_achievement_display(self):
        if not self.current_achievement and self.achievement_queue:
            self.current_achievement = self.achievement_queue.pop(0)
            self.achievement_start_time = time.time()

        if self.current_achievement and time.time() - self.achievement_start_time > self.achievement_display_time:
            self.current_achievement = None  # Remove achievement after display duration

    def draw_achievement_banner(self, display):
        if self.current_achievement:
            banner_rect = pygame.Rect(50, 50, 500, 50)
            pygame.draw.rect(display, black, banner_rect)
            pygame.draw.rect(display, yellow, banner_rect, 3)
            text = font_style.render(self.current_achievement, True, white)
            display.blit(text, (banner_rect.x + 10, banner_rect.y + 10))

def game_loop(selected_map, high_score):
    achievement_system = AchievementSystem()
    global power_up_active, power_up_timer, power_up_rect, power_up_creation_time
    game_over = False
    game_close = False
    score = 0

    map_details = maps[selected_map]
    background_color = map_details["background"]
    obstacles = map_details["obstacles"]

    velocities = [normalize_velocity([random.choice([-1, 1]), random.choice([-1, 1])], obstacle_speed) for _ in obstacles]

    x1 = width / 2
    y1 = height / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    snake_length = 1

    foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

    while not game_over:
        while game_close:
            display.fill(background_color)
            display_message("You Lost! Press Q-Quit or C-Play Again", red)
            display_score(snake_length - 1)
            if snake_length - 1 > high_score:
                high_score = snake_length - 1
            display_high_score(high_score)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop(selected_map, high_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            pygame.mixer.Sound.play(collision_sound)
            game_close = True

        x1 += x1_change
        y1 += y1_change
        display.fill(background_color)

        move_obstacles(obstacles, velocities)
        draw_obstacles(obstacles)

        draw_food(foodx, foody)

        # Draw the power-up if it exists
        if power_up_rect:
            draw_power_up(power_up_rect)

        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                pygame.mixer.Sound.play(collision_sound)
                game_close = True

        for obs in obstacles:
            if obs.collidepoint(x1, y1):
                if not power_up_active:  # Only collide with obstacles if power-up is not active
                    pygame.mixer.Sound.play(collision_sound)
                    game_close = True

        # Draw the snake with the ghostly effect when power-up is active
        draw_ghostly_snake(snake_block, snake_list)
        display_score(snake_length - 1)
        display_high_score(high_score)
        achievement_system.update_achievement_display()
        achievement_system.draw_achievement_banner(display)
        pygame.display.update()

        # Check for collision with food
        if x1 == foodx and y1 == foody:
            achievement_system.check_achievements(snake_length - 1, selected_map, not game_close)
            pygame.mixer.Sound.play(food_sound)
            foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
            snake_length += 1

            # Generate power-up on food consumption
            power_up_rect = generate_power_up()
            if power_up_rect:  # If power-up generated, store its creation time
                power_up_creation_time = time.time()

        # If the player has collected a power-up
        if power_up_rect and pygame.Rect(x1, y1, snake_block, snake_block).colliderect(power_up_rect):
            power_up_active = True
            power_up_timer = time.time()  # Start the power-up timer
            power_up_rect = None  # Remove the power-up after collection

        # If the power-up timer expires, deactivate the power-up
        if power_up_active and time.time() - power_up_timer > 5:  # Power-up lasts for 5 seconds
            power_up_active = False

        # If the power-up has not been collected and 5 seconds have passed, remove it
        if power_up_rect and time.time() - power_up_creation_time > 5:
            power_up_rect = None  # Remove the power-up if not collected

        clock.tick(snake_speed)

    pygame.quit()
    quit()

main_menu()
