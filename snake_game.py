#Juego snake: https://www.youtube.com/watch?v=--nsd2ZeYvs

import pygame

import random
from enum import Enum
from collections import namedtuple
import math

pygame.init() # Inicializar Pygame

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
 
class Colors(tuple, Enum): #Al poner tuple, devuelve un tuple, lo que permite usarlo como color en pygame
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN1 = (0, 100, 0)
    GREEN2 = (0, 150, 0)
    BLUE = (0, 0, 255)

Point = namedtuple('Point', 'x, y') #Definir un punto con coordenadas x e y | Similar a un dict pero con acceso a los elementos por nombre

BLOCK_SIZE = 10 #Tamaño de cada bloque de la serpiente y la comida
COLLISION = True #Si colision contra la pared o no
RESIZABLE = False #Si la ventana es redimensionable o no

font = pygame.font.SysFont('arial', 15) #Fuente para mostrar la puntuación

class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h

        #inicializar pantalla
        self.display = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE if RESIZABLE else 0) #Permitir redimensionar la ventana
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock() #controlar FPS

        #inicializar estado del juego
        self.direction = Direction.RIGHT
        self.speed = 10

        self.head = Point(self.w/2, self.h/2) #posicion inicial de la cabeza de la serpiente
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y)] #cuerpo inicial de la serpiente con dos bloques, como se mueve inicialmente a la derecha, el segundo bloque se coloca a la izquierda de la cabeza

        self.score = 0
        self.food = None
        self._place_food() #colocar la comida en una posición aleatoria

    def _place_food(self):
        #Generar una coordenada x e y aleatoria que sea un múltiplo de BLOCK_SIZE para asegurar que la comida se alinee con la cuadrícula del juego
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)

        if self.food in self.snake:
            self._place_food() #Si la comida se genera en una posición ocupada por la serpiente, se vuelve a generar

    def play_step(self):
      #manejar eventos
      self._manage_events()

      #mover la serpiente
      self._move(self.direction) #actualizar la posición de la cabeza de la serpiente según la dirección actual
      self.snake.insert(0, self.head) #insertar la nueva posición de la cabeza al inicio de la lista que representa el cuerpo de la serpiente

      #chequear colisiones
      game_over = False
      if self._is_collision():
          game_over = True
          return game_over, self.score
 
      #Poner comida nueva o mover la serpiente
      if self.head == self.food: #Si la cabeza de la serpiente está en la misma posición que la comida, significa que ha comido la comida
          self.score += 1
          self.speed += 0.25
          self._place_food() #Colocar una nueva comida en una posición aleatoria
      else:
          self.snake.pop() #Si no ha comido, se elimina el último bloque de la serpiente para simular el movimiento

      #actualizar UI y reloj
      self._update_ui()
      self.clock.tick(self.speed) #Controlar FPS del juego

      #devolver game_over y puntuacion
      return game_over, self.score
    
    def _update_ui(self):
        self.display.fill(Colors.BLACK) #Limpia la pantalla, pintando todo

        #Dibujar serpiente, primero cabeza y luego cuerpo
        pygame.draw.rect(self.display, Colors.GREEN1, pygame.Rect(self.head.x, self.head.y, BLOCK_SIZE, BLOCK_SIZE))
        for pt in self.snake[1:]:
            pygame.draw.rect(self.display, Colors.GREEN2, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)) #Dibujar cada bloque de la serpiente en la pantalla usando un rectángulo verde (punto x, punto y, ancho, alto)

        if self.food:
            pygame.draw.rect(self.display, Colors.RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Puntuación: " + str(self.score) + " | Velocidad: " + str(self.speed), True, Colors.WHITE) #Renderizar el texto de la puntuación en blanco
        self.display.blit(text, [0, 0]) #Dibujar el texto en la pantalla en la esquina superior izquierda
        pygame.display.flip() #Actualizar la pantalla

    def _manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
            elif event.type == pygame.VIDEORESIZE:
                self.w, self.h = event.size
                self.w = math.floor(self.w / BLOCK_SIZE) * BLOCK_SIZE #Ajustar el ancho al múltiplo más cercano de BLOCK_SIZE para mantener la cuadrícula alineada
                self.h = math.floor(self.h / BLOCK_SIZE) * BLOCK_SIZE
                self.display = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE if RESIZABLE else 0) #Actualizar el tamaño de la ventana al redimensionarla
                if self.food and (self.food.x >= self.w or self.food.y >= self.h): #Si la comida está fuera de los límites de la nueva ventana, se coloca una nueva comida
                    self._place_food()

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y) #Actualizar la posición de la cabeza de la serpiente

    def _is_collision(self):
        #Chequear si la serpiente choca con las paredes
        if COLLISION:
          if self.head.x >= self.w or self.head.x < 0 or self.head.y >= self.h or self.head.y < 0:
              return True
        else:
          self._teleport() #Si no hay colisión, teletransportar la serpiente a la posición opuesta

        #Chequear si la serpiente choca consigo misma
        if self.head in self.snake[1:]: #Si la cabeza de la serpiente está en el resto del cuerpo, significa que se ha mordido a sí misma
            return True

        return False
    
    def _teleport(self):
        #Teletransportar la serpiente a la posición opuesta si choca con las paredes
        if self.head.x >= self.w:
            self.head = Point(0, self.head.y)
        elif self.head.x < 0:
            self.head = Point(self.w - BLOCK_SIZE, self.head.y)
        elif self.head.y >= self.h:
            self.head = Point(self.head.x, 0)
        elif self.head.y < 0:
            self.head = Point(self.head.x, self.h - BLOCK_SIZE)

        self.snake[0] = self.head #Actualizar la posición de la cabeza en el cuerpo de la serpiente después de teletransportarla

if __name__ == "__main__":
    game = SnakeGame()
    
    #game loop
    while True:
        game_over, score = game.play_step()
        
        #game over
        if game_over:
            print('Final del juego. Puntuación: ', score)
            break

    pygame.quit()