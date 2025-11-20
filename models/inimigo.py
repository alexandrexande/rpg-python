from __future__ import annotations
import random
from .base import Entidade, Atributos

class Inimigo(Entidade):
    def __init__(self, nome: str, vida: int, ataque: int, defesa: int):
        super().__init__(nome, Atributos(vida=vida, ataque=ataque, defesa=defesa, vida_max=vida))
        self.xp_recompensa = 0 # Definido nas subclasses

# --- Subclasses Específicas  ---

class Goblin(Inimigo):
    def __init__(self):
        super().__init__("Goblin Saqueador", vida=30, ataque=8, defesa=1)
        self.xp_recompensa = 50

class Lobo(Inimigo):
    def __init__(self):
        super().__init__("Lobo Selvagem", vida=50, ataque=12, defesa=2)
        self.xp_recompensa = 80

class Orc(Inimigo):
    def __init__(self):
        super().__init__("Orc Guerreiro", vida=80, ataque=15, defesa=4)
        self.xp_recompensa = 120

# --- Classe Chefão (Desafio Extra) [cite: 126] ---

class Chefao(Inimigo):
    def __init__(self):
        super().__init__("Rei dos Ogros", vida=200, ataque=25, defesa=8)
        self.xp_recompensa = 500
    
    def atacar(self) -> int:
        # O Chefão tem chance de crítico ou ataque especial
        if random.random() < 0.3: # 30% de chance de esmagar
            print("!!! O CHEFÃO PREPARA UM GOLPE ESMAGADOR !!!")
            return int(self._atrib.ataque * 1.5)
        return self._atrib.ataque