import pygame
import sys
from typing import NoReturn
from constants import *
from assets import *

# Check for cheat mode in command line arguments
CHEAT_MODE = "--cheaton" in sys.argv

def end_game() -> NoReturn:
    pygame.mixer.quit()
    pygame.quit()
    quit()

# Init
pygame.init()
screen = pygame.display.set_mode(SCREEN_RESOLUTION)
clock = pygame.time.Clock()

Grid = World()

# Timer event
base_time_delay = 500 # velocidad de caida inicial
current_time_delay = base_time_delay
timer_event = pygame.USEREVENT + 1
pygame.time.set_timer(timer_event, current_time_delay)
pygame.mixer.init()
pygame.mixer.music.load('tetris.mp3')
# Música apagada por defecto
Grid.sound_on = False

def game_loop_scene() -> None:
    # Gameloop
    move_repeat_delay = 200  # Sensibilidad, cuanto mayor mas lento se mueve
    last_move_time = 0
    game_pause = False

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
                    Grid.move(0,1)  # Movimiento directo hacia abajo en modo cheat
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
            elif event.type == timer_event:
                if not game_pause:  # La pieza solo baja automáticamente cuando no está en pausa
                    Grid.move(0,1)

        # Manejo de movimiento continuo
        can_move = not game_pause or (game_pause and CHEAT_MODE)
        if pygame.key.get_pressed()[pygame.K_LEFT] and can_move:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time >= move_repeat_delay:
                Grid.move(-1, 0)
                last_move_time = current_time
        if pygame.key.get_pressed()[pygame.K_RIGHT] and can_move:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time >= move_repeat_delay:
                Grid.move(1, 0)
                last_move_time = current_time
                
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


