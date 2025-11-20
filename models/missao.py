from __future__ import annotations
import time
import random
from dataclasses import dataclass
from utils.logger import Logger
from .personagem import Personagem
from .inimigo import Inimigo, Goblin, Lobo, Orc, Chefao
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
    def __init__(self, dificuldade: str):
        self.dificuldade = dificuldade
        self.inimigo = self._gerar_inimigo(dificuldade)
        self.titulo = f"Batalha contra {self.inimigo.nome}"

    def _gerar_inimigo(self, dif: str) -> Inimigo:
        """Fábrica de inimigos: escolhe aleatoriamente baseado na dificuldade."""
        if dif == "Fácil":
            return random.choice([Goblin(), Lobo()])
        elif dif == "Média":
            return random.choice([Lobo(), Orc()])
        else: # Difícil
            # 20% de chance de virar um Chefão no difícil
            if random.random() < 0.2:
                return Chefao()
            return Orc()

    def executar(self, p: Personagem) -> ResultadoMissao:
        Logger.registrar(f"Iniciando missão: {p.nome} (Nvl {p.nivel}) vs {self.inimigo.nome}")
        
        print(f"\n{Cor.AMARELO}{'='*40}{Cor.RESET}")
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
                # Abre inventário; se não usar nada, não passa o turno
                usou = self._menu_item(p)
                if usou:
                    dano_causado = 0
                    msg_acao = "usou um item"
                else:
                    passou_turno = False
            
            elif acao == "4":
                if random.random() < 0.4:
                    Logger.registrar(f"{p.nome} fugiu do {self.inimigo.nome}.")
                    print(f"{Cor.VERDE}Você conseguiu escapar!{Cor.RESET}")
                    return ResultadoMissao(False, "Fugiu da batalha.")
                else:
                    print(f"{Cor.VERMELHO}Falha ao fugir! O inimigo bloqueou o caminho.{Cor.RESET}")
            
            else:
                print("Opção inválida.")
                passou_turno = False

            # --- Aplicação de Dano (se o turno valeu) ---
            if passou_turno:
                if dano_causado > 0:
                    real = self.inimigo.receber_dano(dano_causado)
                    print(f"--> Você {msg_acao} causando {Cor.VERDE}{real}{Cor.RESET} de dano!")
                    Logger.log_combate(turnos, p.nome, self.inimigo.nome, real)
                
                if not self.inimigo.vivo:
                    break

                # --- Turno do Inimigo ---
                time.sleep(0.5)
                dano_ini = self.inimigo.atacar()
                # Pequena variação de dano (random)
                dano_var = int(dano_ini * random.uniform(0.8, 1.2))
                recebido = p.receber_dano(dano_var)
                
                print(f"<-- O {self.inimigo.nome} atacou! Você sofreu {Cor.VERMELHO}{recebido}{Cor.RESET} de dano.")
                Logger.log_combate(turnos, self.inimigo.nome, p.nome, recebido)

        # --- Resultado Final ---
        if p.vivo:
            print(f"\n{Cor.VERDE}VITÓRIA! O inimigo caiu.{Cor.RESET}")
            
            # Ganha XP
            xp_ganho = self.inimigo.xp_recompensa
            p.ganhar_xp(xp_ganho)
            Logger.registrar(f"Vitória. Ganhou {xp_ganho} XP.")
            
            # Drop de Loot
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
            print("Você não tem poções!")
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
                
                # Remove do inventário após uso
                p.inventario.remove(item)
                return True
        except ValueError:
            pass
        return False

    def _dropar_loot(self, p: Personagem):
        """Gera recompensa aleatória."""
        chance = random.random()
        
        if chance < 0.5: # 50% de chance de nada
            print("O inimigo não tinha itens valiosos.")
            return

        item_drop = None
        # Se for Chefão, dropa item melhor (opcional)
        if isinstance(self.inimigo, Chefao):
             item_drop = Equipamento("Espada do Rei Ogro", "arma", ataque=20)
        
        elif chance < 0.8: # 30% Chance de Poção
            tipo = random.choice(["vida", "mana"])
            qtd = 50 if tipo == "vida" else 20
            item_drop = Consumivel(f"Poção de {tipo.capitalize()}", tipo, qtd)
        
        else: # 20% Chance de Equipamento Comum
            if random.random() < 0.5:
                item_drop = Equipamento("Adaga de Goblin", "arma", ataque=5)
            else:
                item_drop = Equipamento("Escudo Quebrado", "armadura", defesa=3)

        if item_drop:
            print(f"\n{Cor.AMARELO}$$$ LOOT! Você pegou: {item_drop.nome} $$${Cor.RESET}")
            p.inventario.append(item_drop)
            Logger.registrar(f"Loot obtido: {item_drop.nome}")