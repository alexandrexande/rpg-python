from __future__ import annotations
from datetime import datetime

class Logger:
    """
    Responsável por registrar eventos do jogo em arquivo.log.
    Requisito obrigatório do projeto.
    """
    
    @staticmethod
    def registrar(mensagem: str, nivel: str = "INFO") -> None:
        """
        Escreve a mensagem no arquivo 'jogo.log' com data e hora.
        """
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha_log = f"[{data_hora}] [{nivel}] {mensagem}"
        
        # Escreve no arquivo (append mode)
        try:
            with open("jogo.log", "a", encoding="utf-8") as f:
                f.write(linha_log + "\n")
        except Exception as e:
            print(f"Erro ao gravar log: {e}")

    @staticmethod
    def log_combate(turno: int, atacante: str, defensor: str, dano: int):
        msg = f"Turno {turno}: {atacante} causou {dano} de dano em {defensor}."
        Logger.registrar(msg, "COMBATE")