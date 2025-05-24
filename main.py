"""
Extrator de Dados - Investidor10

Arquivo principal para inicialização da aplicação.
Versão 2.0 - Arquitetura modular com separação de responsabilidades.

Este arquivo contém apenas a inicialização da aplicação,
importando as classes da interface e do extrator de dados.
"""

import tkinter as tk
from interface_app import InvestidorApp


def main():
    """Função principal para inicializar a aplicação."""
    try:
        # Criar janela principal
        root = tk.Tk()

        # Inicializar aplicação
        app = InvestidorApp(root)

        # Iniciar loop principal da interface
        root.mainloop()

    except Exception as e:
        print(f"Erro ao inicializar a aplicação: {e}")
        input("Pressione Enter para fechar...")


if __name__ == "__main__":
    main()