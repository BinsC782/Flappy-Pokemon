import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

PIXEL_SIZE = 2
pixel_surfaces = {}
pygame.display.set_caption("Flappy Pokémon")

def load_pixel_art(path, scale_factor=PIXEL_SIZE):
    surf = pygame.image.load(path)
    surf = surf.convert_alpha()
    w, h = surf.get_size()
    target_w = max(1, w // scale_factor)
    target_h = max(1, h // scale_factor)
    surf = pygame.transform.smoothscale(surf, (target_w, target_h))
    surf = pygame.transform.scale(surf, (w, h))
    return surf

bg = pygame.image.load("Images/background.png")
bg = pygame.transform.smoothscale(bg, (WIDTH, HEIGHT))

pokemon_glide = load_pixel_art("Images/Main Character #1.png", 1)
pokemon_glide = pygame.transform.smoothscale(pokemon_glide, (64, 64))

pokemon_flap = load_pixel_art("Images/Main Character #2.png", 1)
pokemon_flap = pygame.transform.smoothscale(pokemon_flap, (64, 64))

pipe_img = load_pixel_art("Images/Pillar.png", 1)
orig_w, orig_h = pipe_img.get_size()
pipe_width = 250
pipe_img = pygame.transform.smoothscale(pipe_img, (pipe_width, 400))

start_screen_bg = pygame.image.load("Images/Start Screen.jpg")
start_screen_bg = pygame.transform.smoothscale(start_screen_bg, (WIDTH, HEIGHT))

border_img = pygame.image.load("Images/border.jpg")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_GREEN = (0, 255, 100)
NEON_BLUE = (0, 150, 255)
NEON_PURPLE = (180, 0, 255)
NEON_PINK = (255, 0, 150)
CYAN = (0, 255, 255)
NEON_CYAN = CYAN
YELLOW = (255, 255, 0)

try:
    title_font = pygame.font.Font("Images/pixel_font.ttf", 64)
    font = pygame.font.Font("Images/pixel_font.ttf", 32)
    small_font = pygame.font.Font("Images/pixel_font.ttf", 20)
except:
    title_font = pygame.font.SysFont("Courier New", 64, bold=True)
    font = pygame.font.SysFont("Courier New", 32, bold=True)
    small_font = pygame.font.SysFont("Courier New", 20, bold=True)

player_x = 80
player_y = 300
velocity = 0
gravity = 0.5
jump = -8

pipe_list = []
gap = 170
pipe_speed = 3

score = 0
high_score = 0

in_start_screen = True
high_score_file = "highscore.txt"

if os.path.exists(high_score_file):
    with open(high_score_file, "r") as f:
        high_score = int(f.read())

def create_pipe():
    r = random.random()
    if r < 0.3:
        gap = 140
        height = random.randint(220, 300)
    elif r < 0.6:
        gap = 200
        height = random.randint(180, 320)
    else:
        gap = 260
        height = random.randint(150, 350)
    
    top = height - 400
    bottom = height + gap
    return {"x": WIDTH, "top": top, "bottom": bottom, "scored": False}

def draw_pipes(pipes):
    for p in pipes:
        top_x = p["x"]
        top_y = p["top"]
        screen.blit(pipe_img, (top_x, top_y))
        flipped = pygame.transform.flip(pipe_img, False, True)
        bot_x = p["x"]
        bot_y = p["bottom"]
        screen.blit(flipped, (bot_x, bot_y))

def move_pipes(pipes):
    for p in pipes:
        p["x"] -= pipe_speed
    return [p for p in pipes if p["x"] > -pipe_width]

def check_collision(pipes):
    global player_y
    player_rect = pygame.Rect(player_x + 10, player_y + 10, 44, 44)

    for p in pipes:
        pillar_visible_x = p["x"] + 97
        pillar_visible_w = 56
        
        top_rect = pygame.Rect(pillar_visible_x, p["top"], pillar_visible_w, 400)
        bottom_rect = pygame.Rect(pillar_visible_x, p["bottom"], pillar_visible_w, 400)

        if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
            return True

    if player_y <= -10 or player_y >= HEIGHT - 10:
        return True

    return False

def save_highscore():
    with open(high_score_file, "w") as f:
        f.write(str(high_score))

def draw_start_screen():
    screen.blit(start_screen_bg, (0, 0))
    
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(screen, (0, 0, 0, 30), (0, y), (WIDTH, y), 1)
    
    CYAN = (0, 255, 255)
    
    border_rect = pygame.Rect(20, 20, WIDTH - 40, HEIGHT - 40)
    pygame.draw.rect(screen, NEON_CYAN, border_rect, 3, border_radius=20)
    pygame.draw.rect(screen, NEON_PINK, border_rect.inflate(-10, -10), 2, border_radius=15)
    
    title_text = "FLAPPY POKÉMON"
    for offset in range(3, 0, -1):
        glow = title_font.render(title_text, True, (0, 50 + offset * 30, 100))
        screen.blit(glow, (WIDTH // 2 - title_font.size(title_text)[0] // 2 + offset, 80 + offset))
    title = title_font.render(title_text, True, CYAN)
    screen.blit(title, (WIDTH // 2 - title_font.size(title_text)[0] // 2, 80))
    
    pygame.draw.line(screen, NEON_GREEN, (WIDTH // 2 - 200, 170), (WIDTH // 2 + 200, 170), 3)
    
    sb_x, sb_y = WIDTH // 2 - 170, 190
    sb_w, sb_h = 340, 180
    sb_border = pygame.transform.smoothscale(border_img, (sb_w, sb_h))
    screen.blit(sb_border, (sb_x, sb_y))
    
    sb_title = small_font.render("  SCORE BOARD  ", True, BLACK)
    screen.blit(sb_title, (sb_x + sb_w // 2 - sb_title.get_width() // 2, sb_y + 12))
    
    last_score_text = font.render(f"Last: {last_score}", True, BLACK)
    best_score_text = font.render(f"Best: {high_score}", True, BLACK)
    screen.blit(last_score_text, (sb_x + sb_w // 2 - last_score_text.get_width() // 2 + 1, sb_y + 50 + 1))
    screen.blit(last_score_text, (sb_x + sb_w // 2 - last_score_text.get_width() // 2, sb_y + 50))
    screen.blit(best_score_text, (sb_x + sb_w // 2 - best_score_text.get_width() // 2 + 1, sb_y + 90 + 1))
    screen.blit(best_score_text, (sb_x + sb_w // 2 - best_score_text.get_width() // 2, sb_y + 90))
    
    btn_x, btn_y = WIDTH // 2 - 120, 360
    pygame.draw.rect(screen, NEON_GREEN, (btn_x, btn_y, 240, 70), border_radius=15)
    pygame.draw.rect(screen, WHITE, (btn_x, btn_y, 240, 70), 4, border_radius=15)
    pygame.draw.rect(screen, NEON_GREEN, (btn_x - 5, btn_y - 5, 250, 80), 3, border_radius=18)
    play_text = title_font.render("PLAY", True, BLACK)
    screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, btn_y))
    
    creators = small_font.render("CREATOR: RHEDZ MIRAS", True, BLACK)
    c_w, c_h = creators.get_width() + 20, creators.get_height() + 12
    c_x, c_y = WIDTH // 2 - c_w // 2, 500 - c_h // 2
    pygame.draw.rect(screen, CYAN, (c_x, c_y, c_w, c_h), border_radius=10)
    pygame.draw.rect(screen, BLACK, (c_x, c_y, c_w, c_h), 3, border_radius=10)
    screen.blit(creators, (WIDTH // 2 - creators.get_width() // 2, 500 - creators.get_height() // 2))
    
    corner_size = 30
    pygame.draw.line(screen, NEON_GREEN, (30, 40), (30 + corner_size, 40), 3)
    pygame.draw.line(screen, NEON_GREEN, (30, 40), (30, 40 + corner_size), 3)
    pygame.draw.line(screen, NEON_PINK, (WIDTH - 30, 40), (WIDTH - 30 - corner_size, 40), 3)
    pygame.draw.line(screen, NEON_PINK, (WIDTH - 30, 40), (WIDTH - 30, 40 + corner_size), 3)
    pygame.draw.line(screen, NEON_PINK, (30, HEIGHT - 40), (30 + corner_size, HEIGHT - 40), 3)
    pygame.draw.line(screen, NEON_PINK, (30, HEIGHT - 40), (30, HEIGHT - 40 - corner_size), 3)
    pygame.draw.line(screen, NEON_GREEN, (WIDTH - 30, HEIGHT - 40), (WIDTH - 30 - corner_size, HEIGHT - 40), 3)
    pygame.draw.line(screen, NEON_GREEN, (WIDTH - 30, HEIGHT - 40), (WIDTH - 30, HEIGHT - 40 - corner_size), 3)
    
    inst_text = "PRESS [SPACE] OR [CLICK] TO START"
    inst = small_font.render(inst_text, True, BLACK)
    i_w, i_h = inst.get_width() + 30, inst.get_height() + 12
    i_x, i_y = WIDTH // 2 - i_w // 2, 550 - i_h // 2
    pygame.draw.rect(screen, NEON_BLUE, (i_x, i_y, i_w, i_h), border_radius=15)
    pygame.draw.rect(screen, BLACK, (i_x, i_y, i_w, i_h), 3, border_radius=15)
    screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, 550 - inst.get_height() // 2 + 2))

clock = pygame.time.Clock()
running = True
game_over = False
spawn_time = 0
last_score = 0

while running:
    clock.tick(60)

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_ESCAPE] and game_over:
        in_start_screen = True
        last_score = score

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_highscore()
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if in_start_screen:
                    in_start_screen = False
                    game_over = False
                    player_y = 300
                    velocity = 0
                    pipe_list.clear()
                    score = 0
                    spawn_time = 0
                elif not game_over:
                    velocity = jump
            
            if event.key == pygame.K_r and game_over:
                player_y = 300
                velocity = 0
                pipe_list.clear()
                score = 0
                game_over = False
                in_start_screen = True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_start_screen:
                in_start_screen = False
                game_over = False
                player_y = 300
                velocity = 0
                pipe_list.clear()
                score = 0
                spawn_time = 0
            elif not game_over:
                velocity = jump

    if in_start_screen:
        draw_start_screen()
        pygame.display.update()
        continue

    if not game_over:
        velocity += gravity
        player_y += velocity

        spawn_time += 1
        if spawn_time > 100:
            pipe_list.append(create_pipe())
            spawn_time = 0

        pipe_list = move_pipes(pipe_list)

        for p in pipe_list:
            if not p.get("scored", False) and p["x"] + pipe_width < player_x:
                score += 1
                p["scored"] = True

        if check_collision(pipe_list):
            game_over = True
            last_score = score
            if score > high_score:
                high_score = score
                save_highscore()

    for y in range(0, HEIGHT, 4):
        pygame.draw.line(screen, (0, 0, 0, 30), (0, y), (WIDTH, y), 1)
    
    screen.blit(bg, (0, 0))
    draw_pipes(pipe_list)
    
    if not game_over:
        if velocity < -2:
            screen.blit(pokemon_flap, (player_x, player_y))
        else:
            screen.blit(pokemon_glide, (player_x, player_y))
    else:
        screen.blit(pokemon_glide, (player_x, player_y))

    ib_x, ib_y = 10, 0
    ib_w, ib_h = 250, 200
    in_game_border = pygame.transform.smoothscale(border_img, (ib_w, ib_h))
    screen.blit(in_game_border, (ib_x, ib_y))
    
    score_text = font.render(f"{score}", True, BLACK)
    high_text = font.render(f"HI: {high_score}", True, BLACK)
    screen.blit(score_text, (ib_x + ib_w // 2 - score_text.get_width() // 2, ib_y + 60))
    screen.blit(high_text, (ib_x + ib_w // 2 - high_text.get_width() // 2, ib_y + 110))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, (0, 0, 0, 50), (0, y), (WIDTH, y), 1)
        
        over_text = title_font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 200))
        
        score_msg = font.render(f"Score: {last_score}", True, WHITE)
        screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, 280))
        
        if last_score == high_score and last_score > 0:
            new_record = font.render("★ NEW RECORD ★", True, YELLOW)
            screen.blit(new_record, (WIDTH // 2 - new_record.get_width() // 2, 320))
        
        restart_text = font.render("[R] RESTART", True, NEON_GREEN)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 370))
        
        menu_text = small_font.render("[ESC] MENU", True, NEON_BLUE)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, 410))

    pygame.display.update()

pygame.quit()