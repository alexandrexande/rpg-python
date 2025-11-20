from __future__ import annotations
import random
from .base import Entidade, Atributos
from .item import Equipamento, Consumivel

class Inimigo(Entidade):
    def __init__(self, nome: str, vida: int, ataque: int, defesa: int):
        super().__init__(nome, Atributos(vida=vida, ataque=ataque, defesa=defesa, vida_max=vida))
        self.xp_recompensa = 0 
        self.loot_especifico = [] # Lista de itens possíveis

    def realizar_acao(self) -> tuple[int, str]:
        """Decide se ataca normal ou usa habilidade."""
        # 25% de chance de usar habilidade especial em inimigos comuns
        if random.random() < 0.25:
            return self.habilidade_especial()
        return self.atacar(), "atacou normalmente"

    def habilidade_especial(self) -> tuple[int, str]:
        """Sobrescrito pelas subclasses."""
        return self.atacar(), "tentou algo mas falhou"

    def gerar_loot(self) -> list:
        """Gera loot baseado na tabela da criatura."""
        drops = []
        if random.random() < 0.4: # 40% de chance de drop genérico
            drops.append(Consumivel("Poção Pequena", "vida", 20))
        
        # Chance de drop raro específico
        if self.loot_especifico and random.random() < 0.2:
            item = random.choice(self.loot_especifico)
            drops.append(item)
            
        return drops

# ==============================================================================
# ÁREA 1: FLORESTA (Clássicos)
# ==============================================================================

class Goblin(Inimigo):
    def __init__(self):
        super().__init__("Goblin Saqueador", 35, 9, 1)
        self.xp_recompensa = 40
        self.loot_especifico = [Equipamento("Adaga Enferrujada", "arma", ataque=4)]

    def habilidade_especial(self):
        return int(self._atrib.ataque * 1.5), "usou Ataque Sorrateiro!"

class Lobo(Inimigo):
    def __init__(self):
        super().__init__("Lobo Selvagem", 55, 12, 2)
        self.xp_recompensa = 60

    def habilidade_especial(self):
        return int(self._atrib.ataque * 1.2) + 5, "usou Mordida Crítica!"

class Orc(Inimigo):
    def __init__(self):
        super().__init__("Orc Guerreiro", 90, 16, 5)
        self.xp_recompensa = 110
        self.loot_especifico = [Equipamento("Machado de Orc", "arma", ataque=12)]

    def habilidade_especial(self):
        return int(self._atrib.ataque * 2), "usou Esmagar Crânio!"

class ReiOgro(Inimigo): # CHEFE
    def __init__(self):
        super().__init__("Rei dos Ogros", 250, 28, 10)
        self.xp_recompensa = 600
        self.loot_especifico = [Equipamento("Clava do Rei", "arma", ataque=25)]

    def realizar_acao(self):
        # PASSIVA: Fúria (Dano aumenta quando HP < 50%)
        fator_furia = 1.0
        if self._atrib.vida < (self._atrib.vida_max / 2):
            fator_furia = 1.3

        dano_base = int(self._atrib.ataque * fator_furia)
        
        roll = random.random()
        if roll < 0.2: # Skill 1
            return int(35 * fator_furia), "usou Pisotão Sísmico (Area)!"
        elif roll < 0.4: # Skill 2
            return int(45 * fator_furia), "lançou uma Rocha Gigante!"
        else:
            msg = "atacou furiosamente!" if fator_furia > 1 else "atacou com sua clava"
            return dano_base, msg

# ==============================================================================
# ÁREA 2: TRILHA (Humanoides/Bandidos)
# ==============================================================================

class Ladrao(Inimigo):
    def __init__(self):
        super().__init__("Ladrão de Estrada", 45, 14, 2)
        self.xp_recompensa = 55
        self.loot_especifico = [Consumivel("Elixir de Agilidade", "mana", 30)]

    def habilidade_especial(self):
        return int(self._atrib.ataque) + 10, "usou Golpe nas Costas!"

class Cacador(Inimigo):
    def __init__(self):
        super().__init__("Caçador de Recompensas", 70, 18, 6)
        self.xp_recompensa = 90
        self.loot_especifico = [Equipamento("Capa de Viagem", "armadura", defesa=5)]

    def habilidade_especial(self):
        return 25, "disparou Tiro na Perna!"

class Elfo(Inimigo):
    def __init__(self):
        super().__init__("Patrulheiro Elfo", 60, 20, 3)
        self.xp_recompensa = 100
        self.loot_especifico = [Equipamento("Arco Elfico", "arma", ataque=15)]

    def habilidade_especial(self):
        return 30, "lançou Flecha Encantada!"

class EnviadoCacada(Inimigo): # CHEFE
    def __init__(self):
        super().__init__("Enviado da Caçada Selvagem", 220, 35, 8)
        self.xp_recompensa = 700
        self.loot_especifico = [Equipamento("Lança Espectral", "arma", ataque=30)]
        self.turnos = 0

    def realizar_acao(self):
        self.turnos += 1
        # PASSIVA: Ganha ataque a cada turno (Acumulativo)
        bonus_passiva = self.turnos * 2 
        
        roll = random.random()
        if roll < 0.3: # Skill 1
            return 40 + bonus_passiva, "invocou Mastins Fantasmas!"
        elif roll < 0.5: # Skill 2
            return 50 + bonus_passiva, "executou o Julgamento Final!"
        
        return self.atacar() + bonus_passiva, "atacou com precisão sobrenatural"

# ==============================================================================
# ÁREA 3: CAVERNA (Monstros Subterrâneos)
# ==============================================================================

class MorcegoGigante(Inimigo):
    def __init__(self):
        super().__init__("Morcego Gigante", 40, 12, 0)
        self.xp_recompensa = 50

    def habilidade_especial(self):
        self._atrib.vida += 10
        return 15, "usou Drenar Sangue (Curou 10 HP)!"

class Gargula(Inimigo):
    def __init__(self):
        super().__init__("Gárgula de Pedra", 80, 15, 15) # Muita defesa
        self.xp_recompensa = 100
        self.loot_especifico = [Equipamento("Elmo de Pedra", "armadura", defesa=10)]

    def habilidade_especial(self):
        return 25, "caiu em Investida Aérea!"

class Kobold(Inimigo):
    def __init__(self):
        super().__init__("Kobold Mineiro", 30, 10, 2)
        self.xp_recompensa = 35
        self.loot_especifico = [Consumivel("Bomba de Fumaça", "vida", -5)] # Item troll ou útil?

    def habilidade_especial(self):
        return 20, "jogou uma picareta!"

class VermeColossal(Inimigo): # CHEFE
    def __init__(self):
        super().__init__("Verme Colossal", 400, 20, 5) # Muito HP
        self.xp_recompensa = 800
        self.loot_especifico = [Equipamento("Placa Quitina", "armadura", defesa=18)]

    def realizar_acao(self):
        # PASSIVA: Regeneração constante
        cura = 15
        if self._atrib.vida < self._atrib.vida_max:
            self._atrib.vida += cura
            print(f"\033[90m(O Verme regenerou {cura} HP na escuridão...)\033[0m")

        roll = random.random()
        if roll < 0.3: # Skill 1
            return 40, "causou um Terremoto Subterrâneo!"
        elif roll < 0.5: # Skill 2
            return 60, "tentou Engolir por Inteiro!"
        
        return self.atacar(), "mordeu brutalmente"

# ==============================================================================
# ÁREA 4: RUÍNAS (Mortos-Vivos)
# ==============================================================================

class SoldadoZumbi(Inimigo):
    def __init__(self):
        super().__init__("Soldado Zumbi", 60, 10, 5)
        self.xp_recompensa = 70
        self.loot_especifico = [Equipamento("Espada Antiga", "arma", ataque=8)]

    def habilidade_especial(self):
        return 15, "usou Mordida Infectada (Dano Venenoso)!"

class Ghoul(Inimigo):
    def __init__(self):
        super().__init__("Ghoul Devorador", 70, 18, 3)
        self.xp_recompensa = 90

    def habilidade_especial(self):
        return 25, "entrou em Frenesi Sangrento!"

class EspiritoSombrio(Inimigo):
    def __init__(self):
        super().__init__("Espírito Sombrio", 40, 25, 0) # Vidro canhão (muito dano, pouca vida)
        self.xp_recompensa = 110
        self.loot_especifico = [Consumivel("Essência de Mana", "mana", 50)]

    def habilidade_especial(self):
        return 35, "soltou um Grito da Morte!"

class Lich(Inimigo): # CHEFE
    def __init__(self):
        super().__init__("Arquimago Lich", 300, 40, 10)
        self.xp_recompensa = 1000
        self.loot_especifico = [Equipamento("Cajado do Vazio", "arma", ataque=40)]

    def realizar_acao(self):
        roll = random.random()
        dano_causado = 0
        msg = ""

        if roll < 0.3: # Skill 1
            dano_causado = 60
            msg = "lançou Raio da Morte!"
        elif roll < 0.5: # Skill 2
            dano_causado = 45
            msg = "invocou uma Chuva de Meteoros Sombrios!"
        else:
            dano_causado = self.atacar()
            msg = "disparou um raio arcano"

        # PASSIVA: Roubo de Vida (Lifesteal)
        cura = int(dano_causado * 0.2) # Cura 20% do dano causado
        self._atrib.vida = min(self._atrib.vida_max, self._atrib.vida + cura)
        if cura > 0:
            msg += f" (Drenou {cura} HP)"
        
        return dano_causado, msg