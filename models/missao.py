from __future__ import annotations
import time
import random
from dataclasses import dataclass
from utils.logger import Logger
from .personagem import Personagem
# Importando todas as variações de inimigos criadas
from .inimigo import (
    Inimigo, 
    Goblin, Lobo, Orc, ReiOgro,                  # Floresta
    Ladrao, Cacador, Elfo, EnviadoCacada,        # Trilha
    MorcegoGigante, Gargula, Kobold, VermeColossal, # Caverna
    SoldadoZumbi, Ghoul, EspiritoSombrio, Lich   # Ruinas
)
from .item import Equipamento, Consumivel

# --- Códigos de Cores para o Terminal ---
class Cor:
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

@dataclass
class ResultadoMissao:
    venceu: bool
    detalhes: str

class Missao:
    def __init__(self, dificuldade: str, cenario: str = "Floresta"):
        self.dificuldade = dificuldade
        self.cenario = cenario
        self.inimigo = self._gerar_inimigo(dificuldade, cenario)
        self.titulo = f"Batalha contra {self.inimigo.nome}"

    def _gerar_inimigo(self, dif: str, cenario: str) -> Inimigo:
        """
        Seleciona o inimigo correto baseando-se no Cenário e na Dificuldade.
        """
        # Mapa de inimigos comuns por cenário
        mapa_comuns = {
            "Trilha":   [Ladrao, Cacador, Elfo],
            "Floresta": [Goblin, Lobo, Orc],
            "Caverna":  [Kobold, MorcegoGigante, Gargula],
            "Ruínas":   [SoldadoZumbi, Ghoul, EspiritoSombrio]
        }
        
        # Mapa de Chefes por cenário
        mapa_chefes = {
            "Trilha": EnviadoCacada,
            "Floresta": ReiOgro,
            "Caverna": VermeColossal,
            "Ruínas": Lich
        }

        # Recupera a lista (ou usa Floresta como fallback/padrão)
        lista_inimigos = mapa_comuns.get(cenario, [Goblin, Lobo, Orc])
        classe_chefe = mapa_chefes.get(cenario, ReiOgro)
        
        if dif == "Fácil":
            # Escolhe entre os dois primeiros (mais fracos da área)
            return random.choice(lista_inimigos[:2])()
            
        elif dif == "Média":
            # Pode ser qualquer um dos comuns
            return random.choice(lista_inimigos)()
            
        else: # Difícil
            # 30% de chance de ser o Chefe da área
            if random.random() < 0.30:
                print(f"{Cor.VERMELHO}!!! UM CHEFE APARECEU !!!{Cor.RESET}")
                return classe_chefe()
            else:
                # Se não for chefe, é um dos inimigos mais fortes (exclui o primeiro da lista)
                return random.choice(lista_inimigos[1:])()

    def executar(self, p: Personagem) -> ResultadoMissao:
        Logger.registrar(f"Iniciando missão ({self.cenario}): {p.nome} vs {self.inimigo.nome}")
        
        print(f"\n{Cor.AMARELO}{'='*40}{Cor.RESET}")
        print(f"CENÁRIO: {self.cenario}")
        print(f"PERIGO: Você encontrou um {Cor.VERMELHO}{self.inimigo.nome}{Cor.RESET}!")
        print(f"{Cor.AMARELO}{'='*40}{Cor.RESET}\n")
        time.sleep(1)

        turnos = 0
        while p.vivo and self.inimigo.vivo:
            turnos += 1
            self._mostrar_status(p, self.inimigo)
            print(f"\n--- Turno {turnos} ---")

            # --- Turno do Jogador ---
            print("[1] Atacar")
            print("[2] Habilidade Especial")
            print("[3] Usar Item")
            print("[4] Fugir")
            acao = input("> ").strip()
            
            dano_causado = 0
            msg_acao = ""
            passou_turno = True

            if acao == "1":
                dano_causado = p.calcular_dano_base()
                msg_acao = f"atacou com {p.equipamentos['arma'].nome if p.equipamentos['arma'] else 'punhos'}"
            
            elif acao == "2":
                dano, msg = p.habilidade_especial()
                if dano > 0:
                    dano_causado = dano
                    msg_acao = msg
                else:
                    print(f"{Cor.AMARELO}{msg}{Cor.RESET}")
                    passou_turno = False # Não gasta o turno se falhar

            elif acao == "3":
                usou = self._menu_item(p)
                if usou:
                    dano_causado = 0
                    msg_acao = "usou um item"
                else:
                    passou_turno = False
            
            elif acao == "4":
                # Chance de fuga (mais difícil contra chefes)
                chance_fuga = 0.4
                if "Rei" in self.inimigo.nome or "Lich" in self.inimigo.nome or "Verme" in self.inimigo.nome:
                    chance_fuga = 0.15
                
                if random.random() < chance_fuga:
                    Logger.registrar(f"{p.nome} fugiu do {self.inimigo.nome}.")
                    print(f"{Cor.VERDE}Você conseguiu escapar!{Cor.RESET}")
                    return ResultadoMissao(False, "Fugiu da batalha.")
                else:
                    print(f"{Cor.VERMELHO}Falha ao fugir! O inimigo bloqueou o caminho.{Cor.RESET}")
            
            else:
                print("Opção inválida.")
                passou_turno = False

            # --- Aplicação de Dano do Jogador ---
            if passou_turno:
                if dano_causado > 0:
                    real = self.inimigo.receber_dano(dano_causado)
                    print(f"--> Você {msg_acao} causando {Cor.VERDE}{real}{Cor.RESET} de dano!")
                    Logger.log_combate(turnos, p.nome, self.inimigo.nome, real)
                
                if not self.inimigo.vivo:
                    break

                # --- Turno do Inimigo (IA Atualizada) ---
                time.sleep(0.5)
                
                # O inimigo decide se usa Skill ou Ataque Normal
                dano_ini, msg_ini = self.inimigo.realizar_acao()
                
                # Pequena variação aleatória no dano final (±10%)
                dano_var = int(dano_ini * random.uniform(0.9, 1.1))
                
                recebido = p.receber_dano(dano_var)
                
                print(f"<-- O {self.inimigo.nome} {msg_ini}! Você sofreu {Cor.VERMELHO}{recebido}{Cor.RESET} de dano.")
                Logger.log_combate(turnos, self.inimigo.nome, p.nome, recebido)

        # --- Resultado Final ---
        if p.vivo:
            print(f"\n{Cor.VERDE}VITÓRIA! O inimigo caiu.{Cor.RESET}")
            
            # Ganha XP
            xp_ganho = self.inimigo.xp_recompensa
            msgs_level = p.ganhar_xp(xp_ganho)
            print(f"Ganhou {Cor.AMARELO}{xp_ganho} XP{Cor.RESET}.")
            
            for msg in msgs_level:
                print(f"{Cor.AZUL}{msg}{Cor.RESET}")
            
            Logger.registrar(f"Vitória. Ganhou {xp_ganho} XP.")
            
            # Drop de Loot (Novo Sistema)
            self._dropar_loot(p)
            
            return ResultadoMissao(True, "Vitória Conquistada.")
        else:
            print(f"\n{Cor.VERMELHO}DERROTA... Você caiu em combate.{Cor.RESET}")
            Logger.registrar(f"Derrota. Personagem {p.nome} morreu.")
            return ResultadoMissao(False, "Morto em combate.")

    def _mostrar_status(self, p, e):
        print(f"\n{Cor.AZUL}{p.nome}{Cor.RESET}: {p.barra_hp()} | MP: {p._atrib.mana}")
        print(f"{Cor.VERMELHO}{e.nome}{Cor.RESET}: {e.barra_hp()}")

    def _menu_item(self, p: Personagem) -> bool:
        """Lista apenas consumíveis para uso em batalha."""
        potions = [i for i in p.inventario if isinstance(i, Consumivel)]
        
        if not potions:
            print("Você não tem itens utilizáveis em combate!")
            return False
        
        print("\n--- Itens Disponíveis ---")
        for i, item in enumerate(potions):
            print(f"[{i+1}] {item.nome} (Efeito: {item.valor_efeito})")
        print("[0] Cancelar")
        
        try:
            op = int(input("Usar qual item? > "))
            if op > 0 and op <= len(potions):
                item = potions[op-1]
                msg = item.usar(p)
                print(f"{Cor.VERDE}{msg}{Cor.RESET}")
                Logger.registrar(f"Usou item: {item.nome}")
                
                p.inventario.remove(item)
                return True
        except ValueError:
            pass
        return False

    def _dropar_loot(self, p: Personagem):
        """Gera recompensa baseada no loot específico do inimigo."""
        print(f"\nVerificando os espólios de {self.inimigo.nome}...")
        time.sleep(0.5)
        
        itens_dropados = self.inimigo.gerar_loot()
        
        if not itens_dropados:
            print("Nada de valor encontrado.")
        else:
            for item in itens_dropados:
                print(f"{Cor.AMARELO}$$$ LOOT! Você pegou: {item.nome} $$${Cor.RESET}")
                p.inventario.append(item)
                Logger.registrar(f"Loot obtido: {item.nome}")