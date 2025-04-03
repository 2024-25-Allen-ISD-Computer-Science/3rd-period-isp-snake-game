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
purple = (128, 0, 128)

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
invincibility_sound = pygame.mixer.Sound("invincibility.mp3")  # SFX for invincibility power-up
speed_boost_sound = pygame.mixer.Sound("speed_boost.mp3")  # SFX for speed boost power-up
power_down_sound = pygame.mixer.Sound("power_down.mp3")  # Power-up expiration sound
achievement_sound = pygame.mixer.Sound("achievement.mp3")  # Achievement unlocked sound
menu_click_sound = pygame.mixer.Sound("menu_click.mp3")  # Menu click sound
pygame.mixer.music.load(background_music)
pygame.mixer.music.set_volume(0.5)  # Decrease volume to 50%
pygame.mixer.music.play(-1)  # Loop the background music

# Volume settings
master_volume = 0.5
music_volume = 0.5
sfx_volume = 0.5

# Power-up variables
power_up_active = False  # Tracks if any power-up is active
power_up_type = None  # Tracks the type of power-up (None, "invincibility", or "speed_boost")
power_up_timer = 0  # Timer for the active power-up
power_up_rect = None  # Rectangle for the power-up on the screen
power_up_creation_time = 0  # Timestamp when the power-up is created

# Purple balls variables
purple_balls = []
purple_ball_radius = 15
purple_ball_speed = 2

def initialize_purple_balls():
    global purple_balls
    purple_balls = []
    spacing = height // 5  # Equal spacing between balls
    for i in range(1, 5):  # Create 4 balls
        purple_balls.append({
            'x': 0,
            'y': spacing * i,
            'direction': 1,  # 1 for right, -1 for left
            'radius': purple_ball_radius
        })

def update_purple_balls():
    for ball in purple_balls:
        ball['x'] += purple_ball_speed * ball['direction']
        # Reverse direction if hitting boundaries
        if ball['x'] <= ball['radius']:
            ball['x'] = ball['radius']  # Prevent getting stuck at edge
            ball['direction'] = 1  # Force move right
        elif ball['x'] >= width - ball['radius']:
            ball['x'] = width - ball['radius']  # Prevent getting stuck at edge
            ball['direction'] = -1  # Force move left

def draw_purple_balls():
    for ball in purple_balls:
        pygame.draw.circle(display, purple, (int(ball['x']), int(ball['y'])), ball['radius'])
        # Add a highlight to make them look more ball-like
        pygame.draw.circle(display, (178, 102, 255), (int(ball['x'] - ball['radius']/3), int(ball['y'] - ball['radius']/3)), ball['radius']//4)

def check_purple_ball_collision(x, y):
    for ball in purple_balls:
        distance = math.sqrt((x - ball['x'])**2 + (y - ball['y'])**2)
        if distance <= ball['radius'] + snake_block/2:
            return True
    return False


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
            pygame.draw.polygon(display, forest_green, [(x, y + snake_block), (x + snake_block, y + snake_block), (x + snake_block // 2, y)])
            eye_radius = snake_block // 5
            pygame.draw.circle(display, black, (center_x - 3, center_y - 3), eye_radius)
            pygame.draw.circle(display, black, (center_x + 3, center_y - 3), eye_radius)
            pygame.draw.line(display, red, (center_x, center_y + 3), (center_x, center_y + 8), 2)  # Tongue
        else:  # Body with scales
            if power_up_active and power_up_type == "speed_boost":
                flash_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
                pygame.draw.ellipse(display, flash_color, [x + 1, y + 1, snake_block - 2, snake_block - 2])
            else:
                pygame.draw.ellipse(display, forest_green, [x + 1, y + 1, snake_block - 2, snake_block - 2])
                for j in range(0, snake_block, 4):  # Adding scales
                    pygame.draw.arc(display, dark_gray, [x + j, y, 4, snake_block], 0, math.pi, 1)
        
        if i == len(snake_list) - 1:  # Tail Tapering
            if power_up_active and power_up_type == "speed_boost":
                flash_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
                pygame.draw.ellipse(display, flash_color, [x + 3, y + 3, snake_block - 4, snake_block - 4])
            else:
                pygame.draw.ellipse(display, forest_green, [x + 3, y + 3, snake_block - 4, snake_block - 4])

def draw_food(x, y):
    boundary_x_min = 100  
    boundary_x_max = width - 100 
    boundary_y_min = 100  
    boundary_y_max = height - 100  
    
    
    x = max(min(x, boundary_x_max), boundary_x_min)
    y = max(min(y, boundary_y_max), boundary_y_min)
    
    pygame.draw.ellipse(display, (0, 0, 0), [x - 5, y + 10, 20, 5])  # Shadow
    pygame.draw.circle(display, red, (x, y), 10)  # Apple
    pygame.draw.ellipse(display, white, [x + 2, y - 4, 4, 2])  # Highlight on the apple

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
    "green": {"background": light_green, "obstacles": []},  # Will be populated randomly
    "dark": {"background": dark_gray, "obstacles": []}  # Will be populated randomly
}

def generate_random_obstacles(map_type):
    obstacles = []
    if map_type == "green":
        # Generate 2-4 random obstacles for green map
        num_obstacles = random.randint(2, 4)
        for _ in range(num_obstacles):
            # Randomly choose between horizontal or vertical obstacle
            if random.random() < 0.5:  # 50% chance for horizontal
                length = random.randint(100, 300)  # Random length between 100-300
                thickness = random.randint(5, 15)   # Random thickness between 5-15
                x = random.randint(50, width - length - 50)
                y = random.randint(50, height - thickness - 50)
                obstacles.append(pygame.Rect(x, y, length, thickness))
            else:  # Vertical obstacle
                length = random.randint(50, 200)    # Random length between 50-200
                thickness = random.randint(5, 15)   # Random thickness between 5-15
                x = random.randint(50, width - thickness - 50)
                y = random.randint(50, height - length - 50)
                obstacles.append(pygame.Rect(x, y, thickness, length))
                
    elif map_type == "dark":
        # Generate 3-5 random obstacles for dark map
        num_obstacles = random.randint(3, 5)
        for _ in range(num_obstacles):
            # 70% chance for horizontal, 30% for vertical
            if random.random() < 0.7:  # Horizontal obstacle
                length = random.randint(200, 400)  # Longer obstacles for dark map
                thickness = random.randint(5, 10)
                x = random.randint(20, width - length - 20)
                y = random.randint(20, height - thickness - 20)
                obstacles.append(pygame.Rect(x, y, length, thickness))
            else:  # Vertical obstacle
                length = random.randint(100, 300)
                thickness = random.randint(5, 10)
                x = random.randint(20, width - thickness - 20)
                y = random.randint(20, height - length - 20)
                obstacles.append(pygame.Rect(x, y, thickness, length))
                
    return obstacles

def draw_slider(label, x, y, value):
    pygame.draw.rect(display, white, [x, y, 200, 10])
    pygame.draw.rect(display, green, [x, y, int(value * 200), 10])
    text = font_style.render(label, True, white)
    display.blit(text, (x, y - 30))

def draw_home_icon():
    home_icon = pygame.Rect(10, 10, 40, 40)
    pygame.draw.rect(display, white, home_icon, border_radius=10)
    text = font_style.render("🏠", True, black)
    display.blit(text, (20, 15))
    return home_icon

def options_menu():
    global master_volume, music_volume, sfx_volume
    options_active = True
    while options_active:
        display.fill(black)
        display_message("Options", yellow, y_offset=-120, x_offset=width // 3, underline=True)
        home_icon = draw_home_icon()
        draw_slider("Master Volume", 200, 100, master_volume)
        draw_slider("Music Volume", 200, 150, music_volume)
        draw_slider("SFX Volume", 200, 200, sfx_volume)
        display_message("Press ESC to return to the main menu", white, y_offset=200, x_offset=100)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    options_active = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if home_icon.collidepoint(pygame.mouse.get_pos()):
                    options_active = False
                        
def upcoming_updates_screen():
    display.fill(black)
    display_message("Upcoming Updates", yellow, y_offset=-120, x_offset=width // 3, underline=True)
    home_icon = draw_home_icon()
    display_message("- New maps coming soon!", white, y_offset=-50, x_offset=50)
    display_message("- New power-ups coming soon!", white, y_offset=0, x_offset=50)
    display_message("Press ESC to return to the main menu.", white, y_offset=200, x_offset=50)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if home_icon.collidepoint(pygame.mouse.get_pos()):
                    waiting = False
                    
# Function to show "How to Play" instructions
def how_to_play_screen():
    display.fill(black)
    display_message("How to Play", yellow, y_offset=-120, x_offset=width // 3, underline=True)
    home_icon = draw_home_icon()
    display_message("Use WASD or Arrow Keys to move the snake.", white, y_offset=-50, x_offset=50)
    display_message("Press ESC to return to the main menu.", white, y_offset=200, x_offset=50)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if home_icon.collidepoint(pygame.mouse.get_pos()):
                    waiting = False

def cosmetic_shop_screen():
    shop_active = True
    selected_skin = None
    skins = ["Classic", "Neon", "Retro", "Ghost"]  # List of available skins
    skin_prices = {
        "Classic": 20,  # Price for Classic skin
        "Neon": 50,     # Price for Neon skin
        "Retro": 100,   # Price for Retro skin
        "Ghost": 200    # Price for Ghost skin
    }
    
    while shop_active:
        display.fill(blue)
        display_message("Cosmetic Shop", white, y_offset=-90, x_offset=200, underline=True)
        
        for index, skin in enumerate(skins):
            price = skin_prices[skin]  # Get the price of the skin
            display_message(f"{index + 1}. {skin} Skin - {price} Shop Points", white, y_offset=-40 + (index * 50), x_offset=200)
        
        display_message("Press ESC to return to the main menu", white, y_offset=200, x_offset=100)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    shop_active = False
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    selected_skin = skins[event.key - pygame.K_1]
                    print(f"Selected Skin: {selected_skin} - Price: {skin_prices[selected_skin]} Shop Points")  # Debugging output
                
def main_menu():
    menu_active = True
    selected_map = None
    high_score = 0
    button_color = (50, 150, 255)
    button_hover_color = (30, 100, 200)
    text_color = white
    button_width = 250
    button_height = 50
    button_x = (width - button_width) // 2 
    button_y_start = 120  
    button_spacing = 60 

    menu_options = [
        ("Blue Map", "blue", -15, -35),
        ("Green Map", "green", -15, -30),
        ("Dark Map", "dark", -15, -25),
        ("Options", "options",-15, -20),
        ("How to Play", "how_to_play", -15, -15),
        ("Upcoming Updates", "updates", -15, -10),
        ("Cosmetic Shop", "shop", -15, -5),
        ("Exit", "exit", -15, 0)
    ]

    while menu_active:
        display.fill(black)  
        display_message("Welcome to Snake Game!", yellow, y_offset=-120, x_offset=width // 4, underline=True)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        buttons = []

        for i, (label, action, x_offset, y_offset) in enumerate(menu_options):
            btn_rect = pygame.Rect(button_x + x_offset, button_y_start + i * button_spacing + y_offset, button_width, button_height)
            buttons.append((btn_rect, action))

            color = button_hover_color if btn_rect.collidepoint(mouse_x, mouse_y) else button_color
            pygame.draw.rect(display, color, btn_rect, border_radius=10)
            pygame.draw.rect(display, white, btn_rect, 2, border_radius=10) 

            text_surface = font_style.render(label, True, text_color)
            text_x = btn_rect.centerx - text_surface.get_width() // 2
            text_y = btn_rect.centery - text_surface.get_height() // 2
            display.blit(text_surface, (text_x, text_y))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                for btn_rect, action in buttons:
                    if btn_rect.collidepoint(mouse_x, mouse_y):
                        if action == "exit":
                            pygame.quit()
                            quit()
                        elif action == "options":
                            options_menu()
                        elif action == "how_to_play":
                            how_to_play_screen()
                        elif action == "updates":
                            upcoming_updates_screen()
                        elif action == "shop":
                            cosmetic_shop_screen()
                        else:
                            selected_map = action
                            menu_active = False

    game_loop(selected_map, high_score)

# Function to draw the power-up
def draw_power_up(power_up_rect, power_up_type):
    # Boundary for power-up spawn (similar to the apple boundary)
    boundary_x_min = 100
    boundary_x_max = width - 100
    boundary_y_min = 100
    boundary_y_max = height - 100

    # Adjust the power-up's position if it's outside the defined boundaries
    power_up_rect.x = max(min(power_up_rect.x, boundary_x_max - power_up_rect.width), boundary_x_min)
    power_up_rect.y = max(min(power_up_rect.y, boundary_y_max - power_up_rect.height), boundary_y_min)

    if power_up_type == "invincibility":
        # Draw heart for invincibility
        pygame.draw.circle(display, (255, 0, 0), (power_up_rect.x - 15, power_up_rect.y), 15)
        pygame.draw.circle(display, (255, 0, 0), (power_up_rect.x + 15, power_up_rect.y), 15)
        pygame.draw.polygon(display, (255, 0, 0), [(power_up_rect.x - 30, power_up_rect.y), (power_up_rect.x + 30, power_up_rect.y), (power_up_rect.x, power_up_rect.y + 30)])
    elif power_up_type == "speed_boost":
        # Draw fast-forward symbol for speed boost
        pygame.draw.polygon(display, green, [
            (power_up_rect.x + power_up_rect.width * 0.2, power_up_rect.y + power_up_rect.height * 0.2),
            (power_up_rect.x + power_up_rect.width * 0.8, power_up_rect.y + power_up_rect.height * 0.5),
            (power_up_rect.x + power_up_rect.width * 0.2, power_up_rect.y + power_up_rect.height * 0.8),
        ])
        pygame.draw.polygon(display, green, [
            (power_up_rect.x + power_up_rect.width * 0.5, power_up_rect.y + power_up_rect.height * 0.2),
            (power_up_rect.x + power_up_rect.width * 0.8, power_up_rect.y + power_up_rect.height * 0.5),
            (power_up_rect.x + power_up_rect.width * 0.5, power_up_rect.y + power_up_rect.height * 0.8),
        ])

# Function to generate a random power-up
def generate_power_up():
    if random.random() < 1/3:  # 1/3 chance of power-up generation
        power_up_x = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
        power_up_y = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
        power_up_type = random.choice(["invincibility", "speed_boost"])  # Randomly choose power-up type
        return pygame.Rect(power_up_x, power_up_y, snake_block * 4, snake_block * 4), power_up_type
    return None, None

# Function to draw the snake with invincibility when power-up is active
def draw_invincible_snake(snake_block, snake_list):
    for i, segment in enumerate(reversed(snake_list)):
        x, y = segment
        center_x, center_y = x + snake_block // 2, y + snake_block // 2
        
        if i == 0:  # Head
            pygame.draw.polygon(display, red, [(x, y + snake_block), (x + snake_block, y + snake_block), (x + snake_block // 2, y)])
            eye_radius = snake_block // 5
            pygame.draw.circle(display, black, (center_x - 3, center_y - 3), eye_radius)
            pygame.draw.circle(display, black, (center_x + 3, center_y - 3), eye_radius)
            pygame.draw.line(display, red, (center_x, center_y + 3), (center_x, center_y + 8), 2)  # Tongue
        else:  # Body with scales
            if power_up_active and power_up_type == "speed_boost":
                flash_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
                pygame.draw.ellipse(display, flash_color, [x + 1, y + 1, snake_block - 2, snake_block - 2])
            else:
                pygame.draw.ellipse(display, red, [x + 1, y + 1, snake_block - 2, snake_block - 2])
                for j in range(0, snake_block, 4):  # Adding scales
                    pygame.draw.arc(display, dark_gray, [x + j, y, 4, snake_block], 0, math.pi, 1)
        
        if i == len(snake_list) - 1:  # Tail Tapering
            if power_up_active and power_up_type == "speed_boost":
                flash_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
                pygame.draw.ellipse(display, flash_color, [x + 3, y + 3, snake_block - 4, snake_block - 4])
            else:
                pygame.draw.ellipse(display, forest_green, [x + 3, y + 3, snake_block - 4, snake_block - 4])

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
            pygame.mixer.Sound.play(achievement_sound)
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
    global power_up_active, power_up_type, power_up_timer, power_up_rect, power_up_creation_time, snake_speed 
    game_over = False
    game_close = False
    score = 0

     # Initialize purple balls if dark map
    if selected_map == "dark":
        initialize_purple_balls()

    # Store the original snake speed
    original_snake_speed = snake_speed

    map_details = maps[selected_map]
    background_color = map_details["background"]
    
    # Generate random obstacles for the selected map
    obstacles = generate_random_obstacles(selected_map)
    
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
            button_color = (50, 150, 255)
            button_hover_color = (30, 100, 200)
            button_width = 250
            button_height = 50
            button_x = (width - button_width) // 2
            button_y_end = 120
            text_color = white
            
            # Position of the "Back to Main Menu" button
            button_y = button_y_end + (button_height + 10)  
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            btn_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # Change button color when hovering
            color = button_hover_color if btn_rect.collidepoint(mouse_x, mouse_y) else button_color
            pygame.draw.rect(display, color, btn_rect, border_radius=10)
            pygame.draw.rect(display, white, btn_rect, 2, border_radius=10)

            # Display button text
            text_surface = font_style.render("Back to Main Menu", True, text_color)
            text_x = btn_rect.centerx - text_surface.get_width() // 2
            text_y = btn_rect.centery - text_surface.get_height() // 2
            display.blit(text_surface, (text_x, text_y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()  # Quit the game entirely if the window is closed
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:  # Quit the game entirely
                        pygame.quit()
                        quit()
                    elif event.key == pygame.K_c:  # Restart the game
                        game_loop(selected_map, high_score)  # Restart the game (recursive call)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_rect.collidepoint(mouse_x, mouse_y):
                        pygame.mixer.Sound.play(menu_click_sound)
                        main_menu()  # Go back to the main menu when clicked

            pygame.display.update()



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

        # Update and draw purple balls if dark map
        if selected_map == "dark":
            update_purple_balls()
            draw_purple_balls()
            # Check collision with purple balls
            if check_purple_ball_collision(x1, y1) and (not power_up_active or power_up_type != "invincibility"):
                pygame.mixer.Sound.play(collision_sound)
                game_close = True

        draw_food(foodx, foody)

        # Draw the power-up if it exists
        if power_up_rect:
            draw_power_up(power_up_rect, power_up_type)

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
                if not power_up_active or power_up_type != "invincibility":  # Only collide if not invincible
                    pygame.mixer.Sound.play(collision_sound)
                    game_close = True

        # Draw the snake with the invincibile effect when power-up is active
        if power_up_active and power_up_type == "invincibility":
            draw_invincible_snake(snake_block, snake_list)
        else:
            draw_snake(snake_block, snake_list)

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
            power_up_rect, power_up_type = generate_power_up()
            if power_up_rect:  # If power-up generated, store its creation time
                power_up_creation_time = time.time()

        # If the player has collected a power-up
        if power_up_rect and pygame.Rect(x1, y1, snake_block, snake_block).colliderect(power_up_rect):
            power_up_active = True
            power_up_timer = time.time()  # Start the power-up timer
            if power_up_type == "speed_boost":
                pygame.mixer.Sound.play(speed_boost_sound)
                snake_speed = int(snake_speed * 1.75)  # Increase speed by 75%
            elif power_up_type == "invincibility":
                pygame.mixer.Sound.play(invincibility_sound)
            power_up_rect = None  # Remove the power-up after collection

        # If the power-up timer expires, deactivate the power-up
        if power_up_active and time.time() - power_up_timer > 5:  # Power-up lasts for 5 seconds
            pygame.mixer.Sound.play(power_down_sound)
            power_up_active = False
            if power_up_type == "speed_boost":
                
                snake_speed = original_snake_speed  # Reset to original speed
            power_up_type = None  # Reset power-up type

        # If the power-up has not been collected and 5 seconds have passed, remove it
        if power_up_rect and time.time() - power_up_creation_time > 5:
            power_up_rect = None  # Remove the power-up if not collected

        clock.tick(snake_speed)

    pygame.quit()
    quit()

main_menu()
