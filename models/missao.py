from __future__ import annotations
import time
import random
from dataclasses import dataclass
from utils.logger import Logger
from .personagem import Personagem
from .inimigo import (
    Inimigo, 
    Goblin, Lobo, Orc, ReiOgro,                  
    Ladrao, Cacador, Elfo, EnviadoCacada,        
    MorcegoGigante, Gargula, Kobold, VermeColossal, 
    SoldadoZumbi, Ghoul, EspiritoSombrio, Lich   
)
from .item import Equipamento, Consumivel

class Cor:
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    CIANO = '\033[96m' # Cor nova para Gelo
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
        #Seleciona o inimigo correto baseando-se no Cenário e na Dificuldade
        mapa_comuns = {
            "Trilha":   [Ladrao, Cacador, Elfo],
            "Floresta": [Goblin, Lobo, Orc],
            "Caverna":  [Kobold, MorcegoGigante, Gargula],
            "Ruínas":   [SoldadoZumbi, Ghoul, EspiritoSombrio]
        }
        mapa_chefes = {
            "Trilha": EnviadoCacada, "Floresta": ReiOgro,
            "Caverna": VermeColossal, "Ruínas": Lich
        }

        lista_inimigos = mapa_comuns.get(cenario, [Goblin, Lobo, Orc])
        classe_chefe = mapa_chefes.get(cenario, ReiOgro)
        
        if dif == "Fácil":
            return random.choice(lista_inimigos[:2])()
        elif dif == "Média":
            return random.choice(lista_inimigos)()
        else: # Difícil
            if random.random() < 0.30:
                print(f"{Cor.VERMELHO}!!! UM CHEFE APARECEU !!!{Cor.RESET}")
                return classe_chefe()
            else:
                return random.choice(lista_inimigos[1:])()

    def executar(self, p: Personagem) -> ResultadoMissao:
        Logger.registrar(f"Iniciando missão ({self.cenario}): {p.nome} vs {self.inimigo.nome}")
        
        print(f"\n{Cor.AMARELO}{'='*40}{Cor.RESET}")
        print(f"CENÁRIO: {self.cenario}")
        print(f"PERIGO: Você encontrou um {Cor.VERMELHO}{self.inimigo.nome}{Cor.RESET}!")
        print(f"{Cor.AMARELO}{'='*40}{Cor.RESET}\n")
        time.sleep(1)

        turnos = 0
        
        # Dicionários de Status (Nome do status : Turnos restantes) isso também funciona para os jogador
        status_jogador = {"veneno": 0, "fogo": 0}
        status_inimigo = {"fogo": 0, "congelado": 0, "atordoado": 0}

        while p.vivo and self.inimigo.vivo:
            turnos += 1
            self._mostrar_status(p, self.inimigo)
            
            # Mostra ícones de status se houver
            stats_msg = []
            if status_inimigo['fogo'] > 0: stats_msg.append(f"{Cor.AMARELO}🔥 Queimando{Cor.RESET}")
            if status_inimigo['congelado'] > 0: stats_msg.append(f"{Cor.CIANO}❄️ Congelado{Cor.RESET}")
            if stats_msg: print(f"Status Inimigo: {' '.join(stats_msg)}")

            print(f"\n--- Turno {turnos} ---")

            # --- 1. PROCESSAR STATUS (DOTs) DO JOGADOR ---
            if status_jogador["veneno"] > 0:
                dano = 5
                p._atrib.vida -= dano
                status_jogador["veneno"] -= 1
                print(f"{Cor.VERMELHO}☠️ O veneno te causou {dano} de dano!{Cor.RESET}")
            
            if status_jogador["fogo"] > 0:
                dano = 8
                p._atrib.vida -= dano
                status_jogador["fogo"] -= 1
                print(f"{Cor.AMARELO}🔥 Você está queimando! Sofreu {dano} de dano.{Cor.RESET}")

            if not p.vivo: break

            # --- 2. PROCESSAR STATUS (DOTs) DO INIMIGO ---
            inimigo_perde_turno = False
            
            if status_inimigo["fogo"] > 0:
                # Dano de queimadura baseado na vida máx do inimigo (min 5, max 20)
                dano_burn = max(5, int(self.inimigo._atrib.vida_max * 0.05))
                self.inimigo._atrib.vida -= dano_burn
                status_inimigo["fogo"] -= 1
                print(f"{Cor.AMARELO}🔥 {self.inimigo.nome} sofreu {dano_burn} por queimadura!{Cor.RESET}")

            if status_inimigo["congelado"] > 0:
                inimigo_perde_turno = True
                status_inimigo["congelado"] -= 1
                print(f"{Cor.CIANO}❄️ {self.inimigo.nome} está CONGELADO e não pode se mover!{Cor.RESET}")
            
            elif status_inimigo["atordoado"] > 0: # Else if, para não perder 2 turnos seguidos no mesmo print
                inimigo_perde_turno = True
                status_inimigo["atordoado"] -= 1
                print(f"💫 {self.inimigo.nome} está ATORDOADO!")

            if not self.inimigo.vivo: break

            # --- 3. TURNO DO JOGADOR ---
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
                    
                    # --- APLICAR STATUS BASEADO NA HABILIDADE USADA ---
                    # Verifica palavras chaves na mensagem retornada pela classe
                    msg_lower = msg.lower()
                    
                    # Mago: Bola de Fogo / Meteoro
                    if "fogo" in msg_lower or "meteoro" in msg_lower:
                        if random.random() < 0.5: # 50% de chance de queimar
                            status_inimigo["fogo"] = 3 # Dura 3 turnos
                            print(f"{Cor.AMARELO}>>> Você incendeia o inimigo! (Dano contínuo) <<<{Cor.RESET}")

                    # Mago: Raio Congelante
                    if "congelante" in msg_lower or "gelo" in msg_lower:
                        if random.random() < 0.4: # 40% chance de congelar
                            status_inimigo["congelado"] = 1 # Perde 1 turno
                            print(f"{Cor.CIANO}>>> O inimigo congelou! (Perderá o próximo turno) <<<{Cor.RESET}")

                    # Guerreiro/Outros: Atordoar (Ex: Grito ou Escudo)
                    if "atordoar" in msg_lower or "esmagar" in msg_lower:
                         if random.random() < 0.3:
                            status_inimigo["atordoado"] = 1
                            print(">>> O impacto atordoou o inimigo! <<<")

                else:
                    print(f"{Cor.AMARELO}{msg}{Cor.RESET}")
                    passou_turno = False

            elif acao == "3":
                if self._menu_item(p):
                    dano_causado = 0
                    msg_acao = "usou um item"
                else:
                    passou_turno = False
            
            elif acao == "4":
                chance = 0.4 if "Rei" not in self.inimigo.nome else 0.15
                if random.random() < chance:
                    print(f"{Cor.VERDE}Você fugiu!{Cor.RESET}")
                    return ResultadoMissao(False, "Fugiu.")
                else:
                    print(f"{Cor.VERMELHO}Falha ao fugir!{Cor.RESET}")
            
            else:
                print("Opção inválida.")
                passou_turno = False

            # --- 4. APLICAÇÃO DO DANO NO INIMIGO ---
            if passou_turno:
                if dano_causado > 0:
                    real = self.inimigo.receber_dano(dano_causado)
                    print(f"--> Você {msg_acao} causando {Cor.VERDE}{real}{Cor.RESET} de dano!")
                    Logger.log_combate(turnos, p.nome, self.inimigo.nome, real)
                
                if not self.inimigo.vivo: break

                # --- 5. TURNO DO INIMIGO ---
                time.sleep(0.5)
                
                if inimigo_perde_turno:
                    print(f"{Cor.CIANO}O {self.inimigo.nome} não pode atacar neste turno!{Cor.RESET}")
                else:
                    # Inimigo age
                    dano_ini, msg_ini = self.inimigo.realizar_acao()
                    
                    # -- Inimigo aplicando status no Jogador --
                    if "Zumbi" in self.inimigo.nome or "Aranha" in self.inimigo.nome:
                        if random.random() < 0.2 and status_jogador["veneno"] == 0:
                            status_jogador["veneno"] = 3
                            print(f"{Cor.VERMELHO}!!! O inimigo te envenenou! !!!{Cor.RESET}")
                    
                    if "Lich" in self.inimigo.nome or "Dragão" in self.inimigo.nome:
                         if random.random() < 0.2 and status_jogador["fogo"] == 0:
                            status_jogador["fogo"] = 3
                            print(f"{Cor.AMARELO}!!! O inimigo te incendiou! !!!{Cor.RESET}")

                    dano_var = int(dano_ini * random.uniform(0.9, 1.1))
                    recebido = p.receber_dano(dano_var)
                    
                    print(f"<-- O {self.inimigo.nome} {msg_ini}! Você sofreu {Cor.VERMELHO}{recebido}{Cor.RESET} de dano.")
                    Logger.log_combate(turnos, self.inimigo.nome, p.nome, recebido)

        # --- FIM DO COMBATE ---
        if p.vivo:
            print(f"\n{Cor.VERDE}VITÓRIA! O inimigo caiu.{Cor.RESET}")
            xp = self.inimigo.xp_recompensa
            msgs = p.ganhar_xp(xp)
            print(f"Ganhou {Cor.AMARELO}{xp} XP{Cor.RESET}.")
            for m in msgs: print(f"{Cor.AZUL}{m}{Cor.RESET}")
            self._dropar_loot(p)
            return ResultadoMissao(True, "Vitória.")
        else:
            print(f"\n{Cor.VERMELHO}DERROTA...{Cor.RESET}")
            return ResultadoMissao(False, "Derrota.")

    def _mostrar_status(self, p, e):
        print(f"\n{Cor.AZUL}{p.nome}{Cor.RESET}: {p.barra_hp()} | MP: {p._atrib.mana}")
        print(f"{Cor.VERMELHO}{e.nome}{Cor.RESET}: {e.barra_hp()}")

    def _menu_item(self, p: Personagem) -> bool:
        potions = [i for i in p.inventario if isinstance(i, Consumivel)]
        if not potions:
            print("Sem poções!")
            return False
        print("\n--- Itens ---")
        for i, item in enumerate(potions):
            print(f"[{i+1}] {item.nome}")
        print("[0] Cancelar")
        try:
            op = int(input("> "))
            if op > 0 and op <= len(potions):
                item = potions[op-1]
                print(f"{Cor.VERDE}{item.usar(p)}{Cor.RESET}")
                p.inventario.remove(item)
                return True
        except: pass
        return False

    def _dropar_loot(self, p: Personagem):
        itens = self.inimigo.gerar_loot()
        if itens:
            for item in itens:
                print(f"{Cor.AMARELO}LOOT! {item.nome}{Cor.RESET}")
                p.inventario.append(item)
        else:
            print("Sem loot.")