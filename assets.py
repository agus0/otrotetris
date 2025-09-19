import pygame
from constants import *
from typing import Literal
import random

block_list = [I_PIECE,J_PIECE,L_PIECE,O_PIECE,T_PIECE,S_PIECE,Z_PIECE]

# Jblock,Lblock,Oblock,Sblock
# logica_rotacion = list(zip(*tblock[::-1])) Esto invierte nuestra lista de [[0,2,0],[2,2,2]] a [[2,2,2],[0,2,0]]
class World:
    def __init__(self) -> None:
        self.end = False 
        self.rows = 20
        self.columns = 10
        self.cell_size = 30
        self.score = 0 
        self.level = 1
        self.sound_on = True
        self.color_mode = True  # True for colored pieces, False for black only
        self.size = (self.columns * self.cell_size, self.rows * self.cell_size)

        self.grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)] # Son tuplas dentro de otra tupla
        #print(self.grid)

        #self.grid[-1] = [1 for _ in range(self.columns)]
        #self.grid[-1][0] = 0
        buffer_block = random.choice(block_list)
        self.next_block = buffer_block.shape
        self.next_block_color = buffer_block.color
        buffer_block = random.choice(block_list)
        self.block = buffer_block.shape
        self.block_color = buffer_block.color
        self.block_offset = [int(self.columns/2)-1, 0]
    
    def move (self, x, y) -> None:
        self.block_offset[0] += x
        if self.collision():
            self.block_offset[0] -=x
        
        self.block_offset[1] += y
        if self.collision():
            self.block_offset[1] -= y
            # Only end game if collision happens at top row
            self.fix_block()
            if any(any(cell != 0 for cell in row) for row in self.grid[:1]):  # Check only top row
                self.end = True
            self.clear_rows()

            self.block = self.next_block
            self.block_color = self.next_block_color
            buffer_block = random.choice(block_list)
            self.next_block = buffer_block.shape
            self.next_block_color = buffer_block.color
            self.block_offset = [int(self.columns/2)-1, 0]
        
    def clear_rows(self) -> None:
        rows_cleared = 0
        for i, row in enumerate(self.grid):
            if all(row): # (all) Si todos los valores son distintos a null o 0 devuelve True.
                self.grid.pop(i)
                self.grid.insert(0, [0 for _ in range(self.columns)])
                rows_cleared += 1
        
        if rows_cleared > 0:
            self.score += self.columns * rows_cleared
            # Check for level up (every 100 points), but don't decrease level if manually set higher
            new_level = max((self.score // 100) + 1, self.level)
            if new_level != self.level:
                self.level = new_level
                # Update game speed in main.py through a new method
                self.update_game_speed()
    

    def fix_block(self) -> None:
        for i, block_row in enumerate(self.block):
            for j, block_element in enumerate(block_row):
                if block_element != 0:
                    self.grid[i + self.block_offset[1]][j + self.block_offset[0]] = [TetrisPiece(block_row, self.block_color)]

        
    def update_game_speed(self) -> int:
        # Base speed is 500ms, decrease by 10% for each level (min 100ms)
        base_speed = 500
        speed = int(base_speed * (0.9 ** (self.level - 1)))
        return max(speed, 100)  # Don't go faster than 100ms

    def change_piece(self, direction: int = 1) -> None:
        before_state = self.block
        before_color = self.block_color
        
        # Find current piece index by color instead of shape
        current_piece = None
        for i, piece in enumerate(block_list):
            if piece.color == self.block_color:
                current_piece = i
                break
        
        # Si no encontramos por color, usamos el primer índice
        if current_piece is None:
            current_piece = 0
            
        # Calculate next index based on direction (1 for forward, -1 for backward)
        next_index = (current_piece + direction) % len(block_list)
        new_piece = block_list[next_index]
        
        # Try to change to new piece
        self.block = [list(row) for row in new_piece.shape]  # Crear una nueva copia de la forma
        self.block_color = new_piece.color
        if self.collision():
            self.block = before_state
            self.block_color = before_color

    def rotate(self) -> None:
        before_state = self.block
        self.block = list(zip(*self.block[::-1]))  # Rotar la pieza
        if self.collision():
            self.block = before_state  # Restaurar la pieza a su estado anterior


    def collision(self) -> Literal[True] | None:
        #Detect end of screen
        if self.block_offset[0] < 0:
            return True
        if self.block_offset[0] >= self.columns - len(self.block[0]) + 1:
            return True
        # Vertical collision
        if self.block_offset[1] > self.rows - len(self.block):
            return True
        # Detect if there are block on the sides
        for i, block_row in enumerate(self.block):
            for j, block_element in enumerate(block_row):
                if block_element != 0:
                    if self.grid[i + self.block_offset[1]][j + self.block_offset[0]] != 0:
                        return True
    

    def draw(self, screen):
        # Draw score and controls on the left side
        font = pygame.font.Font('freesansbold.ttf', 24)
        text_x = 20  # Left margin
        
        # Draw level
        level_text = font.render(f'Level: {self.level}', True, WHITE)
        level_rect = level_text.get_rect()
        level_rect.x = text_x
        level_rect.y = 50
        screen.blit(level_text, level_rect)

        # Draw score
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.x = text_x
        score_rect.y = 90  # Increased spacing
        screen.blit(score_text, score_rect)

        # Add some extra spacing before controls
        controls_y_start = 160  # Increased spacing before controls

        # Draw keyboard shortcuts
        controls_font = pygame.font.Font('freesansbold.ttf', 20)
        controls = [
            ('Q', 'Quit'),
            ('P', 'Pause'),
            ('+/-', 'Change Level')
        ]
        
        for i, (key, action) in enumerate(controls):
            text = font.render(f'{key}: {action}', True, WHITE)
            rect = text.get_rect()
            rect.x = text_x
            rect.y = controls_y_start + i * 35  # Increased spacing between controls
            screen.blit(text, rect)
            
        # Draw colored key controls after basic controls
        controls_colored = [
            ('S', 'Sound', self.sound_on),
            ('C', 'Color Mode', self.color_mode)
        ]
        
        for i, (key, action, state) in enumerate(controls_colored):
            text = font.render(f'{key}: {action}', True, GREEN if state else RED)
            rect = text.get_rect()
            rect.x = text_x
            rect.y = controls_y_start + (len(controls) + i) * 35  # Continue spacing after basic controls
            screen.blit(text, rect)

        for i in range(0,self.rows):
            for j in range(self.columns):
                posicion = (
                    j * self.cell_size + SCREEN_RESOLUTION[0] / 2 - self.columns * self.cell_size / 2,#calcula la posición en píxeles de una celda en la columna j de manera que esté centrada horizontalmente en la pantalla.
                    i * self.cell_size + SCREEN_RESOLUTION[1] / 2 - self.rows * self.cell_size / 2,
                    self.cell_size,
                    self.cell_size,
                )
                if self.grid[i][j] == 0:
                    pygame.draw.rect(screen, COLORS[0], posicion, 1)  # Empty cell with border
                else:
                    # Fixed pieces use color mode, but always use their actual color for falling pieces
                    color = self.grid[i][j][0].color if isinstance(self.grid[i][j], list) else COLORS[0]
                    if not self.color_mode:
                        color = COLORS[0]  # Black only for fixed pieces in monochrome mode
                    pygame.draw.rect(screen, color, posicion, 0)  # Filled cell without border
        # Draw "Next Piece" label
        next_text = font.render("Next Piece", True, WHITE)
        next_rect = next_text.get_rect()
        next_rect.x = SCREEN_RESOLUTION[0] / 2 + self.size[0] / 2 + 20
        next_rect.y = SCREEN_RESOLUTION[1] / 2 - self.size[1] / 2 - 20
        screen.blit(next_text, next_rect)

        # Draw next block
        for i, block_row in enumerate(self.next_block):
            for j, block_element in enumerate(block_row):
                posicion = (
                    j * self.cell_size + SCREEN_RESOLUTION[0] / 2 + self.size[0] / 2 + 20,  # Moved to right side with 20px margin
                    i * self.cell_size + SCREEN_RESOLUTION[1] / 2 - self.size[1] / 2 + 20,  # Aligned with game board top with 20px margin
                    self.cell_size,
                    self.cell_size
                )
                if block_element != 0:
                    pygame.draw.rect(screen, self.next_block_color, posicion, 0)  # Always colored for next piece

        # Draw current block
        for i, block_row in enumerate(self.block):
            for j, block_element in enumerate(block_row):
                posicion = (
                    j * self.cell_size + SCREEN_RESOLUTION[0] / 2 - self.size[0] / 2 + self.block_offset[0] * self.cell_size,
                    i * self.cell_size + SCREEN_RESOLUTION[1] / 2 - self.size[1] / 2 + self.block_offset[1] * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                if block_element != 0:
                    pygame.draw.rect(screen, self.block_color, posicion, 0)  # Always colored for falling piece
