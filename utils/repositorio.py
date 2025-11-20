from __future__ import annotations
import json
import os
from typing import Any

class Repositorio:
    """
    Gerencia a leitura e escrita de arquivos JSON.
    """

    def salvar(self, dados: dict[str, Any], nome_arquivo: str) -> None:
        # Garante que o nome do arquivo tenha extensão .json
        if not nome_arquivo.endswith(".json"):
            nome_arquivo += ".json"
        
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            print(f"✔ Jogo salvo com sucesso em '{nome_arquivo}'!")
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")

    def carregar(self, nome_arquivo: str) -> dict[str, Any] | None:
        if not nome_arquivo.endswith(".json"):
            nome_arquivo += ".json"

        if not os.path.exists(nome_arquivo):
            print(f"❌ Arquivo '{nome_arquivo}' não encontrado.")
            return None

        try:
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return dados
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return None