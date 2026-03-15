class World():
     def __init__(self,largura,altura):
          self.chars = " .,:;irsXA253hMHGS#9B&@"
          self.largura = largura
          self.altura = altura
          self.buffer = [" "] * (self.largura * self.altura)
          # Luz vindo de cima, direita e frente (estática)
          self.luz_estatica= (-1.0, 1.5, 1.0)
          self.luz_ambiente= 0.15
          self.zbuffer = [[float("inf") for x in range(self.largura)] for y in range(self.altura)]
          self.aspecto_terminal = 2.0 # Compensa a altura do caractere