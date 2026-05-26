import torch
import random
import os
import numpy as np
from collections import deque #para almacenar las experiencias de entrenamiento
from snake_game_AI import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000 #maximo de experiencias a almacenar
BATCH_SIZE = 1000 #tamaño del batch para el entrenamiento
LR = 0.001 #learning rate | tasa de aprendizaje, que controla cuánto se ajustan los pesos del modelo en respuesta al error cada vez que se actualizan los pesos

class SnakeAgent:
  def __init__(self):
    self.n_games = 0
    self.epsilon = 0 #controla la exploración vs explotación, se ajustará a medida que el agente juegue más juegos
    self.gamma = 0.9 #factor de descuento para futuras recompensas, que determina la importancia de las recompensas futuras en comparación con las recompensas inmediatas (Menos de 1 hace que el agente valore más las recompensas inmediatas, mientras que un valor cercano a 1 hace que el agente valore más las recompensas futuras)
    self.memory = deque(maxlen=MAX_MEMORY) #memoria para almacenar experiencias de entrenamiento | Se borra automáticamente la experiencia más antigua cuando se alcanza el límite de memoria
    
    self.model = Linear_QNet(11, 256, 3) #modelo de red neuronal con 11 entradas (estado), 256 neuronas en la capa oculta y 3 salidas (acciones)
    self.trainer = QTrainer(self.model, LR, self.gamma) #entrenador para actualizar los pesos del modelo en función de las experiencias de entrenamiento

    if os.path.exists('./model/model.pth'):
      self.model.load() #cargar el modelo si existe un archivo de modelo guardado
    self._load_data() #cargar los datos de entrenamiento, como el número de juegos jugados y el valor de epsilon, para que puedan ser cargados en futuras sesiones de entrenamiento

  def get_state(self, game): #obtener el estado actual del juego, que se usará como entrada para la red neuronal
    #[peligro de frente, peligro de la derecha, peligro de la izquierda, dirección izquierda, dirección derecha, dirección arriba, dirección abajo, comida a la izquierda, comida a la derecha, comida arriba, comida abajo]
    head = game.snake[0] #obtener la cabeza de la serpiente
    point_l = Point(head.x - 20, head.y) #punto a la izquierda de la cabeza
    point_r = Point(head.x + 20, head.y) #punto a la derecha de la cabeza
    point_u = Point(head.x, head.y - 20) #punto arriba de la cabeza
    point_d = Point(head.x, head.y + 20) #punto abajo de la cabeza

    dir_l = game.direction == Direction.LEFT #si la dirección actual es izquierda
    dir_r = game.direction == Direction.RIGHT #si la dirección actual es derecha
    dir_u = game.direction == Direction.UP #si la dirección actual es arriba
    dir_d = game.direction == Direction.DOWN #si la dirección actual es abajo

    state = [
        #peligro de frente
        (dir_r and game.is_collision(point_r)) or (dir_l and game.is_collision(point_l)) or (dir_u and game.is_collision(point_u)) or (dir_d and game.is_collision(point_d)),
        #peligro de la derecha
        (dir_u and game.is_collision(point_r)) or (dir_d and game.is_collision(point_l)) or (dir_l and game.is_collision(point_u)) or (dir_r and game.is_collision(point_d)),
        #peligro de la izquierda
        (dir_d and game.is_collision(point_r)) or (dir_u and game.is_collision(point_l)) or (dir_r and game.is_collision(point_u)) or (dir_l and game.is_collision(point_d)),
        #dirección izquierda
        dir_l,
        #dirección derecha
        dir_r,
        #dirección arriba
        dir_u,
        #dirección abajo
        dir_d,
        #comida a la izquierda
        game.food.x < game.head.x,
        #comida a la derecha
        game.food.x > game.head.x,
        #comida arriba
        game.food.y < game.head.y,
        #comida abajo
        game.food.y > game.head.y
    ]

    return np.array(state, dtype=int) #convertir el estado a un array de numpy, que se usará como entrada para la red neuronal | Convierte los booleans a enteros (0 o 1) para que puedan ser procesados por la red neuronal

  def remember(self, state, action, reward, next_state, done): #almacenar la experiencia en la memoria
    self.memory.append((state, action, reward, next_state, done)) #agregar la experiencia a la memoria

  def train_long_memory(self): #entrenar con un batch de experiencias almacenadas
    if len(self.memory) > BATCH_SIZE: #si hay suficientes experiencias en la memoria para formar un batch
      mini_sample = random.sample(self.memory, BATCH_SIZE) #seleccionar un batch aleatorio de experiencias de la memoria
    else:
      mini_sample = self.memory #si no hay suficientes experiencias, usar todas las experiencias disponibles

    states, actions, rewards, next_states, dones = zip(*mini_sample) #desempaquetar las experiencias del batch | zip(*mini_sample) separa cada elemento de las tuplas en mini_sample
    self.trainer.train_step(states, actions, rewards, next_states, dones)

    self._save_data() #guardar los datos de entrenamiento, como el número de juegos jugados y el valor de epsilon, para que puedan ser cargados en futuras sesiones de entrenamiento

  def train_short_memory(self, state, action, reward, next_state, done): #entrenar con una sola experiencia
    self.trainer.train_step(state, action, reward, next_state, done) #entrenar el modelo con una sola experiencia

  def get_action(self, state): #decidir la acción a tomar en base al estado actual
    #movimientos aleatorios: equilibrio entre exploración y explotación
    self.epsilon = 80 - self.n_games #a medida que el agente juega más juegos, la probabilidad de tomar una acción aleatoria disminuye
    final_move = [0, 0, 0] #inicializar la acción a tomar | [1, 0, 0] -> ir recto | [0, 1, 0] -> girar a la derecha | [0, 0, 1] -> girar a la izquierda

    if random.randint(0, 200) < self.epsilon:
      move = random.randint(0, 2)
      final_move[move] = 1
    else:
      state0 = torch.tensor(state, dtype=torch.float) #convertir el estado a un tensor de PyTorch, que se usará como entrada para la red neuronal
      prediction = self.model(state0) #predecir la acción a tomar en base al estado actual usando el modelo de red neuronal
      move = torch.argmax(prediction).item() #obtener la acción con la mayor probabilidad de ser la mejor acción
      final_move[move] = 1

    return final_move
  
  def _save_data(self):
    with open('./model/data.txt', 'a') as f:
      f.write(f'{self.n_games},{self.epsilon}\n')

  def _load_data(self):
    try:
      with open('./model/data.txt', 'r') as f:
        lines = f.readlines()
        if lines:
          last_line = lines[-1]
          self.n_games, self.epsilon = map(int, last_line.strip().split(','))
    except FileNotFoundError:
      pass

def train():
  plot_scores = [] #para almacenar los puntajes de cada juego
  plot_mean_scores = [] #para almacenar los puntajes promedio
  total_score = 0 #para almacenar el puntaje total acumulado
  record = 0 #para almacenar el puntaje más alto alcanzado
  n_games = 0 #para almacenar el número de juegos jugados
  agent = SnakeAgent() 
  game = SnakeGameAI() 

  while True:
    #obtener el estado actual del juego
    state_old = agent.get_state(game)

    #decidir la acción a tomar
    final_move = agent.get_action(state_old)

    #realizar la acción y obtener la nueva información del juego
    reward, done, score = game.play_step(final_move)
    state_new = agent.get_state(game)

    #entrenar con la experiencia reciente
    agent.train_short_memory(state_old, final_move, reward, state_new, done)

    #almacenar la experiencia en la memoria
    agent.remember(state_old, final_move, reward, state_new, done)

    if done: #game over, entrenar con un batch de experiencias almacenadas y reiniciar el juego
      game.reset()
      agent.n_games += 1
      n_games += 1
      agent.train_long_memory()

      if score > record:
        record = score
        agent.model.save() #guardar el modelo si se alcanza un nuevo récord

      print('Game:', n_games, '| Score:', score, '| Record:', record, '| N Games:', agent.n_games, '| Epsilon:', agent.epsilon)

      #Plot
      plot_scores.append(score)
      total_score += score
      mean_score = total_score / n_games
      plot_mean_scores.append(mean_score)
      plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
  train()