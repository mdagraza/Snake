#Juego snake: https://www.youtube.com/watch?v=--nsd2ZeYvs
#Reinforcement learning: https://www.youtube.com/watch?v=PJl4iabBEz0&list=PLqnslRFeH2UrDh7vUmJ60YrmWd64mTTKV

import pygame

import random
from enum import Enum
from collections import namedtuple
import math
import numpy as np #Para usar arrays en lugar de listas para representar el estado del juego, lo que puede ser más eficiente para el aprendizaje automático

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
INCREMENT_SPEED = True #Si la velocidad aumenta al comer comida o no


font = pygame.font.SysFont('arial', 15) #Fuente para mostrar la puntuación

class SnakeGameAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h

        #inicializar pantalla
        self.display = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE if RESIZABLE else 0) #Permitir redimensionar la ventana
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock() #controlar FPS

        self.reset() #inicializar estado del juego

    def reset(self):
        self.direction = Direction.RIGHT
        self.speed = 50

        self.head = Point(self.w/2, self.h/2) #posicion inicial de la cabeza de la serpiente
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y), Point(self.head.x - 2 * BLOCK_SIZE, self.head.y)] #cuerpo inicial de la serpiente con tres bloques, como se mueve inicialmente a la derecha, los segundos y tercer bloque se coloca a la izquierda de la cabeza

        self.score = 0
        self.food = None
        self._place_food() #colocar la comida en una posición aleatoria
        self.frame_iteration = 0 #Contador de iteraciones para evitar que el juego se quede atascado en un bucle infinito sin comer comida

    def _place_food(self):
        #Generar una coordenada x e y aleatoria que sea un múltiplo de BLOCK_SIZE para asegurar que la comida se alinee con la cuadrícula del juego
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)

        if self.food in self.snake:
            self._place_food() #Si la comida se genera en una posición ocupada por la serpiente, se vuelve a generar

    def play_step(self, action):
      self.frame_iteration += 1

      #manejar eventos
      self._manage_events()

      #mover la serpiente
      self._move(action) #actualizar la posición de la cabeza de la serpiente según la dirección actual
      self.snake.insert(0, self.head) #insertar la nueva posición de la cabeza al inicio de la lista que representa el cuerpo de la serpiente

      #recompensa
      reward = 0

      #chequear colisiones
      game_over = False
      if self.is_collision() or self.frame_iteration > 100 * len(self.snake): #Si la serpiente choca o si ha pasado demasiado tiempo sin comer comida, el juego termina
          game_over = True
          reward = -10
          return reward, game_over, self.score
 
      #Poner comida nueva o mover la serpiente
      if self.head == self.food: #Si la cabeza de la serpiente está en la misma posición que la comida, significa que ha comido la comida
          self.score += 1
          reward = 10
          if INCREMENT_SPEED:
            self.speed += 0.25
          self._place_food() #Colocar una nueva comida en una posición aleatoria
      else:
          self.snake.pop() #Si no ha comido, se elimina el último bloque de la serpiente para simular el movimiento

      #actualizar UI y reloj
      self._update_ui()
      self.clock.tick(self.speed) #Controlar FPS del juego

      #devolver game_over y puntuacion
      return reward, game_over, self.score
    
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
                '''elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN'''
            elif event.type == pygame.VIDEORESIZE:
                self.w, self.h = event.size
                self.w = math.floor(self.w / BLOCK_SIZE) * BLOCK_SIZE #Ajustar el ancho al múltiplo más cercano de BLOCK_SIZE para mantener la cuadrícula alineada
                self.h = math.floor(self.h / BLOCK_SIZE) * BLOCK_SIZE
                self.display = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE if RESIZABLE else 0) #Actualizar el tamaño de la ventana al redimensionarla
                if self.food and (self.food.x >= self.w or self.food.y >= self.h): #Si la comida está fuera de los límites de la nueva ventana, se coloca una nueva comida
                    self._place_food()

    def _move(self, action):
        #[de frente, derecha, izquierda] 

        clock_wise_directions = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP] #Lista de direcciones en orden horario
        index_direction = clock_wise_directions.index(self.direction) #Obtener el índice de la dirección actual en la lista de direcciones

        if np.array_equal(action, [1, 0, 0]): #Si la acción es ir de frente, la dirección no cambia
            new_direction = clock_wise_directions[index_direction]
        elif np.array_equal(action, [0, 1, 0]): #Si la acción es girar a la derecha
            new_direction = clock_wise_directions[(index_direction + 1) % 4] # r -> d, d -> l, l -> u, u -> r
        elif np.array_equal(action, [0, 0, 1]): #Si la acción es girar a la izquierda
            new_direction = clock_wise_directions[(index_direction - 1) % 4] # r -> u, u -> l, l -> d, d -> r

        self.direction = new_direction #Actualizar la dirección de la serpiente

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y) #Actualizar la posición de la cabeza de la serpiente

    def is_collision(self, pt=None):
        if pt is None: #Si no se proporciona un punto específico para verificar la colisión, se verifica la colisión de la cabeza de la serpiente
            pt = self.head

        #Chequear si la serpiente choca con las paredes
        if COLLISION:
          if pt.x >= self.w or pt.x < 0 or pt.y >= self.h or pt.y < 0:
              return True
        else:
          self._teleport() #Si no hay colisión, teletransportar la serpiente a la posición opuesta

        #Chequear si la serpiente choca consigo misma
        if pt in self.snake[1:]: #Si la cabeza de la serpiente está en el resto del cuerpo, significa que se ha mordido a sí misma
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

'''if __name__ == "__main__":
    game = SnakeGameAI()
    
    #game loop
    while True:
        game_over, score = game.play_step()
        
        #game over
        if game_over:
            print('Final del juego. Puntuación: ', score)
            break

    pygame.quit()'''