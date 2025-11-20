from __future__ import annotations
import random
from .base import Entidade, Atributos

class Personagem(Entidade):
    def __init__(self, nome: str, atrib: Atributos):
        super().__init__(nome, atrib)
        self.nivel = 1
        self.xp = 0

    def calcular_dano_base(self) -> int:
        base = self._atrib.ataque
        return int(base * random.uniform(0.9, 1.1))

    def habilidade_especial(self) -> tuple[int, str]:
        raise NotImplementedError("Subclasses devem implementar isso.")

    # --- NOVO: Métodos de Salvar/Carregar ---

    def to_dict(self) -> dict:
        """Converte o objeto Personagem em um dicionário simples."""
        return {
            "classe": self.__class__.__name__, # Salva "Guerreiro", "Mago", etc.
            "nome": self.nome,
            "nivel": self.nivel,
            "xp": self.xp,
            "atributos": {
                "vida": self._atrib.vida,
                "vida_max": self._atrib.vida_max,
                "ataque": self._atrib.ataque,
                "defesa": self._atrib.defesa,
                "mana": self._atrib.mana
            }
        }

    @staticmethod
    def from_dict(dados: dict) -> Personagem:
        """Reconstrói o objeto correto a partir do dicionário."""
        classe_nome = dados.get("classe")
        nome = dados.get("nome")
        
        # 1. Instancia a classe correta vazia ou inicial
        if classe_nome == "Guerreiro":
            p = Guerreiro(nome)
        elif classe_nome == "Mago":
            p = Mago(nome)
        elif classe_nome == "Arqueiro":
            p = Arqueiro(nome)
        else:
            # Fallback para Guerreiro se der erro
            p = Guerreiro(nome) 
        
        # 2. Restaura os dados salvos
        p.nivel = dados.get("nivel", 1)
        p.xp = dados.get("xp", 0)
        
        # 3. Restaura atributos exatos (vida atual, etc)
        ats = dados.get("atributos", {})
        p._atrib.vida = ats.get("vida", 100)
        p._atrib.vida_max = ats.get("vida_max", 100)
        p._atrib.ataque = ats.get("ataque", 10)
        p._atrib.defesa = ats.get("defesa", 0)
        p._atrib.mana = ats.get("mana", 0)
        
        return p


# --- Subclasses (Mantidas iguais, mas precisam estar aqui) ---

class Guerreiro(Personagem):
    def __init__(self, nome: str):
        atributos = Atributos(vida=120, ataque=15, defesa=5, mana=20)
        super().__init__(nome, atributos)

    def habilidade_especial(self) -> tuple[int, str]:
        custo = 10
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            dano = int(self._atrib.ataque * 2.0)
            return dano, f"usou 'Golpe Devastador' (Custo: {custo} MP)!"
        return 0, "não tem mana suficiente."

class Mago(Personagem):
    def __init__(self, nome: str):
        atributos = Atributos(vida=70, ataque=5, defesa=2, mana=100)
        super().__init__(nome, atributos)

    def habilidade_especial(self) -> tuple[int, str]:
        custo = 25
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            dano = 40 
            return dano, f"lançou 'Bola de Fogo' (Custo: {custo} MP)!"
        return 0, "está sem mana."

class Arqueiro(Personagem):
    def __init__(self, nome: str):
        atributos = Atributos(vida=90, ataque=12, defesa=3, mana=40)
        super().__init__(nome, atributos)

    def habilidade_especial(self) -> tuple[int, str]:
        custo = 15
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            dano = int(self._atrib.ataque * 1.5) + 10
            return dano, f"disparou uma 'Flecha Precisa' (Custo: {custo} MP)!"
        return 0, "não tem foco (mana)."