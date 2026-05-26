#pytorch: https://www.youtube.com/playlist?list=PLqnslRFeH2UrcDBWF5mfPGpqQDSta6VK4

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import numpy as np

class Linear_QNet(nn.Module): #definir la arquitectura de la red neuronal
  def __init__(self, input_size, hidden_size, output_size):
    super().__init__()
    self.linear1 = nn.Linear(input_size, hidden_size) #capa oculta
    self.linear2 = nn.Linear(hidden_size, output_size) #capa de salida

  def forward(self, x): #definir el proceso de forward pass
    x = F.relu(self.linear1(x)) #aplicar la función de activación ReLU a la salida de la capa oculta
    x = self.linear2(x) #obtener la salida de la capa de salida
    return x

  def save(self, file_name='model.pth'): #guardar el modelo entrenado
    model_folder_path = './model'
    if not os.path.exists(model_folder_path):
      os.makedirs(model_folder_path)

    file_name = os.path.join(model_folder_path, file_name)
    torch.save(self.state_dict(), file_name) #guardar los pesos del modelo en un archivo .pth

  def load(self, file_name='model.pth'): #cargar un modelo previamente guardado
    model_folder_path = './model'
    file_name = os.path.join(model_folder_path, file_name)
    if os.path.exists(file_name):
      self.load_state_dict(torch.load(file_name)) #cargar los pesos del modelo desde el archivo .pth
      self.eval() #poner el modelo en modo de evaluación para desactivar dropout y batch normalization
      print("Modelo cargado correctamente.")
    else:
      print("Archivo de modelo no encontrado.")

class QTrainer:
  def __init__(self, model, lr, gamma):
    self.lr = lr
    self.gamma = gamma
    self.model = model
    self.optimizer = optim.Adam(model.parameters(), lr=self.lr) #optimizador Adam para actualizar los pesos del modelo
    self.criterion = nn.MSELoss() #función de pérdida MSE para calcular el error entre las predicciones del modelo y las recompensas reales

  def train_step(self, state, action, reward, next_state, done):
    state = torch.tensor(np.array(state), dtype=torch.float) #convertir el estado a un tensor de PyTorch
    next_state = torch.tensor(np.array(next_state), dtype=torch.float) #convertir el siguiente estado a un tensor de PyTorch
    action = torch.tensor(np.array(action), dtype=torch.long) #convertir la acción a un tensor de PyTorch
    reward = torch.tensor(np.array(reward), dtype=torch.float) #convertir la recompensa a un tensor de PyTorch

    if len(state.shape) == 1: #si el estado es un vector unidimensional, agregar una dimensión adicional para que sea compatible con el modelo
      state = torch.unsqueeze(state, 0)
      next_state = torch.unsqueeze(next_state, 0)
      action = torch.unsqueeze(action, 0)
      reward = torch.unsqueeze(reward, 0)
      done = (done, )

    # Predicción del modelo
    pred = self.model(state) #obtener las predicciones del modelo para el estado actual
    target = pred.clone() #clonar las predicciones para crear el objetivo de entrenamiento
    for idx in range(len(done)): #Q_new = r + y * max(next_predicted Q value) || si el juego ha terminado, entonces Q_new = r
      Q_new = reward[idx] #recompensa para la acción tomada
      if not done[idx]: #si el juego no ha terminado, actualizar la recompensa con la recompensa futura descontada
        Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx])) #recompensa futura descontada

      target[idx][torch.argmax(action[idx]).item()] = Q_new #actualizar el objetivo de entrenamiento para la acción tomada

    self.optimizer.zero_grad() #reiniciar los gradientes del optimizador
    loss = self.criterion(target, pred) #calcular la pérdida entre el objetivo de entrenamiento y las predicciones del modelo
    loss.backward() #realizar backpropagation para calcular los gradientes

    self.optimizer.step() #actualizar los pesos del modelo utilizando el optimizador