from __future__ import annotations
import json
import os
from typing import Any

class Repositorio:
    """
    Gerencia a leitura e escrita de arquivos JSON na pasta 'dados/'.
    """
    DIR_SAVES = "dados"

    def salvar(self, dados: dict[str, Any], nome_arquivo: str) -> None:
        if not nome_arquivo.endswith(".json"):
            nome_arquivo += ".json"
        
        # Garante que a pasta existe
        os.makedirs(self.DIR_SAVES, exist_ok=True)

        # Cria o caminho completo (ex: dados/save1.json)
        caminho_completo = os.path.join(self.DIR_SAVES, nome_arquivo)
        
        try:
            with open(caminho_completo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            print(f"✔ Jogo salvo com sucesso em '{caminho_completo}'!")
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")

    def carregar(self, nome_arquivo: str) -> dict[str, Any] | None:
        if not nome_arquivo.endswith(".json"):
            nome_arquivo += ".json"

        caminho_completo = os.path.join(self.DIR_SAVES, nome_arquivo)

        if not os.path.exists(caminho_completo):
            print(f"❌ Arquivo '{nome_arquivo}' não encontrado na pasta '{self.DIR_SAVES}'.")
            return None

        try:
            with open(caminho_completo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return dados
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return None