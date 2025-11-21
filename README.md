# RPG Python (Sistema de Gestão de Aventuras)

Projeto desenvolvido como trabalho da disciplina de Paradigmas de Linguagem de Programação, aplicando conceitos de Orientação a Objetos, persistência de dados e lógica de jogo.

## 👥 Integrantes
* [**Alexandre Arcanjo**](https://www.github.com/alexandrexande)

# 📦 Ferramentas e Bibliotecas
Este projeto foi construído utilizando apenas bibliotecas nativas do Python, garantindo facilidade de execução em qualquer ambiente configurado.
## Mecanismo base
* Python 3.10 (Necessário devido à sintaxe moderna de tipagem, ex: int | None).

## Módulos Utilizados:

* json: Utilizado para serialização de dados no sistema de salvar e carregar progresso.

* random: Responsável pela aleatoriedade do combate, geração de inimigos e cálculo de dano/crítico.

* time: Controla o fluxo de texto e pausas durante a batalha para melhorar a experiência do usuário.

* os: Manipulação de caminhos de diretórios e verificação de arquivos do sistema.

* glob: Utilizado para buscar e listar todos os arquivos de save .json para o sistema de Ranking.

* dataclasses: Simplifica a declaração de classes que armazenam dados, como Item e Atributos.

* datetime: Registra o horário exato das ações no arquivo de log.

## 🚀 Como Rodar o Jogo

### Pré-requisitos
* É necessário ter o **Python 3.10** ou superior instalado.

### Passo a Passo
1.  Baixe o arquivo `.zip` do projeto (clicando no botão verde **Code** -> **Download ZIP** no GitHub).
2.  Descompacte o arquivo em uma pasta de sua preferência.
3.  Abra o terminal na pasta descompactada.
4.  Execute o arquivo principal:
    ```bash
    python main.py
    ```
    *(Ou clique duas vezes no arquivo `main.py` se o seu sistema estiver configurado para executar Python no console).*

    ## 📂 Estrutura do Projeto

O projeto está organizado seguindo o padrão MVC simplificado, separando modelos, controle e utilitários:

```
rpg_oo/
│
├── main.py              # Ponto de entrada (inicia o jogo)
├── jogo.py              # Controlador principal (Menus e fluxo de telas)
│
├── models/              # Classes de domínio (Regras de Negócio)
│   ├── base.py          # Classe mãe 'Entidade' (Atributos básicos)
│   ├── personagem.py    # Lógica do Jogador, Classes (Guerreiro/Mago) e Level Up
│   ├── inimigo.py       # Lógica dos Monstros, Chefes e Drops
│   ├── missao.py        # Motor de Combate (Turnos, Status, Dano)
│   └── item.py          # Definição de Equipamentos e Consumíveis
│
├── utils/               # Ferramentas auxiliares
│   ├── repositorio.py   # Sistema de Salvar/Carregar (JSON)
│   └── logger.py        # Sistema de Logs em arquivo
│
└── dados/               # Pasta gerada automaticamente para salvar .json e .log
```

## ⚔️ Funcionalidades do Projeto

### 1. Menu Principal e Sistema
* **Criação de Personagem:** Escolha de nome e classe.
* **Save/Load:** Sistema de salvamento orientado a objetos (JSON), permitindo carregar o progresso manualmente.
* **Ranking de XP:** Compara todos os saves criados e exibe um ranking baseado na experiência total (o nível não conta, apenas o XP bruto).
* **Logs:** Registro de combate em arquivo, mostrando o início das missões e o dano gerado pelo jogador e inimigos.

### 2. Classes e Personagens
O jogador pode escolher entre 3 arquétipos, cada um com sua árvore de habilidades (Skill Tree) que pode ser conferida no menu:
* **Guerreiro (Tank):** Focado em defesa e vida.
* **Mago (Glass Cannon):** Alto dano, mas pouca resistência.
* **Arqueiro (Equilibrado):** Balanceado entre ataque e sobrevivência, com foco em críticos.

### 3. Combate e Missões
* **Sistema de Turnos:** Combate tradicional onde é possível atacar, usar habilidades especiais ou itens consumíveis (poções).
* **Status Negativos:** O combate inclui efeitos como veneno, fogo e atordoamento.
* **Inimigos e Áreas:**
    * Cada área possui 3 tipos de inimigos comuns e 1 chefe.
    * **Dificuldade:** A dificuldade "Difícil" habilita a chance de encontrar Chefes, que possuem drops únicos.

### 4. Inventário e Equipamentos
* **Gerenciamento:** É possível checar os status de Dano (ATK) e Defesa (DEF) dos itens.
* **Equipamentos:** Equipar itens concede buffs diretos nos atributos do personagem. Itens possuem restrição de classe (ex: Cajados apenas para Magos).
* **Consumíveis:** Uso de poções de vida e mana durante e fora de batalha.

# ⚙️ Principais Funções e Lógica
Abaixo estão descritas as funções críticas que fazem o sistema funcionar:

## 1. Motor de Combate (models/missao.py)
```executar(self, personagem)```: É o coração do jogo. Gerencia o loop while que mantém a batalha ativa enquanto jogador e inimigo estiverem vivos.

Calcula a ordem dos turnos.

Aplica efeitos de status (ex: dano de queimadura no início do turno).

Processa a escolha do jogador (Ataque, Skill, Item, Fuga) e a IA do inimigo.

Gera o Loot e XP ao vencer.

## 2. Gerenciamento do Jogador (models/personagem.py)
```ganhar_xp(self, quantidade)```: Função recursiva que verifica se o XP acumulado ultrapassou o necessário para o próximo nível. Se sim, incrementa o nível, aumenta os atributos base e chama a função de desbloqueio de habilidades.

```equipar_item(self, item)```: Realiza a validação de regras de negócio. Verifica o item se eles está na lista de itens equipaveis. Se for compatível, troca o item do slot correspondente pelo do inventário.

```to_dict() e from_dict()```: Métodos de serialização. Convertem a estrutura complexa de objetos (incluindo itens e atributos aninhados) para um dicionário Python simples, permitindo que o JSON grave os dados.

## 3. Geração de Inimigos (models/inimigo.py)
```gerar_loot(self)```: Define as recompensas após a morte do inimigo. Pode gerar poções ou equipamentos raros baseados em uma lista específica ```(loot_especifico)``` de cada tipo de monstro.

## 4. Persistência (utils/repositorio.py)
```salvar() e carregar()```: Abstraem a manipulação de arquivos. Garantem que a pasta dados/ exista e lidam com a codificação UTF-8 para evitar erros com acentuação nos arquivos JSON.