from __future__ import annotations
import random
from .base import Entidade, Atributos
from .item import Equipamento, Consumivel

class Personagem(Entidade):
    def __init__(self, nome: str, atrib: Atributos):
        super().__init__(nome, atrib)
        self.nivel = 1
        self.xp = 0
        
        # --- NOVO: Inventário e Equipamentos ---
        self.inventario: list[Consumivel | Equipamento] = []
        self.equipamentos: dict[str, Equipamento | None] = {
            "arma": None,
            "armadura": None
        }

    # --- Propriedades de Combate (Soma Base + Equipamento) ---
    @property
    def ataque_total(self) -> int:
        base = self._atrib.ataque
        bonus = 0
        if self.equipamentos["arma"]:
            bonus += self.equipamentos["arma"].ataque_bonus
        if self.equipamentos["armadura"]: # Algumas armaduras podem dar ataque
            bonus += self.equipamentos["armadura"].ataque_bonus
        return base + bonus

    @property
    def defesa_total(self) -> int:
        base = self._atrib.defesa
        bonus = 0
        if self.equipamentos["armadura"]:
            bonus += self.equipamentos["armadura"].defesa_bonus
        if self.equipamentos["arma"]:
            bonus += self.equipamentos["arma"].defesa_bonus
        return base + bonus

    # --- Métodos de Ação ---

    def calcular_dano_base(self) -> int:
        # Agora usa o ataque_total (com arma)
        return int(self.ataque_total * random.uniform(0.9, 1.1))

    def receber_dano(self, dano: int) -> int:
        # Agora usa defesa_total (com armadura)
        efetivo = max(0, dano - self.defesa_total)
        self._atrib.vida = max(0, self._atrib.vida - efetivo)
        return efetivo

    def curar(self, valor: int) -> int:
        """Recupera vida sem passar do máximo."""
        vida_antiga = self._atrib.vida
        self._atrib.vida = min(self._atrib.vida_max, self._atrib.vida + valor)
        return self._atrib.vida - vida_antiga

    def equipar_item(self, item: Equipamento):
        if item not in self.inventario:
            return
        
        # Se já tem algo equipado, desequipa (volta pro inventário)
        atual = self.equipamentos.get(item.slot)
        if atual:
            self.inventario.append(atual)
        
        # Equipa o novo e remove do inventário
        self.equipamentos[item.slot] = item
        self.inventario.remove(item)
        print(f"Você equipou: {item.nome}")

    def habilidade_especial(self) -> tuple[int, str]:
        raise NotImplementedError("Subclasses devem implementar.")

    # --- Lógica de Level Up (Mantida igual) ---
    def ganhar_xp(self, quantidade: int) -> list[str]:
        self.xp += quantidade
        mensagens = []
        while True:
            xp_nec = self.nivel * 100
            if self.xp >= xp_nec:
                self.xp -= xp_nec
                self.nivel += 1
                self._aplicar_bonus_nivel()
                mensagens.append(f"SUBIU PARA O NÍVEL {self.nivel}!")
            else:
                break
        return mensagens

    def _aplicar_bonus_nivel(self):
        self._atrib.vida_max += 15
        self._atrib.mana += 5
        self._atrib.ataque += 2
        self._atrib.defesa += 1
        self._atrib.vida = self._atrib.vida_max

    # --- Persistência (Atualizada para salvar itens) ---

    def to_dict(self) -> dict:
        # Helper para salvar itens
        def salvar_item(item):
            if not item: return None
            tipo = "equip" if isinstance(item, Equipamento) else "pot"
            dados = item.__dict__.copy()
            dados["classe_item"] = tipo
            return dados

        return {
            "classe": self.__class__.__name__,
            "nome": self.nome,
            "nivel": self.nivel,
            "xp": self.xp,
            "atributos": self._atrib.__dict__,
            "inventario": [salvar_item(i) for i in self.inventario],
            "equipamentos": {k: salvar_item(v) for k, v in self.equipamentos.items()}
        }

    @staticmethod
    def from_dict(dados: dict) -> Personagem:
        classe_nome = dados.get("classe")
        nome = dados.get("nome")
        
        # Instanciação (Factory)
        if classe_nome == "Guerreiro": p = Guerreiro(nome)
        elif classe_nome == "Mago": p = Mago(nome)
        elif classe_nome == "Arqueiro": p = Arqueiro(nome)
        else: p = Guerreiro(nome)
        
        p.nivel = dados.get("nivel", 1)
        p.xp = dados.get("xp", 0)
        
        ats = dados.get("atributos", {})
        p._atrib.vida = ats.get("vida", 100)
        p._atrib.vida_max = ats.get("vida_max", 100)
        p._atrib.ataque = ats.get("ataque", 10)
        p._atrib.defesa = ats.get("defesa", 0)
        p._atrib.mana = ats.get("mana", 0)

        # Reconstrói Itens
        def carregar_item(d):
            if not d: return None
            tipo = d.pop("classe_item", "pot")
            if tipo == "equip":
                # Filtra chaves extras se houver
                return Equipamento(d["nome"], d["slot"], d["ataque_bonus"], d["defesa_bonus"])
            else:
                return Consumivel(d["nome"], d["tipo"], d["valor_efeito"])

        inv_dados = dados.get("inventario", [])
        p.inventario = [carregar_item(i) for i in inv_dados]
        
        eq_dados = dados.get("equipamentos", {})
        p.equipamentos["arma"] = carregar_item(eq_dados.get("arma"))
        p.equipamentos["armadura"] = carregar_item(eq_dados.get("armadura"))
        
        return p

# --- Subclasses (Mantidas idênticas, apenas copie-as do arquivo anterior) ---
class Guerreiro(Personagem):
    def __init__(self, nome): super().__init__(nome, Atributos(120, 15, 5, 20))
    def habilidade_especial(self): 
        if self._atrib.mana >= 10:
            self._atrib.mana -= 10
            return int(self.ataque_total * 2), "usou Golpe Devastador!" 
        return 0, "sem mana."

class Mago(Personagem):
    def __init__(self, nome): super().__init__(nome, Atributos(70, 5, 2, 100))
    def habilidade_especial(self):
        if self._atrib.mana >= 25:
            self._atrib.mana -= 25
            return 40, "lançou Bola de Fogo!"
        return 0, "sem mana."

class Arqueiro(Personagem):
    def __init__(self, nome): super().__init__(nome, Atributos(90, 12, 3, 40))
    def habilidade_especial(self):
        if self._atrib.mana >= 15:
            self._atrib.mana -= 15
            return int(self.ataque_total * 1.5)+10, "disparou Flecha Precisa!"
        return 0, "sem mana."