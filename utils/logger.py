from __future__ import annotations
import os
from datetime import datetime

class Logger:
    #Responsável por registrar eventos do jogo em dados/jogo.log.
    # Define a pasta onde os arquivos ficarão
    DIR_LOG = "dados"

    @staticmethod
    def registrar(mensagem: str, nivel: str = "INFO") -> None:
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha_log = f"[{data_hora}] [{nivel}] {mensagem}"
        
        # Cria a pasta 'dados' se ela não existir
        os.makedirs(Logger.DIR_LOG, exist_ok=True)
        
        # Define o caminho completo: dados/jogo.log
        caminho_arquivo = os.path.join(Logger.DIR_LOG, "jogo.log")

        try:
            with open(caminho_arquivo, "a", encoding="utf-8") as f:
                f.write(linha_log + "\n")
        except Exception as e:
            print(f"Erro ao gravar log: {e}")

    @staticmethod
    def log_combate(turno: int, atacante: str, defensor: str, dano: int):
        msg = f"Turno {turno}: {atacante} causou {dano} de dano em {defensor}."
        Logger.registrar(msg, "COMBATE")