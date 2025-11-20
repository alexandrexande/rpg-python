from __future__ import annotations
import random
from .base import Entidade, Atributos

class Personagem(Entidade):
    """
    Classe base do jogador. Define a estrutura, mas deixa
    os detalhes de implementação para as subclasses.
    """
    def __init__(self, nome: str, atrib: Atributos):
        super().__init__(nome, atrib)
        self.nivel = 1
        self.xp = 0

    def calcular_dano_base(self) -> int:
        # Variação simples de +/- 10% no ataque
        base = self._atrib.ataque
        return int(base * random.uniform(0.9, 1.1))

    def habilidade_especial(self) -> tuple[int, str]:
        """
        Retorna (dano_causado, mensagem_descritiva).
        Se falhar (sem mana), retorna (0, mensagem_erro).
        """
        raise NotImplementedError("Subclasses devem implementar isso.")

# --- Subclasses (Arquétipos) ---

class Guerreiro(Personagem):
    def __init__(self, nome: str):
        # Guerreiro: Muita vida, boa defesa, pouca mana
        atributos = Atributos(vida=120, ataque=15, defesa=5, mana=20)
        super().__init__(nome, atributos)

    def habilidade_especial(self) -> tuple[int, str]:
        custo = 10
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            dano = int(self._atrib.ataque * 2.0) # Golpe Pesado
            return dano, f"usou 'Golpe Devastador' (Custo: {custo} MP)!"
        return 0, "não tem mana suficiente para o Golpe Devastador."

class Mago(Personagem):
    def __init__(self, nome: str):
        # Mago: Pouca vida, ataque físico fraco, muita mana
        atributos = Atributos(vida=70, ataque=5, defesa=2, mana=100)
        super().__init__(nome, atributos)

    def habilidade_especial(self) -> tuple[int, str]:
        custo = 25
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            dano = 40 # Dano mágico fixo alto
            return dano, f"lançou 'Bola de Fogo' (Custo: {custo} MP)!"
        return 0, "está sem mana para a magia."

class Arqueiro(Personagem):
    def __init__(self, nome: str):
        # Arqueiro: Equilibrado
        atributos = Atributos(vida=90, ataque=12, defesa=3, mana=40)
        super().__init__(nome, atributos)

    def habilidade_especial(self) -> tuple[int, str]:
        custo = 15
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            dano = int(self._atrib.ataque * 1.5) + 10
            return dano, f"disparou uma 'Flecha Precisa' (Custo: {custo} MP)!"
        return 0, "não tem foco (mana) para o tiro preciso."