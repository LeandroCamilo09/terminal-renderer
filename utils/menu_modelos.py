from utils.engine import Engine
import os
import msvcrt

class Menu():
    def __init__(self):
        self.pasta = "model_basicos"
        self.model_3d = ""
        self.run = True
        self.show_menu = True
        self.v = 0
        self.f = 0
        self.cache_info = {} # Cache para não reler arquivos

    def infor_modelo(self, path):
        # Verifica se já temos a info guardada
        if path in self.cache_info:
            self.v, self.f = self.cache_info[path]
            return

        self.v, self.f = 0, 0
        try:
            with open(path, "r") as file:
                for linha in file:
                    if linha.startswith("v "):
                        self.v += 1
                    elif linha.startswith("f "):
                        self.f += 1
            self.cache_info[path] = (self.v, self.f)
        except Exception:
            self.v, self.f = "Erro", "Erro"

    def highlight(self, text, width):
        texto_formatado = f"{text:<{width}}"
        return f"\033[48;2;70;70;160m{texto_formatado}\033[0m"

    def menu_modelos(self):
        if not os.path.exists(self.pasta):
            os.makedirs(self.pasta)
            
        modelos = [f for f in os.listdir(self.pasta) if f.endswith(".obj")]
        modelos.append("Carregar .obj externo...")  
        
        selecionado = 0
        ultimo_selecionado = -1
        self.model_3d=""
        while self.run:
            if self.show_menu:
                # Atualiza info apenas se a seleção mudou
                if selecionado != ultimo_selecionado:
                    if selecionado < len(modelos) - 1:
                        self.infor_modelo(os.path.join(self.pasta, modelos[selecionado]))
                    else:
                        self.v, self.f = 0, 0
                    ultimo_selecionado = selecionado

                saida = []
                saida.append("╔══════════════════════════════════════════════╗")
                saida.append("║      (^.^)/    TERMINAL RENDER               ║")
                saida.append("╠══════════════════════════════════════════════╣")
                saida.append("║                                              ║")

                for i, m in enumerate(modelos):
                    if i == selecionado:
                        # Chamamos o highlight passando o tamanho do campo
                        saida.append(f"║  ► {i+1}. {self.highlight(m, 37)}  ║")
                    else:
                        saida.append(f"║    {i+1}. {m:<37}  ║")

                saida.append("║______________________________________________║")
                saida.append(f"║   Vertices: {str(self.v):<10} | Faces: {str(self.f):<10}   ║")
                saida.append("║______________________________________________║")
                saida.append("║  W/S ou ↑↓ | Mover                           ║")
                saida.append("║  ENTER     | Carregar Modelo                 ║")
                saida.append("║  ESC       | Sair                            ║")
                saida.append("╚══════════════════════════════════════════════╝")

                print("\033[H" + "\n".join(saida))

                tecla = msvcrt.getch()
                if tecla == b'\xe0': # Setas
                    tecla = msvcrt.getch()
                    if tecla == b'H': selecionado = (selecionado - 1) % len(modelos)
                    elif tecla == b'P': selecionado = (selecionado + 1) % len(modelos)
                elif tecla == b'w': selecionado = (selecionado - 1) % len(modelos)
                elif tecla == b's': selecionado = (selecionado + 1) % len(modelos)
                elif tecla == b'\x1b': exit()
                elif tecla == b'\r':  # ENTER
                    if selecionado < len(modelos) - 1:
                        self.model_3d = os.path.join(self.pasta, modelos[selecionado])
                        self.show_menu = False
                    else:
                        print("\n Abrindo seletor de arquivos...") 
                        import tkinter as tk
                        from tkinter import filedialog
                        root = tk.Tk()
                        root.withdraw() # Esconde a janela principal do Tkinter
                        root.attributes("-topmost", True) # Força a janela a ficar na frente de tudo
                        arquivo = filedialog.askopenfilename(filetypes=[("Modelos 3D", "*.obj")])
                        root.destroy() # Fecha a instância do Tkinter após o uso
                        self.model_3d = arquivo
                        self.show_menu = False
            else:
                engine = Engine(self.model_3d, self)
                engine.mostrar_3d = True
                engine.run()
                if not engine.mostrar_3d:
                    self.show_menu = True
                    print("\033[2J", end="") # Limpa tela ao voltar