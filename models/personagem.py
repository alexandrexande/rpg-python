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
    
    # ... (métodos anteriores)

    def ganhar_xp(self, quantidade: int) -> list[str]:
        """
        Adiciona XP e verifica se subiu de nível (pode subir múltiplos de uma vez).
        Retorna uma lista de mensagens de log.
        """
        self.xp += quantidade
        mensagens = []

        # Loop para caso ganhe muito XP e suba vários níveis
        while True:
            xp_necessario = self.nivel * 100
            
            if self.xp >= xp_necessario:
                self.xp -= xp_necessario
                self.nivel += 1
                self._aplicar_bonus_nivel()
                mensagens.append(f"SUBIU PARA O NÍVEL {self.nivel}!")
                mensagens.append(f"Status aumentados e Vida/Mana recuperados!")
            else:
                break
        
        return mensagens

    def _aplicar_bonus_nivel(self):
        """Define o quanto o personagem melhora a cada nível."""
        # Bônus fixos para simplificar (poderia variar por classe)
        inc_vida = 15
        inc_mana = 5
        inc_ataque = 2
        inc_defesa = 1

        self._atrib.vida_max += inc_vida
        self._atrib.mana += inc_mana  # Aumenta pool (opcional, ou só recupera)
        self._atrib.ataque += inc_ataque
        self._atrib.defesa += inc_defesa
        
        # Recuperação total ao subir de nível
        self._atrib.vida = self._atrib.vida_max
        
        # (Opcional) Se quiser que a mana encha também, descomente abaixo:
        # self._atrib.mana = 100 # ou algum teto máximo definido na classe

    # ... (restante do código, to_dict, from_dict, etc.)

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