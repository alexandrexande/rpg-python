from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Item:
    nome: str
    valor: int # Preço de venda (futuro) ou raridade (depois faço a loja)

class Consumivel(Item):
    #Poções e itens de uso único.
    def __init__(self, nome: str, tipo: str, valor_efeito: int):
        super().__init__(nome, valor=10)
        self.tipo = tipo  # "vida" ou "mana"
        self.valor_efeito = valor_efeito # Quanto cura

    def usar(self, personagem) -> str:
        if self.tipo == "vida":
            cura = personagem.curar(self.valor_efeito)
            return f"Usou {self.nome} e recuperou {cura} HP."
        elif self.tipo == "mana":
            personagem._atrib.mana += self.valor_efeito
            return f"Usou {self.nome} e recuperou {self.valor_efeito} MP."
        return "Item sem efeito."

class Equipamento(Item):
    #Armas e Armaduras.
    def __init__(self, nome: str, slot: str, ataque: int = 0, defesa: int = 0):
        super().__init__(nome, valor=50)
        self.slot = slot # "arma" ou "armadura"
        self.ataque_bonus = ataque
        self.defesa_bonus = defesa