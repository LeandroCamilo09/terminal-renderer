from utils.carregar_modelo_3d import carregar_obj, carregar_mtl,cor_ansi, vivificar_cor
from utils.camera import Camera
from utils.world import World
import math
import time
import os
import ctypes
import sys

class Engine():
    def __init__(self, model_3d="model_basicos/model_3d.obj", menu=any):
        self.mostrar_3d = False
        self.model_3d = model_3d
        self.menu = menu
        self.camera = Camera(self,500,0,-.5,-20,0,0)
        self.world = World(80,40)
        self.materiais_do_3d = carregar_mtl(self.model_3d)
        self.vertices, self.triangulos, self.face_materiais, _ = carregar_obj(self.model_3d)

    def run(self):
        # Habilita o processamento de sequências ANSI no Windows
        if os.name == 'nt':
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

        global angulox,anguloy,anguloz
        print("\033[2J")
        angulox = 0
        anguloy = 0
        anguloz = 4*0.785398        
        while(self.mostrar_3d):
            pontos2d= []
            pontosz= []
            pontos3d = []
            pontos_brilho = []

            norma = math.sqrt(sum(i**2 for i in self.world.luz_estatica))
            luz = [i/norma for i in self.world.luz_estatica]

            # Movimentação de câmera
            self.camera.movimentacao()

            self.limpar_tela()
            for v in self.vertices:
                x,y,z= self.rotacao(v[0],v[1],v[2],angulox,anguloy,anguloz)

                # posição relativa à câmera
                x -= self.camera.cam_x
                y -= self.camera.cam_y
                z -= self.camera.cam_z

                # rotação da câmera (Y)
                cosy = math.cos(-self.camera.cam_rot_y)
                siny = math.sin(-self.camera.cam_rot_y)

                x,z = (
                    x*cosy - z*siny,
                    x*siny + z*cosy
                )

                pontos3d.append((x,y,z))

                nx,ny,nz = x,y,z
                norma = math.sqrt(nx*nx + ny*ny + nz*nz)
                if norma != 0:
                    nx/=norma
                    ny/=norma
                    nz/=norma
                
                brilho = self.world.luz_ambiente + (1.0-self.world.luz_ambiente)*max(0,self.dot((nx,ny,nz),luz))
                pontos_brilho.append(brilho)

                x2d,y2d = self.projetar(x,y,z)
                pontos2d.append((x2d,y2d))
                pontosz.append(z)
            
            for i,t in enumerate(self.triangulos):
                i1,i2,i3 = t
                x1,y1 = pontos2d[i1]
                x2,y2 = pontos2d[i2]
                x3,y3 = pontos2d[i3]

                z1 = pontosz[i1]
                z2 = pontosz[i2]
                z3 = pontosz[i3]

                b1 = pontos_brilho[i1]
                b2 = pontos_brilho[i2]
                b3 = pontos_brilho[i3]

                if z1 < 0.1 or z2 < 0.1 or z3 < 0.1:
                    continue
                # --------------------
                mat_nome = self.face_materiais[i]
                cor_mtl = self.materiais_do_3d.get(mat_nome, {"Kd":(0.8,0.8,0.8)})["Kd"]
                # 1. PASSA A COR PELO FILTRO
                cor_viva = vivificar_cor(cor_mtl[0], cor_mtl[1], cor_mtl[2], mat_nome)

                p1 = pontos3d[i1]
                p2 = pontos3d[i2]
                p3 = pontos3d[i3]

                nx,ny,nz = self.normal(p1,p2,p3)

                comprimento = math.sqrt(nx*nx + ny*ny + nz*nz)
                if comprimento == 0:
                    continue

                nx/=comprimento
                ny/=comprimento
                nz/=comprimento
                vx = -p1[0]
                vy = -p1[1]
                vz = -p1[2]
                
                if self.dot((nx,ny,nz),(vx,vy,vz)) >= 0:
                    continue

                difusa = max(0, self.dot((nx,ny,nz), luz))

                view_dot = max(0, self.dot((nx,ny,nz), self.camera.view))
                fresnel = (1 - view_dot) ** 2

                brilho = self.world.luz_ambiente + 0.75*difusa + 0.25*fresnel
                brilho = min(1.0, brilho)
                r = int(cor_viva[0] * 255 * brilho)
                g = int(cor_viva[1] * 255 * brilho)
                b = int(cor_viva[2] * 255 * brilho)
                
                index = max(0, min(len(self.world.chars)-1, int(brilho*(len(self.world.chars)-1))))
                char = cor_ansi(r,g,b,self.world.chars[index])

                
                self.desenhar_triangulo_scanline(
                    x1,y1,z1,b1,
                    x2,y2,z2,b2,
                    x3,y3,z3,b3,
                    char    
                )
            
            print("\033[H", end="")
            self.desenhar()
            anguloy += 0.05
            time.sleep(0.016)

        self.menu.show_menu = True
        return self.menu.show_menu

    def desenhar(self):
        saida = "\n".join(
            "".join(buffer[y*self.world.largura:(y+1)*self.world.largura])
            for y in range(self.world.altura)
        )
        sys.stdout.write(saida)

    def projetar(self,x,y,z):
        if z == 0:
            z = 0.0001

        fator = self.camera.fov / z
        x2d = int(x * fator * self.world.aspecto_terminal + self.world.largura*0.5)
        y2d = int(y * fator + self.world.altura/2) 

        return x2d, y2d

    def pixel(self,x,y,z,char="█"):
        if 0 <= x < self.world.largura and 0 <= y < self.world.altura:
            if z < zbuffer[y][x]:
                zbuffer[y][x] = z
                buffer[y*self.world.largura + x] = char

    def limpar_tela(self):
        global buffer, zbuffer
        buffer = [" "] * (self.world.largura *self.world.altura)
        zbuffer = [[float("inf") for x in range(self.world.largura)] for y in range(self.world.altura)]

    def rotacao(self,x,y,z,ax,ay,az):
        # ROTACAO X
        cosx = math.cos(ax)
        sinx = math.sin(ax)

        y,z = (
            y*cosx - z*sinx,
            y*sinx + z*cosx
        )

        # ROTACAO Y
        cosy = math.cos(ay)
        siny = math.sin(ay)

        x,z = (
            x*cosy + z*siny,
            -x*siny + z*cosy
        )

        # ROTACAO Z
        cosz = math.cos(az)
        sinz = math.sin(az)

        x,y = (
            x*cosz - y*sinz,
            x*sinz + y*cosz
        )
        return x,y,z
    def interp(self,y, y0, x0, y1, x1):
            if y1 == y0:
                return x0
            return x0 + (x1-x0)*(y-y0)/(y1-y0)
    def desenhar_triangulo_scanline(self,x1,y1,z1,b1,
                        x2,y2,z2,b2,
                        x3,y3,z3,b3, char_base):
        # Ordena os vértices pelo Y
        pontos = sorted([
        (x1,y1,z1,b1),
        (x2,y2,z2,b2),
        (x3,y3,z3,b3)
        ], key=lambda p: p[1])

        (x1,y1,z1,b1),(x2,y2,z2,b2),(x3,y3,z3,b3) = pontos

        y1,y2,y3 = int(y1), int(y2), int(y3)
        
        for y in range(y1, y3+1):

            if y < y2:
                xa = self.interp(y,y1,x1,y2,x2)
                za = self.interp(y,y1,z1,y2,z2)
                ba = self.interp(y,y1,b1,y2,b2)
            else:
                xa = self.interp(y,y2,x2,y3,x3)
                za = self.interp(y,y2,z2,y3,z3)
                ba = self.interp(y,y2,b2,y3,b3)

            xb = self.interp(y,y1,x1,y3,x3)
            zb = self.interp(y,y1,z1,y3,z3)
            bb = self.interp(y,y1,b1,y3,b3)

            if xa > xb:
                xa,xb = xb,xa
                za,zb = zb,za
                ba,bb = bb,ba   

            for x in range(int(xa), int(xb)+1):

                if xb-xa == 0:
                    z = za
                    b = ba
                else:
                    t = (x-xa)/(xb-xa)
                    z = za + (zb-za)*t
                    b = ba + (bb-ba)*t

                self.pixel(x,y,z,char_base)

    def normal(self,p1,p2,p3):
                x1,y1,z1 = p1
                x2,y2,z2 = p2
                x3,y3,z3 = p3

                ux,uy,uz = x2-x1, y2-y1, z2-z1
                vx,vy,vz = x3-x1, y3-y1, z3-z1  

                nx = uy*vz - uz*vy
                ny = uz*vx - ux*vz
                nz = ux*vy - uy*vx

                return nx,ny,nz

    def dot(self,a,b):
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]