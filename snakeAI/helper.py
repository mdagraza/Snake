import matplotlib.pyplot as plt
from IPython import display

plt.ion() # Modo interactivo activado

def plot(scores, mean_scores):
    display.clear_output(wait=True) # Limpiar la salida anterior
    display.display(plt.gcf()) # Mostrar la figura actual

    plt.clf() # Limpiar la figura para el próximo gráfico
    plt.xlabel('Número de juegos')
    plt.ylabel('Puntuación')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)

    plt.text(len(scores)-1, scores[-1], str(scores[-1])) # Mostrar la puntuación actual en el gráfico
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1])) # Mostrar la puntuación promedio en el gráfico
    plt.legend(['Puntuación', 'Puntuación Promedio'])

    plt.show(block=False)
    plt.pause(.1)