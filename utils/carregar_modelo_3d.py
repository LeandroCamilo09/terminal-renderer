import colorsys
import os
def carregar_obj(nome):

    vertices = []
    faces = []
    face_materiais = []
    materiais = {}
    material_atual = None

    with open(nome,"r") as f:
        for linha in f:

            if linha.startswith("usemtl"):
                material_atual = linha.split()[1]

            elif linha.startswith("v "):
                _,x,y,z = linha.split()
                vertices.append((float(x),float(y),float(z)))

            elif linha.startswith("f "):
                partes = linha.split()[1:]
                indices = []

                for p in partes:
                    i = int(p.split("/")[0]) - 1
                    indices.append(i)

                for i in range(1,len(indices)-1):
                    faces.append((indices[0],indices[i],indices[i+1]))
                    face_materiais.append(material_atual)

    return vertices, faces, face_materiais, materiais

import os

def carregar_mtl(nome):
    materiais = {}
    atual = None

    nome_ = os.path.splitext(nome)[0] + ".mtl"

    with open(nome_, "r") as f:
        for linha in f:

            if linha.startswith("newmtl"):
                atual = linha.split()[1]
                materiais[atual] = {"Kd": (1,1,1)}

            elif linha.startswith("Kd") and atual:
                _, r,g,b = linha.split()
                materiais[atual]["Kd"] = (float(r),float(g),float(b))

    return materiais

def cor_ansi(r, g, b, char):
    # Garante que r, g, b sejam inteiros entre 0 e 255
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"


def vivificar_cor(r, g, b, mat_nome=""):
    # Verifica se a cor é praticamente cinza (canais muito parecidos)
    if abs(r - g) < 0.05 and abs(g - b) < 0.05:
        # Pega o nome do material e gera um número único para ele
        hash_nome = sum(ord(c) for c in mat_nome)
        # Escolhe um Matiz (Hue) entre 0.0 e 1.0
        h = (hash_nome % 100) / 100.0
        s = 0.85 # Saturação alta
        v = max(0.5, r) # Mantém a claridade original
        # Converte HSV de volta para RGB
        return colorsys.hsv_to_rgb(h, s, v)

    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(1.0, s * 1.5) # Aumenta a saturação em 50%
    v = min(1.0, v * 1.2) # Aumenta o brilho em 20%
    
    return colorsys.hsv_to_rgb(h, s, v)