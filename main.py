# Importações principais do Kivy e módulos gráficos
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Ellipse, Rectangle, Color

# Classe que representa a bola do jogo
class PongBall(Widget):
    # Propriedades de velocidade nos eixos X e Y
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    # Combinação das velocidades em um vetor
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30)  # Define o tamanho da bola
        self.draw()  # Desenha a bola

    # Atualiza a posição da bola com base na velocidade
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    # Desenha a bola na tela
    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)  # Cor branca
            Ellipse(pos=self.pos, size=self.size)


# Classe que representa uma raquete
class PongPaddle(Widget):
    score = NumericProperty(0)  # Pontuação do jogador
    paddle_color = ListProperty([1, 1, 1])  # Cor da raquete

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (25, 150)  # Tamanho da raquete
        self.draw()  # Desenha a raquete

    # Verifica colisão entre a raquete e a bola e altera a direção
    def bounce_ball(self, ball):
        if self.collide_widget(ball):  # Se colidiu
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)  # Calcula desvio
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1  # Aumenta a velocidade
            ball.velocity = vel.x, vel.y + offset  # Aplica nova velocidade

    # Desenha a raquete com a cor definida
    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(*self.paddle_color)
            Rectangle(pos=self.pos, size=self.size)


# Classe principal do jogo
class PongGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Desenha fundo cinza
        with self.canvas.before:
            Color(0.5, 0.5, 0.5)
            self.bg = Rectangle(pos=self.pos, size=self.size)

        # Instancia os objetos do jogo
        self.ball = PongBall()
        self.player1 = PongPaddle()
        self.player2 = PongPaddle()

        # Labels do placar dos jogadores
        self.score1_label = Label(text="0", font_size=40, color=(1, 1, 1, 1))
        self.score2_label = Label(text="0", font_size=40, color=(1, 1, 1, 1))

        # Adiciona os objetos na tela
        self.add_widget(self.ball)
        self.add_widget(self.player1)
        self.add_widget(self.player2)
        self.add_widget(self.score1_label)
        self.add_widget(self.score2_label)

        # Captura teclado
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Define cores das raquetes
        self.player1.paddle_color = [1, 0, 0]  # Vermelho
        self.player2.paddle_color = [0, 0, 1]  # Azul

        self.on_size()  # Inicializa posicionamento

    # Fecha o controle do teclado
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    # Define os controles do teclado
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'w':  # Jogador 1 sobe
            self.player1.center_y += 20
            self.player1.draw()
        elif keycode[1] == 's':  # Jogador 1 desce
            self.player1.center_y -= 20
            self.player1.draw()
        elif keycode[1] == 'up':  # Jogador 2 sobe
            self.player2.center_y += 20
            self.player2.draw()
        elif keycode[1] == 'down':  # Jogador 2 desce
            self.player2.center_y -= 20
            self.player2.draw()
        return True

    # Inicializa a bola no centro com velocidade
    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel
        self.ball.draw()

    # Atualiza o estado do jogo
    def update(self, dt):
        self.ball.move()
        self.ball.draw()

        # Rebater nas paredes superior e inferior
        if self.ball.y < 0 or self.ball.top > self.height:
            self.ball.velocity_y *= -1

        # Verifica colisão com as raquetes
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # Se a bola passar do jogador 1, ponto para jogador 2
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))

        # Se a bola passar do jogador 2, ponto para jogador 1
        elif self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

        # Atualiza texto do placar
        self.score1_label.text = str(self.player1.score)
        self.score2_label.text = str(self.player2.score)

    # Redimensionamento e reposicionamento
    def on_size(self, *args):
        # Atualiza fundo
        self.bg.pos = self.pos
        self.bg.size = self.size

        # Posiciona jogadores e bola
        self.player1.center = (self.width * 0.05, self.center_y)
        self.player2.center = (self.width * 0.95, self.center_y)
        self.ball.center = self.center

        # Redesenha elementos
        self.player1.draw()
        self.player2.draw()
        self.ball.draw()

        # Posiciona os placares no topo da tela
        self.score1_label.center_x = self.width * 0.25
        self.score1_label.top = self.height - 10
        self.score2_label.center_x = self.width * 0.75
        self.score2_label.top = self.height - 10


# Classe principal do aplicativo Kivy
class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()  # Começa o jogo com a bola no centro
        Clock.schedule_interval(game.update, 1.0 / 60.0)  # Atualiza 60x por segundo
        return game


# Inicia o app
if __name__ == '__main__':
    PongApp().run()

