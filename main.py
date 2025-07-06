"""
Extrator de Dados - Investidor10

Arquivo principal para inicialização da aplicação.
Versão 2.0 - Arquitetura modular com separação de responsabilidades.

Este arquivo contém apenas a inicialização da aplicação,
importando as classes da interface e do extrator de dados.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
from interface_app import InvestidorApp


def carregar_config():
    """Carrega as configurações do arquivo config.json."""
    arquivo_config = "config.json"
    config_padrao = {
        "acoes": [],
        "colunas_personalizadas": [],
        "headless": True,
        "tema": "escuro",
        "mostrar_mensagem_inicial": True
    }

    try:
        
        if os.path.exists(arquivo_config):
            with open(arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Adicionar chave mostrar_mensagem_inicial se não existir
                if "mostrar_mensagem_inicial" not in config:
                    config["mostrar_mensagem_inicial"] = True
                return config
        return config_padrao
    except (json.JSONDecodeError, Exception):
        return config_padrao


def salvar_config(config):
    """Salva as configurações no arquivo config.json."""
    arquivo_config = "config.json"
    try:
        with open(arquivo_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")


def mostrar_mensagem_inicial():
    """Mostra a mensagem inicial sobre configuração do modo headless e login."""
    config = carregar_config()

    if not config.get("mostrar_mensagem_inicial", True):
        return

    # Criar janela personalizada para a mensagem
    janela_msg = tk.Toplevel()
    janela_msg.title("Configuração Inicial - Investidor10")
    janela_msg.geometry("600x400")
    janela_msg.resizable(False, False)
    janela_msg.configure(bg="#f8fafc")

    # Centralizar a janela
    janela_msg.transient()
    janela_msg.grab_set()

    # Garantir que a janela seja independente da janela principal
    janela_msg.lift()
    janela_msg.focus_force()

    # Calcular posição central
    janela_msg.update_idletasks()
    x = (janela_msg.winfo_screenwidth() // 2) - (600 // 2)
    y = (janela_msg.winfo_screenheight() // 2) - (400 // 2)
    janela_msg.geometry(f"600x400+{x}+{y}")

    # Frame principal
    frame_principal = tk.Frame(janela_msg, bg="#f8fafc", padx=30, pady=20)
    frame_principal.pack(fill=tk.BOTH, expand=True)

    # Título
    titulo = tk.Label(frame_principal,
                     text="🔧  Configuração Inicial",
                     font=("Segoe UI", 16, "bold"),
                     bg="#f8fafc", fg="#1e293b")
    titulo.pack(pady=(0, 20))

    # Texto da mensagem
    mensagem = """Para acessar dados pagos e exportar sua carteira de ações do Investidor10, é necessário fazer login no site.

📋 INSTRUÇÕES IMPORTANTES:

1. Para dados que requerem login, você deve DESABILITAR MANUALMENTE o modo headless:
   • Na página inicial, na seção "Opções"
   • Desmarque a opção "🚫 Headless (sem interface)"
   • Isso permitirá que o navegador apareça para login

2. Quando o navegador aparecer (com headless desabilitado):
   • Faça login normalmente no site Investidor10
   • Voltar para o programa e clicar em "OK", para iniciar a extração

3. Dados que requerem login:
   • Informações detalhadas de algumas ações
   • Exportação da carteira pessoal
   • Dados premium do Investidor10

4. Após a primeira extração com login:
   • Você pode reabilitar o modo headless se desejar
   • O programa tentará manter sua sessão para próximas extrações

⚠️ IMPORTANTE: Mantenha suas credenciais seguras e não compartilhe sua conta."""

    texto_msg = tk.Text(frame_principal,
                       wrap=tk.WORD,
                       height=12,
                       width=70,
                       font=("Segoe UI", 10),
                       bg="#ffffff",
                       fg="#1e293b",
                       relief=tk.RIDGE,
                       bd=1,
                       padx=15,
                       pady=15)
    texto_msg.pack(pady=(0, 20), fill=tk.BOTH, expand=True)
    texto_msg.insert(tk.END, mensagem)
    texto_msg.config(state=tk.DISABLED)

    # Frame para checkbox e botões
    frame_inferior = tk.Frame(frame_principal, bg="#f8f9fa")
    frame_inferior.pack(fill=tk.X, pady=(10, 0))

    # Checkbox para não mostrar novamente
    var_nao_mostrar = tk.BooleanVar()
    checkbox = tk.Checkbutton(frame_inferior,
                             text="Não mostrar esta mensagem novamente",
                             variable=var_nao_mostrar,
                             bg="#f8f9fa",
                             fg="#2c3e50",
                             font=("Segoe UI", 9),
                             activebackground="#f8f9fa")
    checkbox.pack(side=tk.LEFT)

    # Frame para botões
    frame_botoes = tk.Frame(frame_inferior, bg="#f8f9fa")
    frame_botoes.pack(side=tk.RIGHT)

    def fechar_janela():
        # Salvar preferência se checkbox marcado
        if var_nao_mostrar.get():
            config["mostrar_mensagem_inicial"] = False
            salvar_config(config)
        janela_msg.destroy()

    # Botão OK
    btn_ok = tk.Button(frame_botoes,
                      text="Entendi",
                      command=fechar_janela,
                      bg="#007bff",
                      fg="white",
                      font=("Segoe UI", 10, "bold"),
                      padx=20,
                      pady=8,
                      relief=tk.FLAT,
                      cursor="hand2")
    btn_ok.pack(side=tk.RIGHT, padx=(10, 0))

    # Botão para mais informações
    def mostrar_mais_info():
        info_adicional = """DETALHES TÉCNICOS:

• O programa usa Selenium WebDriver para automação
• O modo headless deve ser controlado MANUALMENTE pelo usuário
• Suas credenciais não são armazenadas pelo programa
• A sessão é mantida apenas durante a execução
• Dados são extraídos respeitando os termos do site

PROCESSO RECOMENDADO:
1. Para dados públicos: mantenha headless ativado (mais rápido)
2. Para dados pagos/carteira: desative headless na seção "Opções"
3. Faça login quando o navegador aparecer
4. Após extração: pode reativar headless se desejar

DICAS:
• Mantenha o navegador aberto durante a extração
• Não feche a aba do Investidor10 manualmente
• Se houver problemas, reinicie o programa
• Alterne headless conforme sua necessidade"""

        messagebox.showinfo("Informações Adicionais", info_adicional)

    btn_info = tk.Button(frame_botoes,
                        text="Mais Info",
                        command=mostrar_mais_info,
                        bg="#6c757d",
                        fg="white",
                        font=("Segoe UI", 9),
                        padx=15,
                        pady=8,
                        relief=tk.FLAT,
                        cursor="hand2")
    btn_info.pack(side=tk.RIGHT)

    # Aguardar fechamento da janela
    janela_msg.wait_window()


def main():
    """Função principal para inicializar a aplicação."""
    try:
        # Criar janela principal
        root = tk.Tk()

        # Mostrar mensagem inicial antes de criar a aplicação
        root.withdraw()  # Ocultar janela principal temporariamente
        mostrar_mensagem_inicial()

        # Inicializar aplicação (que configurará a geometria)
        app = InvestidorApp(root)

        # Forçar atualização da janela antes de mostrar
        root.update_idletasks()

        # Mostrar janela principal novamente (agora já com posicionamento correto)
        root.deiconify()

        # Garantir que a janela seja centralizada após ser mostrada
        root.after(100, app.centralizar_janela)

        # Iniciar loop principal da interface
        root.mainloop()

    except ImportError as e:
        print(f"Erro de importação: {e}")
        print("Instale as dependências com: pip install -r requirements.txt")
        input("Pressione Enter para fechar...")
    except Exception as e:
        print(f"Erro inesperado ao inicializar a aplicação: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para fechar...")


if __name__ == "__main__":
    main()