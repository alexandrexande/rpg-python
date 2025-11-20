from __future__ import annotations
import random
from .base import Entidade, Atributos
from .item import Equipamento, Consumivel

# --- TABELA DE PROGRESSÃO (LIVRO DE REGRAS) ---
# Define o que cada classe ganha em cada nível
ARVORE_EVOLUCAO = {
    "Guerreiro": {
        1:  {"tipo": "skill", "nome": "Golpe Devastador", "custo": 10, "desc": "Ataque pesado (200% ATK)."},
        5:  {"tipo": "passiva", "nome": "Pele de Ferro", "desc": "Reduz todo dano recebido em 15%."},
        10: {"tipo": "skill", "nome": "Grito de Guerra", "custo": 20, "desc": "Causa dano e recupera 20 HP."},
        15: {"tipo": "passiva", "nome": "Berserker", "desc": "Se HP < 30%, seu ataque dobra."},
        20: {"tipo": "skill", "nome": "Execução Final", "custo": 50, "desc": "Golpe massivo (400% ATK)."},
        "status_base": {"vida": 15, "mana": 5, "ataque": 2, "defesa": 1} # Ganho padrão por nível
    },
    "Mago": {
        1:  {"tipo": "skill", "nome": "Bola de Fogo", "custo": 25, "desc": "Dano mágico alto (40 fixo + 150% ATK)."},
        5:  {"tipo": "passiva", "nome": "Mente Clara", "desc": "Recupera 5 Mana por turno automaticamente."},
        10: {"tipo": "skill", "nome": "Raio Congelante", "custo": 40, "desc": "Dano alto + Chance de atordoar (turno perdido)."},
        15: {"tipo": "passiva", "nome": "Escudo Arcano", "desc": "Se Mana > 50%, ganha +5 Defesa extra."},
        20: {"tipo": "skill", "nome": "Meteoro", "custo": 100, "desc": "Destruição total em área (500% ATK)."},
        "status_base": {"vida": 8, "mana": 15, "ataque": 1, "defesa": 0}
    },
    "Arqueiro": {
        1:  {"tipo": "skill", "nome": "Flecha Precisa", "custo": 15, "desc": "Tiro focado (150% ATK + Crítico garantido)."},
        5:  {"tipo": "passiva", "nome": "Olhos de Águia", "desc": "Aumenta chance de crítico base em 20%."},
        10: {"tipo": "skill", "nome": "Chuva de Flechas", "custo": 30, "desc": "3 ataques rápidos de 70% ATK cada."},
        15: {"tipo": "passiva", "nome": "Evasão Ladina", "desc": "20% de chance de desviar completamente de um ataque."},
        20: {"tipo": "skill", "nome": "Flecha Fantasma", "custo": 60, "desc": "Ignora defesa do inimigo (300% Dano Real)."},
        "status_base": {"vida": 10, "mana": 8, "ataque": 3, "defesa": 1}
    }
}

class Personagem(Entidade):
    def __init__(self, nome: str, atrib: Atributos):
        super().__init__(nome, atrib)
        self.nivel = 1
        self.xp = 0
        
        self.inventario: list[Consumivel | Equipamento] = []
        self.equipamentos: dict[str, Equipamento | None] = {"arma": None, "armadura": None}
        
        # Novas listas para guardar o progresso
        self.habilidades_conhecidas: list[str] = [] 
        self.passivas_ativas: list[str] = []
        
        # Inicializa skill nível 1
        self._desbloquear_nivel(1, logs=False)

    # --- Propriedades de Combate ---
    @property
    def ataque_total(self) -> int:
        base = self._atrib.ataque
        bonus = 0
        if self.equipamentos["arma"]: bonus += self.equipamentos["arma"].ataque_bonus
        if self.equipamentos["armadura"]: bonus += self.equipamentos["armadura"].ataque_bonus
        
        # Passiva: Berserker (Guerreiro Lv 15)
        if "Berserker" in self.passivas_ativas and (self._atrib.vida < self._atrib.vida_max * 0.3):
            base *= 2
            
        return int(base + bonus)

    @property
    def defesa_total(self) -> int:
        base = self._atrib.defesa
        bonus = 0
        if self.equipamentos["armadura"]: bonus += self.equipamentos["armadura"].defesa_bonus
        if self.equipamentos["arma"]: bonus += self.equipamentos["arma"].defesa_bonus
        
        # Passiva: Escudo Arcano (Mago Lv 15)
        if "Escudo Arcano" in self.passivas_ativas and self._atrib.mana > 50:
            bonus += 5
            
        return base + bonus

    # --- Ações ---

    def calcular_dano_base(self) -> int:
        dano = self.ataque_total * random.uniform(0.9, 1.1)
        
        # Chance de Crítico Padrão (5%)
        chance_crit = 0.05
        # Passiva: Olhos de Águia (Arqueiro Lv 5)
        if "Olhos de Águia" in self.passivas_ativas:
            chance_crit += 0.20 # +20%
        
        if random.random() < chance_crit:
            print(f"\033[93mCRÍTICO! {self.nome} acertou um ponto vital!\033[0m")
            dano *= 1.5
            
        return int(dano)

    def receber_dano(self, dano: int) -> int:
        # Passiva: Evasão Ladina (Arqueiro Lv 15)
        if "Evasão Ladina" in self.passivas_ativas:
            if random.random() < 0.20: # 20% chance
                print(f"\033[94m{self.nome} DESVIOU do ataque com agilidade!\033[0m")
                return 0

        efetivo = max(0, dano - self.defesa_total)
        
        # Passiva: Pele de Ferro (Guerreiro Lv 5)
        if "Pele de Ferro" in self.passivas_ativas:
            efetivo = int(efetivo * 0.85) # Reduz 15%

        self._atrib.vida = max(0, self._atrib.vida - efetivo)
        return efetivo

    def curar(self, valor: int) -> int:
        vida_antiga = self._atrib.vida
        self._atrib.vida = min(self._atrib.vida_max, self._atrib.vida + valor)
        return self._atrib.vida - vida_antiga

    def equipar_item(self, item: Equipamento):
        if item not in self.inventario: return
        atual = self.equipamentos.get(item.slot)
        if atual: self.inventario.append(atual)
        self.equipamentos[item.slot] = item
        self.inventario.remove(item)
        print(f"Você equipou: {item.nome}")

    # --- Sistema de Level Up e Desbloqueio ---

    def ganhar_xp(self, quantidade: int) -> list[str]:
        self.xp += quantidade
        mensagens = []
        while True:
            xp_nec = self.nivel * 100
            if self.xp >= xp_nec:
                self.xp -= xp_nec
                self.nivel += 1
                msg_up = self._desbloquear_nivel(self.nivel)
                mensagens.append(f"SUBIU PARA O NÍVEL {self.nivel}!")
                mensagens.extend(msg_up)
            else:
                break
        return mensagens

    def _desbloquear_nivel(self, nivel: int, logs: bool = True) -> list[str]:
        msgs = []
        classe_nome = self.__class__.__name__
        dados_classe = ARVORE_EVOLUCAO.get(classe_nome, {})
        
        # 1. Aplica Status Base (Vida, Mana, etc)
        stats = dados_classe.get("status_base", {})
        self._atrib.vida_max += stats.get("vida", 10)
        self._atrib.mana += stats.get("mana", 5)
        self._atrib.ataque += stats.get("ataque", 1)
        self._atrib.defesa += stats.get("defesa", 0)
        self._atrib.vida = self._atrib.vida_max # Cura ao upar
        
        if logs:
            msgs.append(f"Atributos: +{stats['vida']} HP, +{stats['mana']} MP, +{stats['ataque']} Atk")

        # 2. Verifica recompensas especiais do nível (Skills/Passivas)
        recompensa = dados_classe.get(nivel)
        if recompensa:
            tipo = recompensa["tipo"]
            nome = recompensa["nome"]
            
            if tipo == "skill":
                if nome not in self.habilidades_conhecidas:
                    self.habilidades_conhecidas.append(nome)
                    if logs: msgs.append(f"NOVA HABILIDADE: [{nome}] - {recompensa['desc']}")
            
            elif tipo == "passiva":
                if nome not in self.passivas_ativas:
                    self.passivas_ativas.append(nome)
                    if logs: msgs.append(f"NOVA PASSIVA: [{nome}] - {recompensa['desc']}")
        
        return msgs

    # --- MENU DE HABILIDADES EM COMBATE ---
    def habilidade_especial(self) -> tuple[int, str]:
        """Exibe menu de seleção se houver mais de uma skill."""
        if not self.habilidades_conhecidas:
            return 0, "não conhece nenhuma habilidade."
        
        # Se tiver só 1 (nível baixo), usa direto
        if len(self.habilidades_conhecidas) == 1:
            return self._executar_skill(self.habilidades_conhecidas[0])
        
        # Se tiver várias, mostra menu
        print("\n--- Escolha sua Habilidade ---")
        
        # Acessa a tabela para pegar o custo de mana
        dados_classe = ARVORE_EVOLUCAO.get(self.__class__.__name__, {})
        
        # Precisamos achar o custo de cada skill na tabela
        # Como a tabela é por nível, faremos uma busca reversa rápida ou iteramos
        # Para simplificar, vou iterar os níveis conhecidos
        
        mapa_skills = []
        for lvl, info in dados_classe.items():
            if lvl == "status_base": continue
            if info["tipo"] == "skill" and info["nome"] in self.habilidades_conhecidas:
                mapa_skills.append(info)

        # Ordena por custo (opcional)
        mapa_skills.sort(key=lambda x: x["custo"])

        for i, skill in enumerate(mapa_skills):
            print(f"[{i+1}] {skill['nome']} (MP: {skill['custo']}) - {skill['desc']}")
        print("[0] Cancelar")
        
        try:
            op = int(input("> ")) - 1
            if 0 <= op < len(mapa_skills):
                nome_skill = mapa_skills[op]["nome"]
                return self._executar_skill(nome_skill)
            return 0, "cancelou a habilidade."
        except ValueError:
            return 0, "opção inválida."

    def _executar_skill(self, nome_skill: str) -> tuple[int, str]:
        """Roteador central que chama a lógica de cada classe."""
        # Chama o método específico na subclasse
        metodo_limpo = nome_skill.lower().replace(" ", "_")
        if hasattr(self, f"skill_{metodo_limpo}"):
            return getattr(self, f"skill_{metodo_limpo}")()
        return 0, "habilidade não implementada."

    # --- Persistência ---
    def to_dict(self) -> dict:
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
            "skills": self.habilidades_conhecidas, # Salva skills
            "passivas": self.passivas_ativas,      # Salva passivas
            "inventario": [salvar_item(i) for i in self.inventario],
            "equipamentos": {k: salvar_item(v) for k, v in self.equipamentos.items()}
        }

    @staticmethod
    def from_dict(dados: dict) -> Personagem:
        classe_nome = dados.get("classe")
        nome = dados.get("nome")
        
        if classe_nome == "Guerreiro": p = Guerreiro(nome)
        elif classe_nome == "Mago": p = Mago(nome)
        elif classe_nome == "Arqueiro": p = Arqueiro(nome)
        else: p = Guerreiro(nome)
        
        p.nivel = dados.get("nivel", 1)
        p.xp = dados.get("xp", 0)
        p.habilidades_conhecidas = dados.get("skills", [])
        p.passivas_ativas = dados.get("passivas", [])
        
        ats = dados.get("atributos", {})
        p._atrib.vida = ats.get("vida", 100)
        p._atrib.vida_max = ats.get("vida_max", 100)
        p._atrib.ataque = ats.get("ataque", 10)
        p._atrib.defesa = ats.get("defesa", 0)
        p._atrib.mana = ats.get("mana", 0)

        # (Lógica de itens omitida para brevidade, mantém igual ao anterior)
        # ... Copie a lógica de carregar_item do prompt anterior se necessário ...
        # Mas como é um método estático, se o user copiar este arquivo inteiro,
        # precisa incluir a lógica de itens aqui dentro. Vou incluir simplificado:
        def carregar_item(d):
            if not d: return None
            tipo = d.pop("classe_item", "pot")
            if tipo == "equip": return Equipamento(d["nome"], d["slot"], d["ataque_bonus"], d["defesa_bonus"])
            else: return Consumivel(d["nome"], d["tipo"], d["valor_efeito"])

        p.inventario = [carregar_item(i) for i in dados.get("inventario", [])]
        eq = dados.get("equipamentos", {})
        p.equipamentos["arma"] = carregar_item(eq.get("arma"))
        p.equipamentos["armadura"] = carregar_item(eq.get("armadura"))
        
        return p


# --- SUBCLASSES COM A LÓGICA DAS SKILLS ---

class Guerreiro(Personagem):
    def __init__(self, nome): super().__init__(nome, Atributos(120, 15, 5, 20))
    
    def skill_golpe_devastador(self):
        custo = 10
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            return int(self.ataque_total * 2), "usou Golpe Devastador!"
        return 0, "sem mana suficiente (10)."

    def skill_grito_de_guerra(self):
        custo = 20
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            # Cura e dá dano
            self.curar(20)
            return int(self.ataque_total * 1.2), "usou Grito de Guerra (Curou 20 HP)!"
        return 0, "sem mana suficiente (20)."

    def skill_execução_final(self):
        custo = 50
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            return int(self.ataque_total * 4), "USOU EXECUÇÃO FINAL!!!"
        return 0, "sem mana suficiente (50)."

class Mago(Personagem):
    def __init__(self, nome): super().__init__(nome, Atributos(70, 5, 2, 100))

    # Passiva Mente Clara: Regen mana
    def calcular_dano_base(self) -> int:
        if "Mente Clara" in self.passivas_ativas:
            self._atrib.mana += 5
            # print("Recuperou 5 mana") # Opcional
        return super().calcular_dano_base()

    def skill_bola_de_fogo(self):
        custo = 25
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            dano = 40 + int(self.ataque_total * 1.5)
            return dano, "lançou Bola de Fogo!"
        return 0, "sem mana suficiente (25)."

    def skill_raio_congelante(self):
        custo = 40
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            # No futuro pode adicionar status "Congelado"
            return int(self.ataque_total * 2.5), "lançou Raio Congelante!"
        return 0, "sem mana suficiente (40)."

    def skill_meteoro(self):
        custo = 100
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            return int(self.ataque_total * 5), "INVOCOU O METEORO DO CAOS!"
        return 0, "sem mana suficiente (100)."

class Arqueiro(Personagem):
    def __init__(self, nome): super().__init__(nome, Atributos(90, 12, 3, 40))

    def skill_flecha_precisa(self):
        custo = 15
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            return int(self.ataque_total * 1.5) + 10, "disparou Flecha Precisa!"
        return 0, "sem mana suficiente (15)."

    def skill_chuva_de_flechas(self):
        custo = 30
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            dano_total = int(self.ataque_total * 0.7) * 3
            return dano_total, "disparou Chuva de Flechas (3 hits)!"
        return 0, "sem mana suficiente (30)."

    def skill_flecha_fantasma(self):
        custo = 60
        if self._atrib.mana >= custo:
            self._atrib.mana -= custo
            # Ignora defesa (simulado com dano puro alto)
            dano = int(self.ataque_total * 3) + 50
            return dano, "disparou Flecha Fantasma (Dano Puro)!"
        return 0, "sem mana suficiente (60)."