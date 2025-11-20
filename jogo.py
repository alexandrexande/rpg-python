from __future__ import annotations
import glob
import json
import time
import random
from models.personagem import Personagem, Guerreiro, Mago, Arqueiro, ARVORE_EVOLUCAO
from models.missao import Missao
from utils.repositorio import Repositorio

# Cores para o terminal (opcional, para ficar bonito)
class Cor:
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

class Jogo:
    def __init__(self) -> None:
        self.jogador: Personagem | None = None
        
        self.dados_criacao = {
            "nome": "",
            "classe_str": ""
        }
        
        # Configuração padrão
        self.missao_config = {
            "dificuldade": "Média",
            "cenario": "Floresta",
        }
        self._ultimo_save = None

    # --------------------------------------------------------------------------
    # MENU: CRIAÇÃO DE PERSONAGEM
    # --------------------------------------------------------------------------
def menu_criar_personagem(self) -> None:
        while True:
            nome_exibir = self.dados_criacao["nome"] or "(não definido)"
            classe_exibir = self.dados_criacao["classe_str"] or "(não definido)"
            
            if self.jogador:
                print(f"\nPersonagem Ativo: {Cor.AZUL}{self.jogador.nome}{Cor.RESET} [{type(self.jogador).__name__}]")
                
            print("\n=== Criar/Substituir Personagem ===")
            print(f"Nome: {nome_exibir} | Classe: {classe_exibir}")
            print("[1] Definir nome")
            print("[2] Escolher classe")
            print("[3] 👀 Ver Preview de Habilidades (Obrigatório ver antes de escolher!)")
            print("[4] Ajuda")
            print("[5] Confirmar e Criar")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._definir_nome()
            elif op == "2":
                self._escolher_arquetipo()
            elif op == "3":
                self._menu_preview_classes() # <--- NOVO MENU
            elif op == "4":
                self._ajuda_criar_personagem
            elif op == "5":
                self._confirmar_criacao()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _definir_nome(self) -> None:
        nome = input("Digite o nome do personagem: ").strip()
        if nome:
            self.dados_criacao["nome"] = nome

    def _escolher_arquetipo(self) -> None:
        print("\nClasses disponíveis:")
        print("[1] Guerreiro (Tanque/Físico)")
        print("[2] Mago (Frágil/Dano Mágico)")
        print("[3] Arqueiro (Equilibrado)")
        escolha = input("> ").strip()

        mapa = {"1": "Guerreiro", "2": "Mago", "3": "Arqueiro"}
        classe_escolhida = mapa.get(escolha)
        
        if classe_escolhida:
            self.dados_criacao["classe_str"] = classe_escolhida
            print(f"Classe selecionada: {classe_escolhida}")
        else:
            print("Opção inválida.")

    def _menu_preview_classes(self) -> None:
        while True:
            print("\n=== Guia de Classes e Evolução ===")
            print("Veja o que cada classe ganha até o nível 20.")
            print("[1] Guerreiro")
            print("[2] Mago")
            print("[3] Arqueiro")
            print("[0] Voltar")
            op = input("> ").strip()
            
            mapa = {"1": "Guerreiro", "2": "Mago", "3": "Arqueiro"}
            classe = mapa.get(op)
            
            if classe:
                self._mostrar_arvore_detalhada(classe)
            elif op == "0":
                break
            else:
                print("Inválido.")

    def _mostrar_arvore_detalhada(self, nome_classe: str):
        dados = ARVORE_EVOLUCAO.get(nome_classe)
        stats = dados["status_base"]
        
        print(f"\n{Cor.AMARELO}>>> EVOLUÇÃO: {nome_classe.upper()} <<<{Cor.RESET}")
        print(f"Ganho fixo por nível: +{stats['vida']} HP | +{stats['mana']} MP | +{stats['ataque']} ATK | +{stats['defesa']} DEF")
        print("-" * 60)
        
        # Itera de 1 a 20 para mostrar timeline
        for nivel in range(1, 21):
            info = dados.get(nivel)
            if info:
                # Nível com Recompensa Especial
                prefixo = "[HABILIDADE]" if info['tipo'] == 'skill' else "[PASSIVA]"
                cor_txt = Cor.VERDE if info['tipo'] == 'skill' else Cor.AZUL
                
                print(f"Nível {nivel:02d}: {cor_txt}{prefixo} {info['nome']}{Cor.RESET}")
                print(f"          Descrição: {info['desc']}")
                if 'custo' in info:
                    print(f"          Custo: {info['custo']} MP")
                print("-" * 60)
            else:
                # Nível Comum
                # print(f"Nível {nivel:02d}: Aumento de Status Padrão")
                pass
        
        input("[Pressione Enter para voltar]")

    def _confirmar_criacao(self) -> None:
        nome = self.dados_criacao["nome"]
        classe_str = self.dados_criacao["classe_str"]

        if not nome or not classe_str:
            print("Erro: Defina NOME e CLASSE antes de confirmar.")
            return

        if classe_str == "Guerreiro":
            self.jogador = Guerreiro(nome)
        elif classe_str == "Mago":
            self.jogador = Mago(nome)
        elif classe_str == "Arqueiro":
            self.jogador = Arqueiro(nome)
        
        print(f"\n✨ Personagem {self.jogador.nome} criado com sucesso!")

    def _ajuda_criar_personagem(self) -> None:
        print("\nAjuda — Criar Personagem")
        print("- Defina um nome e um arquétipo para continuar.")
        print("- Ao confirmar, um novo personagem nível 1 será gerado.")

    # --------------------------------------------------------------------------
    # MENU: MISSÃO (COM MODO SOBREVIVÊNCIA)
    # --------------------------------------------------------------------------
    def menu_missao(self) -> None:
        while True:
            print("\n=== Missão & Combate ===")
            print(f"Configuração Atual: [{self.missao_config['dificuldade']}] em [{self.missao_config['cenario']}]")
            print("[1] Escolher dificuldade")
            print("[2] Escolher cenário")
            print(f"[3] Iniciar Missão Única")
            print(f"{Cor.VERMELHO}[5] ☠️  Modo Sobrevivência (Múltiplas Missões) ☠️{Cor.RESET}")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._escolher_dificuldade()
            elif op == "2":
                self._escolher_cenario()
            elif op == "3":
                self._iniciar_missao_unica()
            elif op == "5":
                self._iniciar_modo_sobrevivencia()
            elif op == "9":
                self._ajuda_missao()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _escolher_dificuldade(self) -> None:
        print("\nDificuldades:")
        print("[1] Fácil")
        print("[2] Média")
        print("[3] Difícil")
        op = input("> ").strip()
        mapa = {"1": "Fácil", "2": "Média", "3": "Difícil"}
        dif = mapa.get(op)
        if dif:
            self.missao_config["dificuldade"] = dif
            print(f"Dificuldade definida: {dif}")

    def _escolher_cenario(self) -> None:
        print("\nCenários:")
        print("[1] Floresta")
        print("[2] Trilha")
        print("[3] Caverna")
        print("[4] Ruínas")
        op = input("> ").strip()
        mapa = {"1": "Floresta", "2": "Trilha", "3": "Caverna", "4": "Ruínas"}
        cen = mapa.get(op)
        if cen:
            self.missao_config["cenario"] = cen
            print(f"Cenário definido: {cen}")

    def _iniciar_missao_unica(self) -> None:
        if not self.jogador:
            print("Crie um personagem primeiro.")
            return

        dificuldade = self.missao_config["dificuldade"]
        cenario = self.missao_config["cenario"]
        
        # Cria e executa a missão
        missao = Missao(dificuldade, cenario)
        missao.executar(self.jogador)
        
        if not self.jogador.vivo:
            print(f"{Cor.VERMELHO}Game Over.{Cor.RESET}")
            self.jogador = None

    def _iniciar_modo_sobrevivencia(self) -> None:
        """
        Loop de múltiplas missões com fogueira entre elas.
        """
        if not self.jogador:
            print("Crie um personagem primeiro.")
            return

        print(f"\n{Cor.VERMELHO}=== ⚔️ MODO SOBREVIVÊNCIA INICIADO ⚔️ ==={Cor.RESET}")
        print("Você viajará por várias terras. Se morrer, perde o personagem.")
        print("Entre as batalhas, você poderá descansar.")
        time.sleep(1)

        rodada = 1
        cenarios_disponiveis = ["Floresta", "Trilha", "Caverna", "Ruínas"]
        
        while self.jogador.vivo:
            # Escolhe um cenário aleatório para dar variedade
            cenario_atual = random.choice(cenarios_disponiveis)
            dificuldade = self.missao_config["dificuldade"] # Mantém a dif escolhida

            print(f"\n>>> {Cor.AMARELO}RODADA {rodada}{Cor.RESET} - Viajando para: {cenario_atual} <<<")
            time.sleep(1)

            # Executa a missão
            missao = Missao(dificuldade, cenario_atual)
            resultado = missao.executar(self.jogador)

            # Se morreu, acaba tudo
            if not self.jogador.vivo:
                print(f"\n{Cor.VERMELHO}Sua jornada acabou na rodada {rodada}.{Cor.RESET}")
                self.jogador = None
                break

            # Se venceu, aparece a FOGUEIRA
            print(f"\n{Cor.AMARELO}🔥 Você encontra uma Fogueira segura... 🔥{Cor.RESET}")
            print(f"Status: {self.jogador.barra_hp()} | MP: {self.jogador._atrib.mana}")
            print("[1] Descansar (Recuperar Vida e Mana) e Continuar")
            print("[2] Pegar o Loot e Voltar para a Cidade (Sair)")
            
            opcao = input("> ").strip()
            
            if opcao == "1":
                print("\nVocê senta perto do fogo, come algo e medita...")
                # Recupera Vida (Cura total)
                recuperado = self.jogador.curar(9999)
                # Recupera Mana (Simples adição, já que não temos mana_max explícito na base)
                self.jogador._atrib.mana += 50 
                
                time.sleep(1)
                print(f"{Cor.VERDE}Recuperou {recuperado} HP e 50 MP!{Cor.RESET}")
                print("Preparando para a próxima viagem...")
                rodada += 1
                time.sleep(1)
                
            elif opcao == "2":
                print(f"\nVocê decide que já arriscou demais por hoje.")
                print(f"Retornando vitorioso após {rodada} rodadas!")
                break
            else:
                print("Opção inválida. Você fica indeciso e acaba descansando por padrão.")
                self.jogador.curar(9999)
                rodada += 1

    def _ajuda_missao(self) -> None:
        print("\nAjuda — Missão")
        print("- Missão Única: Joga no cenário configurado e volta ao menu.")
        print("- Sobrevivência: Enfrenta inimigos aleatórios em sequência.")
        print("- A dificuldade afeta a força dos inimigos e a chance de chefes.")

    # --------------------------------------------------------------------------
    # MENU: SALVAR
    # --------------------------------------------------------------------------
    def menu_salvar(self) -> None:
        while True:
            print("\n=== Salvar ===")
            print("[1] Salvar rápido")
            print("[2] Salvar com nome")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._salvar_rapido()
            elif op == "2":
                self._salvar_nomeado()
            elif op == "0":
                break

    def _salvar_rapido(self) -> None:
        if not self.jogador: return
        repo = Repositorio()
        repo.salvar(self.jogador.to_dict(), "quick_save")
        self._ultimo_save = "quick_save.json"

    def _salvar_nomeado(self) -> None:
        if not self.jogador:
            print("Nenhum personagem para salvar!")
            return
        nome_arquivo = input("Nome do arquivo de save (ex: save1): ").strip()
        if not nome_arquivo: nome_arquivo = "save_auto"
        
        repo = Repositorio()
        repo.salvar(self.jogador.to_dict(), nome_arquivo)

    # --------------------------------------------------------------------------
    # MENU: CARREGAR
    # --------------------------------------------------------------------------
    def menu_carregar(self) -> None:
        while True:
            print("\n=== Carregar ===")
            print("[1] Carregar último save")
            print("[2] Carregar por nome")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._carregar_ultimo()
            elif op == "2":
                self._carregar_nomeado()
            elif op == "0":
                break

    def _carregar_ultimo(self) -> None:
        if self._ultimo_save:
            self._carregar_arquivo(self._ultimo_save)
        else:
            # Tenta carregar o quick_save padrão
            self._carregar_arquivo("quick_save.json")

    def _carregar_nomeado(self) -> None:
        nome_arquivo = input("Nome do arquivo para carregar: ").strip()
        self._carregar_arquivo(nome_arquivo)

    def _carregar_arquivo(self, nome_arquivo: str) -> None:
        repo = Repositorio()
        dados = repo.carregar(nome_arquivo)
        if dados:
            try:
                self.jogador = Personagem.from_dict(dados)
                print(f"✔ Personagem {self.jogador.nome} carregado!")
            except Exception as e:
                print(f"Erro ao reconstruir personagem: {e}")

    # --------------------------------------------------------------------------
    # MENU: INVENTÁRIO & RANKING
    # --------------------------------------------------------------------------
    def menu_inventario(self) -> None:
        if not self.jogador: return
        while True:
            print("\n=== Inventário ===")
            arma = self.jogador.equipamentos['arma'].nome if self.jogador.equipamentos['arma'] else "Mãos nuas"
            armadura = self.jogador.equipamentos['armadura'].nome if self.jogador.equipamentos['armadura'] else "Roupas comuns"
            
            print(f"Equipado: [⚔️ {arma}] [🛡️ {armadura}]")
            print(f"Stats: ATK {self.jogador.ataque_total} | DEF {self.jogador.defesa_total}")
            
            print("\nMochila:")
            if not self.jogador.inventario:
                print("(Vazia)")
            else:
                for i, item in enumerate(self.jogador.inventario):
                    tipo = "Equip" if hasattr(item, 'slot') else "Poção"
                    detalhes = f"ATK+{item.ataque_bonus}" if hasattr(item, 'ataque_bonus') else f"Efeito {item.valor_efeito}"
                    print(f"[{i+1}] {item.nome} ({tipo} - {detalhes})")

            print("\n[N] Usar/Equipar item | [0] Voltar")
            op = input("> ").strip()
            if op == "0": break
            
            try:
                idx = int(op) - 1
                if 0 <= idx < len(self.jogador.inventario):
                    item = self.jogador.inventario[idx]
                    if hasattr(item, 'slot'):
                        self.jogador.equipar_item(item)
                    else:
                        print(item.usar(self.jogador))
                        self.jogador.inventario.pop(idx)
            except ValueError:
                pass

    def exibir_ranking(self) -> None:
        print("\n=== 🏆 HALL DA FAMA 🏆 ===")
        arquivos_saves = glob.glob("*.json")
        placar = []

        for arquivo in arquivos_saves:
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    if "nome" in dados and "xp" in dados:
                        placar.append(dados)
            except:
                continue

        placar_ordenado = sorted(placar, key=lambda x: x["xp"], reverse=True)

        if not placar_ordenado:
            print("Nenhum registro encontrado.")
        else:
            print(f"{'Pos':<4} | {'Nome':<15} | {'Nível':<5} | {'XP':<6}")
            print("-" * 40)
            for i, p in enumerate(placar_ordenado):
                medalha = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else ""
                print(f"{i+1:<4} | {p['nome']:<15} | {p['nivel']:<5} | {p['xp']:<6} {medalha}")
        
        input("\n[Enter] Voltar...")