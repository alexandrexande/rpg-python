from __future__ import annotations
import time
import random
from dataclasses import dataclass
from .personagem import Personagem
from .inimigo import Inimigo
from .item import Equipamento, Consumivel

@dataclass
class ResultadoMissao:
    venceu: bool
    detalhes: str

class Missao:
    def __init__(self, titulo: str, inimigo: Inimigo):
        self.titulo = titulo
        self.inimigo = inimigo

    def executar(self, p: Personagem) -> ResultadoMissao:
        print(f"\n=== COMBATE: {self.titulo} ===")
        print(f"Inimigo: {self.inimigo.nome} (HP: {self.inimigo._atrib.vida})")
        time.sleep(1)

        while p.vivo and self.inimigo.vivo:
            self._mostrar_status(p, self.inimigo)
            
            print("\nAções:")
            print("[1] Atacar")
            print("[2] Habilidade Especial")
            print("[3] Usar Item (Inventário)")
            print("[4] Fugir")
            acao = input("> ").strip()

            dano_causado = 0
            msg_acao = ""
            turno_passou = True

            if acao == "1":
                dano_causado = p.calcular_dano_base()
                msg_acao = f"atacou com {p.equipamentos['arma'].nome if p.equipamentos['arma'] else 'punhos'}"
            
            elif acao == "2":
                dano, msg = p.habilidade_especial()
                if dano > 0:
                    dano_causado = dano
                    msg_acao = msg
                else:
                    print(f"Falha: {msg}")
                    turno_passou = False # Não perde turno se falhar por falta de mana
            
            elif acao == "3":
                usou = self._menu_inventario_batalha(p)
                if usou:
                    msg_acao = "usou um item"
                    dano_causado = 0
                else:
                    turno_passou = False
            
            elif acao == "4":
                if random.random() < 0.4:
                    return ResultadoMissao(False, "Fugiu com sucesso.")
                print("Falha ao fugir!")
            
            else:
                print("Opção inválida.")
                turno_passou = False

            if turno_passou:
                # Aplica dano no inimigo
                if dano_causado > 0:
                    real = self.inimigo.receber_dano(dano_causado)
                    print(f"--> Você {msg_acao} causando {real} de dano!")
                
                if not self.inimigo.vivo: break

                # Inimigo ataca
                time.sleep(0.5)
                dano_ini = int(self.inimigo.atacar() * random.uniform(0.8, 1.2))
                recebido = p.receber_dano(dano_ini)
                print(f"<-- {self.inimigo.nome} atacou você causando {recebido} de dano!")

        if p.vivo:
            print(f"\nVITÓRIA! O {self.inimigo.nome} foi derrotado.")
            p.ganhar_xp(100)
            self._gerar_loot(p)
            return ResultadoMissao(True, "Vitória.")
        
        return ResultadoMissao(False, "Derrota.")

    def _mostrar_status(self, p, e):
        print(f"\n{p.nome}: {p.barra_hp()} | MP:{p._atrib.mana}")
        print(f"{e.nome}: {e.barra_hp()}")

    def _menu_inventario_batalha(self, p: Personagem) -> bool:
        """Retorna True se usou item, False se cancelou."""
        potions = [i for i in p.inventario if isinstance(i, Consumivel)]
        if not potions:
            print("Nenhuma poção no inventário!")
            return False
        
        print("\n--- Poções ---")
        for i, item in enumerate(potions):
            print(f"[{i+1}] {item.nome} (Efeito: {item.valor_efeito})")
        print("[0] Cancelar")
        
        try:
            op = int(input("> "))
            if 0 < op <= len(potions):
                item = potions[op-1]
                print(item.usar(p))
                p.inventario.remove(item)
                return True
        except:
            pass
        return False

    def _gerar_loot(self, p: Personagem):
        """Gera equipamentos ou poções aleatórias."""
        chance = random.random()
        item_drop = None

        if chance < 0.4: # 40% chance de Poção
            tipo = random.choice(["vida", "mana"])
            qtd = 50 if tipo == "vida" else 20
            item_drop = Consumivel(f"Poção de {tipo.capitalize()}", tipo, qtd)
        
        elif chance < 0.7: # 30% chance de Equipamento
            if random.random() < 0.5:
                # Arma
                nomes = ["Espada de Ferro", "Machado Velho", "Adaga Cortante"]
                item_drop = Equipamento(random.choice(nomes), "arma", ataque=random.randint(3, 8))
            else:
                # Armadura
                nomes = ["Colete de Couro", "Armadura Enferrujada", "Manto Mágico"]
                item_drop = Equipamento(random.choice(nomes), "armadura", defesa=random.randint(2, 5))
        
        else:
            print("O inimigo não tinha itens.")
            return

        if item_drop:
            print(f"\n$$$ LOOT! Você encontrou: {item_drop.nome} $$$")
            p.inventario.append(item_drop)
            
            # Auto-equipar se for melhor (opcional, mas ajuda a testar)
            if isinstance(item_drop, Equipamento):
                print("Dica: Vá ao menu de inventário para equipar.")