from __future__ import annotations
import time
import random
from dataclasses import dataclass
from .personagem import Personagem
from .inimigo import Inimigo

@dataclass
class ResultadoMissao:
    venceu: bool
    detalhes: str

class Missao:
    def __init__(self, titulo: str, inimigo: Inimigo):
        self.titulo = titulo
        self.inimigo = inimigo

    def executar(self, p: Personagem) -> ResultadoMissao:
        print(f"\n{'='*40}")
        print(f"MISSÃO INICIADA: {self.titulo}")
        print(f"Você encontrou um {self.inimigo.nome}!")
        print(f"{'='*40}\n")
        time.sleep(1)

        # Loop principal do combate
        turnos = 0
        while p.vivo and self.inimigo.vivo:
            turnos += 1
            self._mostrar_status(p, self.inimigo)
            
            # --- Turno do Jogador ---
            print("\nSua vez! Escolha a ação:")
            print("[1] Ataque Básico")
            print("[2] Habilidade Especial")
            print("[3] Tentar Fugir")
            acao = input("> ").strip()

            dano_causado = 0
            msg_acao = ""

            if acao == "1":
                dano_causado = p.calcular_dano_base()
                msg_acao = f"atacou com sua arma básica"
            
            elif acao == "2":
                dano, msg = p.habilidade_especial()
                if dano > 0:
                    dano_causado = dano
                    msg_acao = msg
                else:
                    print(f"Falha: {msg} (Perdeu o turno!)")
            
            elif acao == "3":
                # Chance de fuga 30%
                if random.random() < 0.3:
                    print("\nVocê conseguiu escapar correndo!")
                    return ResultadoMissao(venceu=False, detalhes="Fugiu da batalha.")
                else:
                    print("\nFalha ao fugir! O inimigo bloqueou o caminho.")
            
            else:
                print("Comando inválido! Você tropeçou e perdeu a vez.")

            # Aplica dano ao inimigo se houve ataque
            if dano_causado > 0:
                dano_real = self.inimigo.receber_dano(dano_causado)
                print(f"--> Você {msg_acao} e causou {dano_real} de dano!")

            # Verifica se inimigo morreu
            if not self.inimigo.vivo:
                break
            
            time.sleep(1)

            # --- Turno do Inimigo ---
            print(f"\nTurno do {self.inimigo.nome}...")
            dano_inimigo = self.inimigo.atacar()
            # Variação leve no dano do inimigo (0.8x a 1.2x)
            dano_var = int(dano_inimigo * random.uniform(0.8, 1.2))
            dano_recebido = p.receber_dano(dano_var)
            
            print(f"<-- O {self.inimigo.nome} atacou você causando {dano_recebido} de dano!")
            time.sleep(1)

        # Fim do Loop
# ... (código anterior do loop while)

        print(f"\n{'='*40}")
        if p.vivo:
            # Define XP base do inimigo (pode virar atributo do Inimigo depois)
            xp_ganho = 100 + (self.inimigo._atrib.ataque * 2)
            
            print(f"VITÓRIA! O {self.inimigo.nome} caiu.")
            print(f"Você ganhou {xp_ganho} XP.")
            
            # --- AQUI A MÁGICA ACONTECE ---
            msgs_levelup = p.ganhar_xp(xp_ganho)
            
            if msgs_levelup:
                print("\n" + "*"*30)
                for msg in msgs_levelup:
                    print(f"*** {msg}")
                print("*"*30 + "\n")
            else:
                xp_prox = p.nivel * 100
                print(f"XP Atual: {p.xp}/{xp_prox}")
            # ------------------------------

            return ResultadoMissao(venceu=True, detalhes="Vitória em combate.")
        else:
            print("DERROTA... Sua visão escurece.")
            return ResultadoMissao(venceu=False, detalhes="Morto em combate.")

    def _mostrar_status(self, p: Personagem, e: Inimigo):
        print(f"\n--- Status ---")
        print(f"{p.nome:15} {p.barra_hp()} | MP: {p._atrib.mana}")
        print(f"{e.nome:15} {e.barra_hp()}")
        print("-" * 30)