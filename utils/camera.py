import msvcrt
import math

class Camera():

     def __init__(self,engine,fov,cam_x,cam_y,cam_z,cam_rot_x,cam_rot_y):

          self.fov = fov

          self.cam_x = cam_x
          self.cam_y = cam_y
          self.cam_z = cam_z

          self.cam_rot_x = cam_rot_x
          self.cam_rot_y = cam_rot_y

          self.velocidade = 0.3
          self.rot_speed = 0.02
          self.view = (0,0,-1)
          self.engine=engine

     def movimentacao(self):
          if not msvcrt.kbhit():
               return

          tecla = msvcrt.getch()

          if tecla == b'\x1b':   # ESC
               print("Saindo...")
               self.engine.mostrar_3d = False

          # direção da câmera
          dir_x = math.sin(self.cam_rot_y)
          dir_z = math.cos(self.cam_rot_y)

          # vetor lateral
          right_x = -dir_z
          right_z = dir_x

          # teclas especiais (setas)
          if tecla == b'\xe0':
               tecla = msvcrt.getch()

               if tecla == b'H':  # ↑ frente
                    self.cam_x += dir_x * self.velocidade
                    self.cam_z += dir_z * self.velocidade

               elif tecla == b'P':  # ↓ trás
                    self.cam_x -= dir_x * self.velocidade
                    self.cam_z -= dir_z * self.velocidade

               elif tecla == b'K':  # → direita
                    self.cam_x += right_x * self.velocidade
                    self.cam_z += right_z * self.velocidade

               elif tecla == b'M':  # ← esquerda
                    self.cam_x -= right_x * self.velocidade
                    self.cam_z -= right_z * self.velocidade

               return

          # teclas normais
          tecla = tecla.decode()

          if tecla == "w":
               self.cam_x += dir_x * self.velocidade
               self.cam_z += dir_z * self.velocidade

          elif tecla == "s":
               self.cam_x -= dir_x * self.velocidade
               self.cam_z -= dir_z * self.velocidade

          elif tecla == "d":
               self.cam_x -= right_x * self.velocidade
               self.cam_z -= right_z * self.velocidade

          elif tecla == "a":
               self.cam_x += right_x * self.velocidade
               self.cam_z += right_z * self.velocidade

          elif tecla == "q":
               self.cam_y += self.velocidade

          elif tecla == "e":
               self.cam_y -= self.velocidade

          elif tecla == "j":
               self.cam_rot_y -= self.rot_speed

          elif tecla == "l":
               self.cam_rot_y += self.rot_speed

          self.view = (
               math.sin(self.cam_rot_y),
               0,
               math.cos(self.cam_rot_y)
     )