# Snake

Este repositorio contiene una implementación del juego de la serpiente en dos modos:

- Juego normal: controla la serpiente manualmente.
- Juego con DQN: utiliza un agente de aprendizaje por refuerzo con Deep Q-Network.

## Juego normal

El modo normal es el juego clásico de Snake. El jugador mueve la serpiente en un tablero para comer alimento y crecer sin chocar contra las paredes ni contra su propio cuerpo.

Características:

- Control manual de la serpiente.
- Meta: obtener la mayor puntuación posible.
- Cada vez que la serpiente come comida, crece un segmento.
- El juego termina si la serpiente choca contra una pared o contra sí misma.

## Juego con DQN

El modo DQN utiliza un agente de inteligencia artificial basado en Deep Q-Network para aprender a jugar automáticamente.

Características:

- El agente observa el estado del juego y toma decisiones basadas en una red neuronal.
- Usa recompensas para aprender: recibe puntos por comer comida y penalizaciones por colisiones.
- El agente explora acciones y actualiza su política de juego con entrenamiento.
- Permite comparar el rendimiento del agente con el modo manual.

## Constantes editables

El proyecto contiene varias constantes que se pueden ajustar para cambiar el comportamiento del juego y del agente DQN. Algunas constantes típicas son:

- `COLLISION`: opción de colisionar con los bordes de la ventana, o teletransportarse al otro lado.
- `RESIZABLE`: opción de redimensionar la ventana.
- `BLOCK_SIZE`: tamaño de cada bloque en el tablero.

Para DQN (Además de los ya mencionados antes):

- `INCREMENT_SPEED`: la velocidad vaya incrementando según va creciendo la serpiente.
- `SAVE_AND_LOAD_MODEL`: guardar y cargar datos de aprendizaje para continuar dónde se quedo tras cerrar.
- `MAX_MEMORY`: tamaño máximo del buffer de experiencia.
- `BATCH_SIZE`: tamaño de los lotes usados para entrenar la red.
- `LR`: tasa de aprendizaje
