import pygame
import sys
from dataclasses import dataclass
import copy

@dataclass(slots=True)
class Posicion:
    x: int
    y: int

class SnakeGame:

    def __init__(self):
        # Inicializar pygame
        pygame.init()

        # Pantalla
        self.ancho = 600
        self.alto = 400

        self.ventana = pygame.display.set_mode((self.ancho, self.alto), pygame.RESIZABLE)
        pygame.display.set_caption("Snake Game")

        # Colores
        self.NEGRO = (0, 0, 0)
        self.CUERPO = (0, 100, 0)
        self.CABEZA = (0, 150, 0)
        self.GRIS = (200, 200, 200)
        self.BLANCO = (255, 255, 255)

        self.posiciones = [Posicion(self.ancho / 2, self.alto / 2)]

        self.limite_superior = 30
        self.limite_inferior = 10
        self.limite_izquierda = 10
        self.limite_derecha = 10

        self.pos_comida = Posicion(0, 0)
        self.comida_pos_x = 0
        self.comida_pos_y = 0

        self.generar_comida()

        # Movimiento
        self.movimiento = (-10, 0)
        self.prox_movimiento = []

        self.velocidad = 5

        self.fin_juego = False
        self.puntuacion = 0

        # FPS
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont("Arial", 15)

    def manejar_eventos(self):
        for evento in pygame.event.get():

            # Cerrar ventana
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Teclado
            if evento.type == pygame.KEYDOWN:
                print("Evento: ", evento, "Time: ", pygame.time.get_ticks())
                if evento.key == pygame.K_LEFT and self.movimiento[0] == 0:
                    print("Izquierda")
                    self.prox_movimiento.append((-10, 0))

                elif evento.key == pygame.K_RIGHT and self.movimiento[0] == 0:
                    print("Derecha")
                    self.prox_movimiento.append((10, 0))

                elif evento.key == pygame.K_UP and self.movimiento[1] == 0:
                    print("Arriba")
                    self.prox_movimiento.append((0, -10))

                elif evento.key == pygame.K_DOWN and self.movimiento[1] == 0:
                    print("Abajo")
                    self.prox_movimiento.append((0, 10))

            # Redimensionar ventana
            if evento.type == pygame.VIDEORESIZE:
                self.ancho, self.alto = evento.size
                if self.pos_comida.x < self.limite_izquierda or self.pos_comida.x >= self.ancho - self.limite_derecha or self.pos_comida.y < self.limite_superior or self.pos_comida.y >= self.alto - self.limite_inferior:
                    self.generar_comida()
                
                #self.ventana = pygame.display.set_mode((self.ancho, self.alto), pygame.RESIZABLE)

    def actualizar_movimiento(self):
        if self.prox_movimiento:
            self.movimiento = self.prox_movimiento.pop(0)

    def actualizar(self):
        self.colision_serpiente()

        cabeza = copy.deepcopy(self.posiciones[0])#Se usa copy, porque si se iguala directamente, esta copiando la referencia,no el valor

        # Mover la cabeza de la serpiente
        cabeza.x += self.movimiento[0]
        cabeza.y += self.movimiento[1]

        # Eliminar la cola de la serpiente
        if len(self.posiciones) > 0:
            self.posiciones.insert(0, Posicion(cabeza.x, cabeza.y))
            if cabeza.x == self.comida_pos_x and cabeza.y == self.comida_pos_y:
                self.puntuacion += 1
                #if self.puntuacion % 3 == 0:
                self.velocidad += 0.5

                self.generar_comida()
            else:
                self.posiciones.pop()

        #print("Posiciones: ", [f"({pos.x}, {pos.y})" for pos in self.posiciones])

        # Teletransportar si sale de la pantalla
        if cabeza.x <= self.limite_izquierda:
            self.posiciones[0].x = self.ancho - self.limite_derecha - 10

        elif cabeza.x >= self.ancho - self.limite_derecha:
            self.posiciones[0].x = self.limite_izquierda + 10

        if cabeza.y <= self.limite_superior:
            self.posiciones[0].y = self.alto - self.limite_inferior - 10

        elif cabeza.y >= self.alto - self.limite_inferior:
            self.posiciones[0].y = self.limite_superior + 10

    def dibujar_cuadricula(self):
        # Líneas verticales
        for x in range(0, self.ancho, 10):
            pygame.draw.line(
                self.ventana,
                self.GRIS,
                (x, 0),
                (x, self.alto),
                1
            )

        # Líneas horizontales
        for y in range(0, self.alto, 10):
            pygame.draw.line(
                self.ventana,
                self.GRIS,
                (0, y),
                (self.ancho, y),
                1
            )

    def dibujar_limites(self):
        # Límites
        pygame.draw.line(
            self.ventana,
            self.GRIS,
            (self.limite_izquierda, 0),
            (self.limite_izquierda, self.alto),
            1
        )

        pygame.draw.line(
            self.ventana,
            self.GRIS,
            (self.ancho - self.limite_derecha, 0),
            (self.ancho - self.limite_derecha, self.alto),
            1
        )

        pygame.draw.line(
            self.ventana,
            self.GRIS,
            (0, self.limite_superior),
            (self.ancho, self.limite_superior),
            1
        )

        pygame.draw.line(
            self.ventana,
            self.GRIS,
            (0, self.alto - self.limite_inferior),
            (self.ancho, self.alto - self.limite_inferior),
            1
        )

    def dibujar_comida(self):
        pygame.draw.rect(
            self.ventana,
            (255, 0, 0),
            (
                self.comida_pos_x - 5,
                self.comida_pos_y - 5,
                10,
                10
            )
        )

    def generar_comida(self):
        import random

        #self.comida_pos_x = random.randint(5, (self.ancho - 15) // 10) * 10 #-10 por el ancho del cuadro y -5 por el centro del cuadro
        #self.comida_pos_y = random.randint(5, (self.alto - 15) // 10) * 10

        self.comida_pos_x = random.randint(
            (self.limite_izquierda // 10) + 1,
            ((self.ancho - self.limite_derecha) // 10) - 1
        ) * 10

        self.comida_pos_y = random.randint(
            (self.limite_superior // 10) + 1,
            ((self.alto - self.limite_inferior) // 10) - 1
        ) * 10

        self.pos_comida = Posicion(self.comida_pos_x, self.comida_pos_y)

    def dibujar_snake(self):
        for pos in self.posiciones:
            pygame.draw.rect(
                self.ventana,
                self.CUERPO,
                (
                    pos.x - 5,
                    pos.y - 5,
                    10,
                    10
                )
            )

    def guardar_posicion(self):
        self.posiciones.append(Posicion(self.posiciones[0].x, self.posiciones[0].y))

    def dibujar(self):

        # Fondo
        self.ventana.fill(self.NEGRO)

        # Cuadrícula
        #self.dibujar_cuadricula()

        self.dibujar_limites()

        self.dibujar_puntuacion()

        self.dibujar_comida()

        self.dibujar_snake()

        # Snake
        pygame.draw.rect(
            self.ventana,
            self.CABEZA,
            (
                self.posiciones[0].x - 5,
                self.posiciones[0].y - 5,
                10,
                10
            )
        )

        # Actualizar pantalla
        pygame.display.flip()

    def juego_terminado(self):
        print("¡Juego terminado!")

    def colision_serpiente(self):
        cabeza = self.posiciones[0]
        for pos in self.posiciones[2:]:
            #print(f"Pos: ({pos.x}, {pos.y}) | Cabeza: ({cabeza.x}, {cabeza.y})")
            if cabeza.x == pos.x and cabeza.y == pos.y:
                self.juego_terminado()

    def dibujar_puntuacion(self):
        texto = self.fuente.render(f"Puntuación: {self.puntuacion} | Velocidad: {self.velocidad}", True, self.BLANCO)
        self.ventana.blit(texto, (10, 5))

    def run(self):

        while not self.fin_juego:

            self.manejar_eventos()
            self.actualizar_movimiento()
            self.actualizar()
            self.dibujar()

            # 60 FPS
            self.reloj.tick(self.velocidad)


if __name__ == "__main__":
    juego = SnakeGame()
    juego.run()