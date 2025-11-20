from __future__ import annotations
import glob  # <--- Necessário para listar arquivos na pasta
import json
from models.personagem import Personagem, Guerreiro, Mago, Arqueiro
from models.missao import Missao
from models.inimigo import Inimigo
from utils.repositorio import Repositorio

class Jogo:
    def __init__(self) -> None:
        # Agora 'self.jogador' guardará o Objeto real, não apenas um dicionário
        self.jogador: Personagem | None = None
        
        # Dados temporários para o menu de criação
        self.dados_criacao = {
            "nome": "",
            "classe_str": ""
        }
        
        self.missao_config = {
            "dificuldade": "Fácil",
            "cenario": "Trilha",
        }
        self._ultimo_save = None

    def menu_criar_personagem(self) -> None:
        while True:
            # Mostra os dados temporários ou o objeto já criado
            nome_exibir = self.dados_criacao["nome"] or "(não definido)"
            classe_exibir = self.dados_criacao["classe_str"] or "(não definido)"
            
            if self.jogador:
                print(f"\nPersonagem Ativo: {self.jogador.nome} [{type(self.jogador).__name__}]")
                print(f"HP: {self.jogador._atrib.vida} | ATK: {self.jogador._atrib.ataque} | MP: {self.jogador._atrib.mana}")
            
            print("\n=== Criar/Substituir Personagem ===")
            print(f"Nome (rascunho): {nome_exibir}")
            print(f"Classe (rascunho): {classe_exibir}")
            print("[1] Definir nome")
            print("[2] Escolher classe")
            print("[3] Confirmar e Criar")
            print("[4] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._definir_nome()
            elif op == "2":
                self._escolher_arquetipo()
            elif op == "3":
                self._confirmar_criacao()
            elif op == '4':
                self._ajuda_criar_personagem()
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

    def _confirmar_criacao(self) -> None:
        nome = self.dados_criacao["nome"]
        classe_str = self.dados_criacao["classe_str"]

        if not nome or not classe_str:
            print("Erro: Defina NOME e CLASSE antes de confirmar.")
            return

        # Lógica de Fábrica: Cria o objeto baseado na string
        if classe_str == "Guerreiro":
            self.jogador = Guerreiro(nome)
        elif classe_str == "Mago":
            self.jogador = Mago(nome)
        elif classe_str == "Arqueiro":
            self.jogador = Arqueiro(nome)
        
        print(f"\n✨ Personagem {self.jogador.nome} criado com sucesso!")
        print("Agora você tem atributos reais para jogar.")

    def _ajuda_criar_personagem(self) -> None:
        print("\nAjuda — Criar Personagem")
        print("- Defina um nome e um arquétipo para continuar.")
        print("- Esta etapa não cria atributos reais; é apenas o fluxo do menu.")
        print("- Implementações futuras podem usar essas escolhas para gerar status.")

    def menu_missao(self) -> None:
        while True:
            print("\n=== Missão ===")
            print(f"Dificuldade atual: {self.missao_config['dificuldade']}")
            print(f"Cenário atual:     {self.missao_config['cenario']}")
            print("[1] Escolher dificuldade")
            print("[2] Escolher cenário")
            print("[3] Pré-visualizar missão")
            print("[4] Iniciar missão (placeholder)")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._escolher_dificuldade()
            elif op == "2":
                self._escolher_cenario()
            elif op == "3":
                self._preview_missao()
            elif op == "4":
                self._iniciar_missao_placeholder()
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
        else:
            print("Opção inválida.")

    def _escolher_cenario(self) -> None:
        print("\nCenários:")
        print("[1] Trilha")
        print("[2] Floresta")
        print("[3] Caverna")
        print("[4] Ruínas")
        op = input("> ").strip()
        mapa = {"1": "Trilha", "2": "Floresta", "3": "Caverna", "4": "Ruínas"}
        cen = mapa.get(op)
        if cen:
            self.missao_config["cenario"] = cen
            print(f"Cenário definido: {cen}")
        else:
            print("Opção inválida.")

    def _preview_missao(self) -> None:
        print("\nPré-visualização da Missão")
        print(f"- Dificuldade: {self.missao_config['dificuldade']}")
        print(f"- Cenário:     {self.missao_config['cenario']}")
        print("- Inimigos e recompensas: (em breve)")
        print("- Regras de combate: (em breve)")

    def _iniciar_missao_placeholder(self) -> None:
        if not self.jogador:
            print("Crie um personagem primeiro.")
            return

        # Pega a dificuldade configurada
        dificuldade = self.missao_config["dificuldade"]
        
        # Cria e executa a missão (a missão gera o inimigo sozinha agora)
        missao = Missao(dificuldade)
        
        # Executa
        missao.executar(self.jogador)
        
        # Se morreu, reseta
        if not self.jogador.vivo:
            print("Game Over.")
            self.jogador = None

    def _ajuda_missao(self) -> None:
        print("\nAjuda — Missão")
        print("- Selecione dificuldade e cenário.")
        print("- A opção 'Iniciar missão' executará apenas um placeholder.")
        print("- Uma futura implementação pode usar essas escolhas para montar encontros.")

    def menu_salvar(self) -> None:
        while True:
            print("\n=== Salvar ===")
            print("[1] Salvar rápido (simulado)")
            print("[2] Salvar com nome (simulado)")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._salvar_rapido()
            elif op == "2":
                self._salvar_nomeado()
            elif op == "9":
                self._ajuda_salvar()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _salvar_rapido(self) -> None:
        self._ultimo_save = "quick_save.json"
        print(f"✔ Salvo (simulado) em: {self._ultimo_save}")

    def _salvar_nomeado(self) -> None:
        if not self.jogador:
            print("Nenhum personagem para salvar! Crie um primeiro.")
            return

        nome_arquivo = input("Nome do arquivo de save (ex: save1): ").strip()
        if not nome_arquivo:
            nome_arquivo = "save_auto"

        # 1. Converte o objeto jogador para dicionário
        dados_para_salvar = self.jogador.to_dict()
        
        # 2. Usa o repositório para escrever no disco
        repo = Repositorio()
        repo.salvar(dados_para_salvar, nome_arquivo)

    def _ajuda_salvar(self) -> None:
        print("\nAjuda — Salvar")
        print("- Salvar rápido usa um nome padrão fictício.")
        print("- Salvar nomeado permite escolher um nome fictício.")
        print("- Não há escrita em disco nesta base — é apenas navegação.")

    def menu_carregar(self) -> None:
        while True:
            print("\n=== Carregar ===")
            print("[1] Carregar último save (simulado)")
            print("[2] Carregar por nome (simulado)")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._carregar_ultimo()
            elif op == "2":
                self._carregar_nomeado()
            elif op == "9":
                self._ajuda_carregar()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _carregar_ultimo(self) -> None:
        if self._ultimo_save:
            self._ultimo_load = self._ultimo_save
            print(f"✔ Carregado (simulado) de: {self._ultimo_load}")
        else:
            print("Nenhum save recente encontrado (simulado).")

    def _carregar_nomeado(self) -> None:
        nome_arquivo = input("Nome do arquivo para carregar: ").strip()
        
        repo = Repositorio()
        dados = repo.carregar(nome_arquivo)
        
        if dados:
            # 3. Reconstrói o objeto jogador a partir dos dados
            try:
                self.jogador = Personagem.from_dict(dados)
                print(f"✔ Personagem {self.jogador.nome} (Nível {self.jogador.nivel}) carregado!")
            except Exception as e:
                print(f"Erro ao reconstruir personagem: {e}")

    def _ajuda_carregar(self) -> None:
        print("\nAjuda — Carregar")
        print("- O carregamento aqui é apenas ilustrativo (sem leitura real).")
        print("- Use o nome que você “salvou” anteriormente para simular.")

    def menu_inventario(self) -> None:
        if not self.jogador: return

        while True:
            print("\n=== Inventário & Equipamentos ===")
            # Mostra o que está no corpo
            arma = self.jogador.equipamentos['arma'].nome if self.jogador.equipamentos['arma'] else "Mãos nuas"
            armadura = self.jogador.equipamentos['armadura'].nome if self.jogador.equipamentos['armadura'] else "Roupas comuns"
            
            print(f"Equipado: [Arma: {arma}] [Corpo: {armadura}]")
            print(f"Stats Totais: Ataque {self.jogador.ataque_total} | Defesa {self.jogador.defesa_total}")
            
            print("\nMochila:")
            if not self.jogador.inventario:
                print("(Vazia)")
            else:
                for i, item in enumerate(self.jogador.inventario):
                    tipo = "Equip" if hasattr(item, 'slot') else "Poção"
                    detalhes = f"ATK+{item.ataque_bonus}" if hasattr(item, 'ataque_bonus') else f"Efeito {item.valor_efeito}"
                    print(f"[{i+1}] {item.nome} ({tipo} - {detalhes})")

            print("\n[N] Digite o número do item para usar/equipar")
            print("[0] Voltar")
            
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
# --- NOVO MÉTODO: RANKING ---
    def exibir_ranking(self) -> None:
        print("\n=== 🏆 HALL DA FAMA (RANKING DE XP) 🏆 ===")
        
        arquivos_saves = glob.glob("*.json") # Busca todos arquivos .json na pasta
        placar = []

        for arquivo in arquivos_saves:
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    
                    # Verifica se é um save válido de personagem
                    if "nome" in dados and "xp" in dados and "classe" in dados:
                        nome = dados["nome"]
                        xp = dados["xp"]
                        classe = dados["classe"]
                        nivel = dados["nivel"]
                        placar.append({"nome": nome, "xp": xp, "classe": classe, "nivel": nivel})
            except:
                continue # Ignora arquivos corrompidos ou que não são saves

        # Ordena a lista: Quem tem mais XP fica em primeiro (reverse=True)
        placar_ordenado = sorted(placar, key=lambda x: x["xp"], reverse=True)

        if not placar_ordenado:
            print("Nenhum registro encontrado.")
        else:
            print(f"{'Pos':<4} | {'Nome':<15} | {'Classe':<10} | {'Nível':<5} | {'XP':<6}")
            print("-" * 50)
            
            for i, p in enumerate(placar_ordenado):
                posicao = i + 1
                medalha = ""
                if posicao == 1: medalha = "🥇"
                elif posicao == 2: medalha = "🥈"
                elif posicao == 3: medalha = "🥉"
                
                print(f"{posicao:<4} | {p['nome']:<15} | {p['classe']:<10} | {p['nivel']:<5} | {p['xp']:<6} {medalha}")
        
        input("\nPressione Enter para voltar...")