import pygame
import sys
from typing import NoReturn
from constants import *
from assets import *

# Check command line arguments
CHEAT_MODE = "--cheaton" in sys.argv
SOUND_ENABLED = "--sound" in sys.argv
COLOR_ENABLED = "--color" in sys.argv

def end_game() -> NoReturn:
    pygame.mixer.quit()
    pygame.quit()
    quit()

# Init
pygame.init()
# Initialize joystick support (Xbox controllers etc.)
pygame.joystick.init()
joystick = None
JOYSTICK_ENABLED = False
# Deadzone for analog stick to avoid drift
AXIS_DEADZONE = 0.5
# Common Xbox mapping in pygame: A=0, B=1 (may vary by driver)
JOY_A_BUTTON = 0
JOY_B_BUTTON = 1
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    JOYSTICK_ENABLED = True
    try:
        print(f"Joystick detected: {joystick.get_name()}")
    except Exception:
        pass
# Set window attributes for Windows taskbar icon
if sys.platform == 'win32':  # Solo en Windows
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('agus0.otrotetris.1.0')

screen = pygame.display.set_mode(SCREEN_RESOLUTION)
clock = pygame.time.Clock()

# Set window title and icon
base_title = "otrotetris (agus0's fork)"
if CHEAT_MODE:
    pygame.display.set_caption(f"{base_title} [CHEAT ON]")
else:
    pygame.display.set_caption(base_title)

# Set window icon
try:
    icon = pygame.image.load('Tetris.ico')
    pygame.display.set_icon(icon)
except pygame.error:
    print("Warning: Tetris.ico not found")

Grid = World()

# Timer event
base_time_delay = 500 # velocidad de caida inicial
current_time_delay = base_time_delay
timer_event = pygame.USEREVENT + 1
pygame.time.set_timer(timer_event, current_time_delay)
pygame.mixer.init()
pygame.mixer.music.load('tetris.mp3')
# Inicializar estados según parámetros de línea de comando
Grid.sound_on = SOUND_ENABLED
Grid.color_mode = COLOR_ENABLED
if SOUND_ENABLED:
    pygame.mixer.music.play(-1)

def game_loop_scene() -> None:
    # Gameloop
    global current_time_delay
    lateral_move_delay = 150  # Delay para movimiento lateral (más lento para mejor control)
    down_move_delay = 25     # Delay para movimiento hacia abajo (muy rápido)
    last_move_time = 0
    game_pause = False
    # Joystick state helpers
    prev_hat = (0, 0)
    prev_axis_y = 0.0
    joystick_down_pressed = False  # From B button
    prev_down_active = False

    while not Grid.end:
        clock.tick(FPS)
        screen.fill(LIGHT_BLACK)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Window close button
                end_game()
            elif event.type == pygame.WINDOWFOCUSLOST:  # Window minimized or lost focus
                game_pause = True
                pygame.mixer.music.pause()
            elif event.type == pygame.WINDOWFOCUSGAINED:  # Window restored or gained focus
                game_pause = False
                pygame.mixer.music.unpause()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    end_game()
                if event.key == pygame.K_s:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                        Grid.sound_on = False
                    else:
                        Grid.sound_on = True
                        pygame.mixer.music.play(-1)  # Inicia la música si no estaba sonando
                if event.key == pygame.K_c:
                    Grid.color_mode = not Grid.color_mode
                if event.key == pygame.K_p:
                    game_pause = not game_pause
                    if game_pause and Grid.sound_on:
                        pygame.mixer.music.pause()
                    elif not game_pause and Grid.sound_on:
                        pygame.mixer.music.unpause()
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    Grid.level = min(Grid.level + 1, 30)  # Limitamos a nivel 15
                    current_time_delay = Grid.update_game_speed()
                    pygame.time.set_timer(timer_event, current_time_delay)
                if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    Grid.level = max(Grid.level - 1, 1)  # No permite bajar de nivel 1
                    current_time_delay = Grid.update_game_speed()
                    pygame.time.set_timer(timer_event, current_time_delay)
                
                # Control de movimientos normales
                can_move = not game_pause or (game_pause and CHEAT_MODE)
                
                if event.key == pygame.K_RIGHT and can_move:
                    Grid.move(1,0)
                    last_move_time = pygame.time.get_ticks()
                if event.key == pygame.K_LEFT and can_move:
                    Grid.move(-1,0)
                    last_move_time = pygame.time.get_ticks()
                if event.key == pygame.K_DOWN and can_move:
                    Grid.move(0,1)
                    last_move_time = pygame.time.get_ticks()  # Actualizar el tiempo del último movimiento
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if can_move:
                        Grid.rotate()
                
                # Controles de cheat mode
                if CHEAT_MODE:  # Permitir cambio de pieza en pausa si está en modo cheat
                    if event.key == pygame.K_F4:
                        Grid.change_piece(-1)  # Retroceder una pieza
                    if event.key == pygame.K_F5:
                        Grid.change_piece(1)   # Avanzar una pieza
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN and not game_pause:  # Solo restaurar el timer si no está en pausa
                    current_time_delay = Grid.update_game_speed()
                    pygame.time.set_timer(timer_event, current_time_delay)
            # Joystick button events: A -> rotate, B -> soft-drop (hold)
            elif event.type == pygame.JOYBUTTONDOWN:
                # Map A -> rotate
                if event.button == JOY_A_BUTTON:
                    if not game_pause:
                        Grid.rotate()
                # Map B -> start soft-drop
                if event.button == JOY_B_BUTTON:
                    if not game_pause:
                        joystick_down_pressed = True
                        last_move_time = pygame.time.get_ticks()
            elif event.type == pygame.JOYBUTTONUP:
                if event.button == JOY_B_BUTTON:
                    joystick_down_pressed = False
                    # restore timer when releasing B
                    if not game_pause:
                        current_time_delay = Grid.update_game_speed()
                        pygame.time.set_timer(timer_event, current_time_delay)
            elif event.type == timer_event:
                if not game_pause:  # La pieza solo baja automáticamente cuando no está en pausa
                    Grid.move(0,1)

        # Manejo de movimiento continuo
        can_move = not game_pause or (game_pause and CHEAT_MODE)
        current_time = pygame.time.get_ticks()
        
        # Movimiento lateral (más lento para mejor control)
        if current_time - last_move_time >= lateral_move_delay:
            if pygame.key.get_pressed()[pygame.K_LEFT] and can_move:
                Grid.move(-1, 0)
                last_move_time = current_time
            if pygame.key.get_pressed()[pygame.K_RIGHT] and can_move:
                Grid.move(1, 0)
                last_move_time = current_time
                
        # Movimiento hacia abajo (más rápido)
        if current_time - last_move_time >= down_move_delay:
            if pygame.key.get_pressed()[pygame.K_DOWN] and can_move:
                Grid.move(0, 1)
                last_move_time = current_time
                # Velocidad muy rápida para la caída automática mientras se presiona abajo
                current_time_delay = 25
                
        # --- Joystick polling (D-pad / left stick) ---
        if JOYSTICK_ENABLED and joystick is not None:
            # Read hat (D-pad) and axes (left stick)
            try:
                hat = joystick.get_hat(0)
            except Exception:
                hat = (0, 0)
            # Left stick (axes 0,1) and right stick (commonly axes 2,3) support
            left_x = joystick.get_axis(0) if joystick.get_numaxes() > 0 else 0.0
            left_y = joystick.get_axis(1) if joystick.get_numaxes() > 1 else 0.0
            right_x = joystick.get_axis(2) if joystick.get_numaxes() > 2 else 0.0
            right_y = joystick.get_axis(3) if joystick.get_numaxes() > 3 else 0.0
            # Combine axes so either stick can be used equivalently
            # Horizontal: prefer stronger input between sticks
            axis_x = left_x if abs(left_x) >= abs(right_x) else right_x
            # Vertical: prefer stronger input between sticks
            axis_y = left_y if abs(left_y) >= abs(right_y) else right_y

            # Horizontal movement: D-pad or left stick
            if can_move and current_time - last_move_time >= lateral_move_delay:
                if hat[0] == -1 or axis_x < -AXIS_DEADZONE:
                    Grid.move(-1, 0)
                    last_move_time = current_time
                elif hat[0] == 1 or axis_x > AXIS_DEADZONE:
                    Grid.move(1, 0)
                    last_move_time = current_time

            # Soft-drop (down): D-pad down, stick down or B button hold
            down_active = joystick_down_pressed or (hat[1] == -1) or (axis_y > AXIS_DEADZONE)
            if down_active and can_move and current_time - last_move_time >= down_move_delay:
                Grid.move(0, 1)
                last_move_time = current_time
                current_time_delay = 25

            # Rotation on up: D-pad up or stick up should rotate once on the edge
            if can_move:
                # hat edge
                if hat[1] == 1 and prev_hat[1] != 1:
                    Grid.rotate()
                # axis edge (analog up)
                if axis_y < -AXIS_DEADZONE and prev_axis_y >= -AXIS_DEADZONE:
                    Grid.rotate()

            # If down was active last frame but not now, restore timer
            if prev_down_active and not down_active and not game_pause:
                current_time_delay = Grid.update_game_speed()
                pygame.time.set_timer(timer_event, current_time_delay)

            prev_hat = hat
            prev_axis_y = axis_y
            prev_down_active = down_active
        #Creacion de figuras
        Grid.draw(screen)
        if game_pause:
            font = pygame.font.Font('freesansbold.ttf', 32)
            pause_text = font.render(' PAUSE ', True, WHITE, BLACK)
            pause_textRect = pause_text.get_rect()
            pause_textRect.center = (SCREEN_RESOLUTION[0] // 2, SCREEN_RESOLUTION[1] // 2)
            screen.blit(pause_text, pause_textRect)
        pygame.display.update()
        
        
    end_scene()

def end_scene() -> None:
    #Game loop
    pygame.mixer.music.stop()
    restart = False
    while not restart:
        clock.tick(FPS)


        #Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Window close button
                end_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    end_game()
                if event.key == pygame.K_SPACE:
                    current_time_delay = Grid.update_game_speed()
                    pygame.time.set_timer(timer_event, current_time_delay)
                    pygame.mixer.music.play(-1) 
                    restart = True
        
        key = pygame.key.get_pressed()

        #Draw
        #Draw a text using pygame
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(' GAME OVER ', True, RED, WHITE)
        textRect = text.get_rect()
        textRect.center = (SCREEN_RESOLUTION[0] // 2, SCREEN_RESOLUTION[1]//2)
        screen.blit(text, textRect)

        pygame.display.update()
    Grid.__init__()
    game_loop_scene()

game_loop_scene()


