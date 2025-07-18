import pygame
import sys
import random
import math
from moviepy.editor import VideoFileClip

# INITIALIZE PYGAME
pygame.init()

# SET UP THE SCREEN DIMENSIONS
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

# ADDING BACKGROUND
background = pygame.image.load('background_pink.png')

# TITLE AND ICON
pygame.display.set_caption("Bouncing Balls!!")
icon = pygame.image.load("cannon.png")
pygame.display.set_icon(icon)

# LOAD AND PLAY BACKGROUND MUSIC
pygame.mixer.music.load('background_music.mp3')
pygame.mixer.music.play(-1)  # -1 MEANS THE MUSIC WILL LOOP INDEFINITELY.
pygame.mixer.music.set_volume(0.5)

# LOAD CANON SOUND EFFECT
cannon_sound = pygame.mixer.Sound('canon_sound.wav')

# LOAD BUTTON CLICK SOUND
button_click_sound = pygame.mixer.Sound('buttonclick.mp3')

# DEFINE COLORS.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARKGREEN = (0, 100, 0)
MIDNIGHT_BLUE = (25, 25, 112)
LEMON_CHIFFON = (255, 250, 205)
GOLD = (255, 215, 0)

# BALL PROPERTIES
ball_radius = 20
num_balls_per_line = 20  # NUMBER OF BALLS PER LINE
num_lines = 4  # NUMBER OF LINES
ball_spacing = 40  # SPACING BETWEEN BALLS.
line_spacing = 0  # SPACING BETWEEN LINES.

# DEFINE FOUR COLORS.
colors = [RED, GREEN, BLUE, YELLOW]

# GENERATE COLORS FOR EACH LINE.
line_colors = [[random.choice(colors) for _ in range(num_balls_per_line)] for _ in range(num_lines)]

# DEFINE BALL PROPERTIES.
balls = []

def move_ball(ball):
    ball['x'] += ball['speed'] * math.cos(ball['direction'])
    ball['y'] += ball['speed'] * math.sin(ball['direction'])

def check_collision(ball):
    if ball['x'] + ball_radius >= screen_width or ball['x'] - ball_radius <= 0:
        ball['direction'] = math.pi - ball['direction']  # Reverse direction on collision with side walls
    if ball['y'] + ball_radius >= screen_height:
        ball['direction'] = -ball['direction']  # Reverse direction on collision with top or bottom walls

def check_cannon_collision(cannon_ball):
    for line_index, line in enumerate(line_colors):
        for ball_index, ball_color in enumerate(line):
            if ball_color:
                ball_x = ball_radius + ball_index * ball_spacing
                ball_y = ball_radius + line_index * (ball_radius * 2 + line_spacing)
                dist_squared = (cannon_ball['x'] - ball_x) ** 2 + (cannon_ball['y'] - ball_y) ** 2
                min_dist_squared = (ball_radius * 2) ** 2  # Minimum distance for collision
                if dist_squared <= min_dist_squared:
                    return (line_index, ball_index)
    return None

def attach_ball(cannon_ball, hit_ball_position):
    line_index, ball_index = hit_ball_position

    # Ensure no more than two new lines below the initial lines
    max_lines = num_lines + 6
    if line_index >= max_lines - 1:
        line_index = max_lines - 2

    if len(line_colors) <= line_index + 1:
        line_colors.append([None] * num_balls_per_line)
    
    if cannon_ball['color'] == line_colors[line_index][ball_index]:
        new_line_index = line_index + 1
    else:
        new_line_index = line_index + 1

    if new_line_index >= len(line_colors):
        line_colors.append([None] * num_balls_per_line)

    line_colors[new_line_index][ball_index] = cannon_ball['color']
    return (new_line_index, ball_index)

# Load pop music sound effect
pop_music = pygame.mixer.Sound('popsound2.mp3')

def remove_connected_balls(line_index, ball_index, color):
    to_remove = [(line_index, ball_index)]
    visited = set()
    while to_remove:
        li, bi = to_remove.pop()
        if (li, bi) in visited:
            continue
        visited.add((li, bi))
        neighbors = get_neighbors(li, bi)
        for n_li, n_bi in neighbors:
            if n_li >= 0 and n_li < len(line_colors) and n_bi >= 0 and n_bi < len(line_colors[n_li]):
                if line_colors[n_li][n_bi] == color:
                    to_remove.append((n_li, n_bi))

    if len(visited) >= 3:
        for li, bi in visited:
            line_colors[li][bi] = None
        num_removed = len(visited)  # Return the number of balls removed
        pop_music.play()
        return num_removed

    else:
        return 0

def get_neighbors(line_index, ball_index):
    neighbors = [
        (line_index, ball_index - 1),
        (line_index, ball_index + 1),
        (line_index - 1, ball_index),
        (line_index + 1, ball_index)
    ]
    return neighbors

def settle_balls():
    for line in line_colors:
        line[:] = [ball for ball in line if ball is not None]
    # Ensure all lines have the correct number of elements
    for line in line_colors:
        while len(line) < num_balls_per_line:
            line.append(None)

# Cannon
cannon_img = pygame.image.load('canon1_img.png')
cannonX = 360
cannonY = 500
cannon_rect = cannon_img.get_rect(center=(cannonX, cannonY))

def degrees_to_radians(degrees):
    return degrees * math.pi / 180

def get_cannon_mouth(center, length, angle):
    radians = degrees_to_radians(angle)
    x = center[0] + length * math.cos(radians)
    y = center[1] - length * math.sin(radians)
    return (x, y)

cannon_length = 64
cannon_angle = 90
cannon_rotation_speed = 5

# Current ball to be shot
current_ball_color = random.choice(colors)

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Define buttons
start_button = pygame.Rect(300, 300, 200, 50)
instructions_button = pygame.Rect(300, 400, 200, 50)
quit_button = pygame.Rect(300, 500, 200, 50)
game_over_button = pygame.Rect(300, 400, 200,50)
back_button = pygame.Rect(50, 520, 100, 50)  # Define the back button
restart_button = pygame.Rect(160, 520, 100, 50)  # Define the restart button
quit_game_button = pygame.Rect(screen_width - 280, 520, 100, 50)  # Define the quit game button

# Score
score = 0


# Counter for bottom line collisions
bottom_line_collisions = 0

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)
    return text_rect  # Return the rect for further use

# Load and prepare the menu screen video
menu_video = VideoFileClip('menu_screen.mp4')
menu_video = menu_video.resize((screen_width, screen_height))
start_time = pygame.time.get_ticks()

def show_menu():
    global start_time
    current_time = (pygame.time.get_ticks() - start_time) / 1000.0
    if current_time >= menu_video.duration:
        start_time = pygame.time.get_ticks()
        current_time = 0
    
    frame = menu_video.get_frame(current_time)
    frame_image = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")
    screen.blit(frame_image, (0, 0))

    pygame.draw.rect(screen, DARKGREEN, start_button)
    pygame.draw.rect(screen, DARKGREEN, instructions_button)
    pygame.draw.rect(screen, DARKGREEN, quit_button)
    pygame.draw.rect(screen, WHITE, start_button, 2)
    pygame.draw.rect(screen, WHITE, instructions_button, 2)
    pygame.draw.rect(screen, WHITE, quit_button, 2)
    draw_text('Start', font, WHITE, screen, start_button.centerx, start_button.centery)
    draw_text('Instructions', font, WHITE, screen, instructions_button.centerx, instructions_button.centery)
    draw_text('Quit', font, WHITE, screen, quit_button.centerx, quit_button.centery)
    pygame.display.flip()

instructions_screen = pygame.image.load('INSTRUCTIONS.png')
def show_instructions():
    screen.blit(instructions_screen, (0, 0))
    pygame.display.flip()

# Load game over music
gameover_music = pygame.mixer.Sound('gameover_music.wav')
gameover_screen = pygame.image.load('GAMEOVER.png')
def show_game_over():
    screen.blit(gameover_screen, (0, 0))
    draw_text(f'Your score: {score}', large_font, GOLD, screen, screen_width // 2, 350)
    pygame.draw.rect(screen, LEMON_CHIFFON, game_over_button)
    pygame.draw.rect(screen, WHITE, game_over_button, 2)
    draw_text('Return to Menu', font, MIDNIGHT_BLUE, screen, game_over_button.centerx, game_over_button.centery)
    pygame.display.flip()
    pygame.mixer.music.stop()
    gameover_music.play()

# Game state
state = "menu"
running = True
quit_prompt = False
restart_prompt = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if state == "menu":
                if start_button.collidepoint(mouse_pos):
                    button_click_sound.play()
                    state = "game_active"
                    bottom_line_collisions = 0
                    line_colors = [[random.choice(colors) for _ in range(num_balls_per_line)] for _ in range(num_lines)]
                    score = 0
                    balls.clear()
                elif instructions_button.collidepoint(mouse_pos):
                    button_click_sound.play()
                    state = "instructions"
                elif quit_button.collidepoint(mouse_pos):
                    button_click_sound.play()
                    running = False
            elif state == "game_over":
                if game_over_button.collidepoint(mouse_pos):
                    button_click_sound.play()
                    state = "menu"
                    pygame.mixer.music.play(-1)
            elif state == "game_active":
                if back_button.collidepoint(mouse_pos):
                    button_click_sound.play()
                    state = "menu"
                    pygame.mixer.music.play(-1)
                elif restart_button.collidepoint(mouse_pos):  # Check if the restart button is clicked
                    button_click_sound.play()
                    restart_prompt = True
                elif quit_game_button.collidepoint(mouse_pos):
                    button_click_sound.play()
                    quit_prompt = True
        if event.type == pygame.KEYDOWN:
            if state == "instructions":
                button_click_sound.play()
                state = "menu"
            if event.key == pygame.K_LEFT:
                cannon_angle += cannon_rotation_speed
                if cannon_angle > 160:
                    cannon_angle = 160
            if event.key == pygame.K_RIGHT:
                cannon_angle -= cannon_rotation_speed
                if cannon_angle < 20:
                    cannon_angle = 20
            if event.key == pygame.K_SPACE:
                cannon_sound.play()
                ballX, ballY = get_cannon_mouth(cannon_rect.center, cannon_length, cannon_angle)
                speed = 8
                direction = degrees_to_radians(cannon_angle)
                new_ball = {'x': ballX - 15, 'y': ballY, 'speed': speed, 'direction': direction, 'color': current_ball_color}
                balls.append(new_ball)
                current_ball_color = random.choice(colors)

    if state == "menu":
        show_menu()
    elif state == "instructions":
        show_instructions()
    elif state == "game_over":
        show_game_over()
    elif state == "game_active":
        screen.fill(BLACK)
        screen.blit(background, (0, 0))  # Adding background

        for line_index, line in enumerate(line_colors):
            for ball_index, ball_color in enumerate(line):
                if ball_color:
                    ball_x = ball_radius + ball_index * ball_spacing
                    ball_y = ball_radius + line_index * (ball_radius * 2 + line_spacing)
                    pygame.draw.circle(screen, ball_color, (ball_x, ball_y), ball_radius)

        for ball in balls:
            move_ball(ball)
            check_collision(ball)
            pygame.draw.circle(screen, ball['color'], (int(ball['x']), int(ball['y'])), ball_radius)

            collision = check_cannon_collision(ball)
            if collision:
                line_index, ball_index = collision
                attach_result = attach_ball(ball, collision)
                balls.remove(ball)
                num_removed = remove_connected_balls(attach_result[0], attach_result[1], ball['color'])
                score += num_removed

                if line_index >= 9:
                    bottom_line_collisions += 1
                    if bottom_line_collisions >= 1:
                        state = "game_over"

                break

        ballX, ballY = get_cannon_mouth(cannon_rect.center, cannon_length, cannon_angle)
        pygame.draw.circle(screen, current_ball_color, (int(ballX - 10), int(ballY)), ball_radius)

        rotated_cannon = pygame.transform.rotate(cannon_img, cannon_angle)
        rotated_cannon_rect = rotated_cannon.get_rect(center=cannon_rect.center)
        screen.blit(rotated_cannon, rotated_cannon_rect)

        ballX, ballY = get_cannon_mouth(rotated_cannon_rect.center, cannon_length, cannon_angle)
        pygame.draw.circle(screen, current_ball_color, (int(ballX - 10), int(ballY)), ball_radius)

        score_text = f'Score: {score}'
        score_text_surface = font.render(score_text, True, MIDNIGHT_BLUE)
        score_rect = score_text_surface.get_rect(center=(screen_width - 100, 550))
        padded_score_rect = score_rect.inflate(20, 20)
        pygame.draw.rect(screen, LEMON_CHIFFON, padded_score_rect)
        pygame.draw.rect(screen, WHITE, padded_score_rect, 2)
        screen.blit(score_text_surface, score_rect)

        pygame.draw.rect(screen, LEMON_CHIFFON, back_button)
        pygame.draw.rect(screen, WHITE, back_button, 2)
        draw_text('Home', font, MIDNIGHT_BLUE, screen, back_button.centerx, back_button.centery)

        pygame.draw.rect(screen, LEMON_CHIFFON, restart_button)  # Draw the restart button
        pygame.draw.rect(screen, WHITE, restart_button, 2)
        draw_text('Restart', font, MIDNIGHT_BLUE, screen, restart_button.centerx, restart_button.centery)

        pygame.draw.rect(screen, LEMON_CHIFFON, quit_game_button)  # Draw the quit game button
        pygame.draw.rect(screen, WHITE, quit_game_button, 2)
        draw_text('Quit', font, MIDNIGHT_BLUE, screen, quit_game_button.centerx, quit_game_button.centery)

        if quit_prompt:
            prompt_rect = pygame.Rect(200, 200, 400, 200)
            pygame.draw.rect(screen, WHITE, prompt_rect)
            pygame.draw.rect(screen, MIDNIGHT_BLUE, prompt_rect, 5)
            draw_text('Do you want to quit the game?', font, MIDNIGHT_BLUE, screen, prompt_rect.centerx, prompt_rect.centery - 40)
            yes_button = draw_text('Yes', font, MIDNIGHT_BLUE, screen, prompt_rect.centerx - 50, prompt_rect.centery + 40)
            no_button = draw_text('No', font, MIDNIGHT_BLUE, screen, prompt_rect.centerx + 50, prompt_rect.centery + 40)
            if yes_button.collidepoint(mouse_pos):
                running = False
            elif no_button.collidepoint(mouse_pos):
                quit_prompt = False

        if restart_prompt:
            prompt_rect = pygame.Rect(200, 200, 400, 200)
            pygame.draw.rect(screen, WHITE, prompt_rect)
            pygame.draw.rect(screen, MIDNIGHT_BLUE, prompt_rect, 5)
            draw_text('Do you want to restart the game?', font, MIDNIGHT_BLUE, screen, prompt_rect.centerx, prompt_rect.centery - 40)
            yes_button = draw_text('Yes', font, MIDNIGHT_BLUE, screen, prompt_rect.centerx - 50, prompt_rect.centery + 40)
            no_button = draw_text('No', font, MIDNIGHT_BLUE, screen, prompt_rect.centerx + 50, prompt_rect.centery + 40)
            if yes_button.collidepoint(mouse_pos):
                bottom_line_collisions = 0
                line_colors = [[random.choice(colors) for _ in range(num_balls_per_line)] for _ in range(num_lines)]
                score = 0
                balls.clear()
                restart_prompt = False
            elif no_button.collidepoint(mouse_pos):
                restart_prompt = False

    pygame.display.flip()

pygame.quit()
sys.exit()
