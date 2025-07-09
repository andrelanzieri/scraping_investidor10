import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import os
from tkinter import font as tkfont
import threading
import time
from data_extractor import DataExtractor
from excel_exporter import ExcelExporter
from data_viewer import DataViewer


class ToolTip:
    """Classe para criar tooltips personalizados nos widgets da interface."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        pointer_x = self.widget.winfo_pointerx()
        pointer_y = self.widget.winfo_pointery()
        offset = 25
        tooltip_x_on_screen = pointer_x + offset
        tooltip_y_on_screen = pointer_y + offset

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{tooltip_x_on_screen}+{tooltip_y_on_screen}")

        tooltip_text = self.text
        if hasattr(self.widget, 'tooltip_shortcut'):
            tooltip_text += f"\nAtalho: {self.widget.tooltip_shortcut}"

        label = tk.Label(self.tooltip, text=tooltip_text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"))
        label.pack()

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class InvestidorApp:
    """
    Aplicação Tkinter para interface gráfica do extrator de dados do Investidor10.
    Gerencia a interface do usuário, configurações e coordena a extração de dados.
    """

    def __init__(self, root):
        """Inicializa a aplicação InvestidorApp."""
        self.root = root
        self.root.title("📊 Extrator de Dados - Investidor10")

        # Configurar tamanho da janela
        window_width = 1200
        window_height = 820
        self.root.minsize(1000, 600)

        # Definir tamanho inicial sem posição (será centralizada depois)
        self.root.geometry(f"{window_width}x{window_height}")

        # Armazenar dimensões para uso posterior
        self.window_width = window_width
        self.window_height = window_height

        # Configurar fontes modernas e hierarquia tipográfica
        self.default_font = tkfont.Font(family="Segoe UI", size=10, weight="normal")
        self.root.option_add("*Font", self.default_font)

        # Hierarquia de fontes
        self.title_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.subtitle_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.button_font = tkfont.Font(family="Segoe UI", size=9, weight="normal")
        self.small_font = tkfont.Font(family="Segoe UI", size=8, weight="normal")
        self.large_button_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.monospace_font = tkfont.Font(family="Consolas", size=9, weight="normal")

        # Configurar tema
        self.tema_escuro = True
        self.aplicar_tema()

        # Configurar estilos TTK
        self.style = ttk.Style()
        self.configurar_estilos_ttk()

        # Controle de cancelamento da extração
        self.cancelar_extracao = threading.Event()
        self.extracao_em_andamento = False

        # Carregar configurações
        self.config_file = "config.json"
        self.config = self.carregar_config()

        # Instanciar extrator de dados
        self.data_extractor = None

        # DataFrames para armazenar resultados
        self.df_acoes = pd.DataFrame()
        self.df_fiis = pd.DataFrame()
        self.df_carteiras_acoes = pd.DataFrame()
        self.df_carteiras_fiis = pd.DataFrame()

        # Criar interface
        self.criar_interface()
        self.configurar_atalhos()

    def centralizar_janela(self):
        """Centraliza a janela na tela."""
        try:
            # Forçar atualização completa da janela
            self.root.update_idletasks()
            self.root.update()

            # Usar dimensões armazenadas para garantir consistência
            window_width = getattr(self, 'window_width', 1280)
            window_height = getattr(self, 'window_height', 800)

            # Calcular posição central da tela
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            center_x = int(screen_width/2 - window_width/2)
            center_y = int(screen_height/2 - window_height/2)

            # Garantir que a posição não seja negativa e não saia da tela
            center_x = max(0, min(center_x, screen_width - window_width))
            center_y = max(0, min(center_y, screen_height - window_height))

            # Aplicar nova geometria com dimensões fixas
            self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

            # Forçar a janela para frente
            self.root.lift()
            self.root.focus_force()

            # Atualizar novamente para garantir que as mudanças sejam aplicadas
            self.root.update_idletasks()

        except Exception as e:
            # Em caso de erro, pelo menos garantir que a janela tenha o tamanho correto
            print(f"Erro ao centralizar janela: {e}")
            self.root.geometry(f"{getattr(self, 'window_width', 1280)}x{getattr(self, 'window_height', 800)}")

    def aplicar_tema(self):
        """Aplica o tema claro ou escuro à interface com paleta de cores melhorada e moderna."""
        if self.tema_escuro:
            # Tema escuro moderno com cores mais suaves e harmoniosas
            self.cor_fundo = "#0f1419"                    # Azul muito escuro, quase preto
            self.cor_fundo_secundario = "#1a1f26"         # Azul escuro suave
            self.cor_fundo_terciario = "#252d38"          # Azul acinzentado
            self.cor_texto = "#e8eaed"                    # Branco suave
            self.cor_texto_secundario = "#9aa0a6"         # Cinza claro
            self.cor_texto_terciario = "#5f6368"          # Cinza médio
            self.cor_botao = "#2d3748"                    # Azul acinzentado escuro
            self.cor_botao_hover = "#4a5568"              # Azul acinzentado médio
            self.cor_botao_ativo = "#3182ce"              # Azul vibrante
            self.cor_botao_ativo_hover = "#2c5aa0"        # Azul vibrante escuro
            self.cor_entrada = "#1e2a38"                  # Azul escuro para inputs
            self.cor_entrada_foco = "#2d3748"             # Azul médio para foco
            self.cor_lista = "#1a1f26"                    # Mesmo do fundo secundário
            self.cor_borda = "#374151"                    # Cinza azulado
            self.cor_borda_foco = "#60a5fa"               # Azul claro para foco
            self.cor_destaque = "#3b82f6"                 # Azul moderno
            self.cor_sucesso = "#10b981"                  # Verde moderno
            self.cor_aviso = "#f59e0b"                    # Amarelo moderno
            self.cor_erro = "#ef4444"                     # Vermelho moderno
            self.cor_info = "#06b6d4"                     # Ciano moderno
            self.cor_cabecalho_fundo = "#1f2937"          # Cinza azulado escuro
            self.cor_cabecalho_texto = "#f9fafb"          # Branco quase puro
            self.cor_sombra = "#000000"                   # Preto para sombras
        else:
            # Tema claro moderno com cores mais suaves e profissionais
            self.cor_fundo = "#f8fafc"                    # Cinza muito claro azulado
            self.cor_fundo_secundario = "#ffffff"         # Branco puro
            self.cor_fundo_terciario = "#f1f5f9"          # Cinza claro azulado
            self.cor_texto = "#1e293b"                    # Azul escuro para texto
            self.cor_texto_secundario = "#64748b"         # Cinza azulado
            self.cor_texto_terciario = "#94a3b8"          # Cinza azulado claro
            self.cor_botao = "#e2e8f0"                    # Cinza claro
            self.cor_botao_hover = "#cbd5e1"              # Cinza médio
            self.cor_botao_ativo = "#3b82f6"              # Azul moderno
            self.cor_botao_ativo_hover = "#2563eb"        # Azul moderno escuro
            self.cor_entrada = "#ffffff"                  # Branco puro
            self.cor_entrada_foco = "#f8fafc"             # Cinza muito claro
            self.cor_lista = "#ffffff"                    # Branco puro
            self.cor_borda = "#d1d5db"                    # Cinza claro
            self.cor_borda_foco = "#3b82f6"               # Azul para foco
            self.cor_destaque = "#3b82f6"                 # Azul moderno
            self.cor_sucesso = "#10b981"                  # Verde moderno
            self.cor_aviso = "#f59e0b"                    # Amarelo moderno
            self.cor_erro = "#ef4444"                     # Vermelho moderno
            self.cor_info = "#06b6d4"                     # Ciano moderno
            self.cor_cabecalho_fundo = "#ffffff"          # Branco puro
            self.cor_cabecalho_texto = "#1f2937"          # Cinza escuro
            self.cor_sombra = "#00000010"                 # Preto transparente para sombras

        self.root.configure(bg=self.cor_fundo)

    def configurar_estilos_ttk(self):
        """Configura estilos TTK melhorados e modernos para elementos da interface."""
        if self.tema_escuro:
            try:
                self.style.theme_use('clam')
            except:
                pass
        else:
            try:
                self.style.theme_use('vista' if os.name == 'nt' else 'clam')
            except:
                pass

        # Configurar estilo geral do Notebook (abas)
        self.style.configure("TNotebook",
                           background=self.cor_fundo,
                           borderwidth=0,
                           tabmargins=[2, 5, 2, 0])

        self.style.configure("TNotebook.Tab",
                           background=self.cor_botao,
                           foreground=self.cor_texto,
                           padding=[20, 12],
                           borderwidth=1,
                           focuscolor='none')

        self.style.map("TNotebook.Tab",
                      background=[('selected', self.cor_fundo_secundario),
                                ('active', self.cor_botao_hover)],
                      foreground=[('selected', self.cor_texto),
                                ('active', self.cor_texto)],
                      expand=[('selected', [1, 1, 1, 0])])

        # Estilos para barra de progresso com gradientes visuais
        self.style.configure("red.Horizontal.TProgressbar",
                           troughcolor=self.cor_fundo_terciario,
                           background=self.cor_erro,
                           lightcolor=self.cor_erro,
                           darkcolor=self.cor_erro,
                           borderwidth=1,
                           relief='flat')

        self.style.configure("yellow.Horizontal.TProgressbar",
                           troughcolor=self.cor_fundo_terciario,
                           background=self.cor_aviso,
                           lightcolor=self.cor_aviso,
                           darkcolor=self.cor_aviso,
                           borderwidth=1,
                           relief='flat')

        self.style.configure("green.Horizontal.TProgressbar",
                           troughcolor=self.cor_fundo_terciario,
                           background=self.cor_sucesso,
                           lightcolor=self.cor_sucesso,
                           darkcolor=self.cor_sucesso,
                           borderwidth=1,
                           relief='flat')

        # Configurar Treeview com estilo moderno
        self.style.configure("Custom.Treeview",
                           background=self.cor_lista,
                           foreground=self.cor_texto,
                           fieldbackground=self.cor_lista,
                           borderwidth=1,
                           relief='solid')

        self.style.configure("Custom.Treeview.Heading",
                           background=self.cor_cabecalho_fundo,
                           foreground=self.cor_cabecalho_texto,
                           relief='flat',
                           borderwidth=1)

        self.style.map("Custom.Treeview",
                      background=[('selected', self.cor_destaque)],
                      foreground=[('selected', 'white')])

        self.style.map("Custom.Treeview.Heading",
                      background=[('active', self.cor_botao_hover)])

        # Estilo para Combobox
        self.style.configure("Custom.TCombobox",
                           fieldbackground=self.cor_entrada,
                           background=self.cor_botao,
                           foreground=self.cor_texto)

        self.style.map("Custom.TCombobox",
                      fieldbackground=[('readonly', self.cor_entrada)],
                      selectbackground=[('readonly', self.cor_destaque)],
                      selectforeground=[('readonly', 'white')])

    def configurar_atalhos(self):
        """Configura os atalhos de teclado da aplicação."""
        self.atalhos_funcoes = {
            "<Control-s>": lambda e: self.salvar_configuracoes(),
            "<Control-e>": lambda e: self.start_combined_extraction(),
            "<Control-t>": lambda e: self.alternar_tema(),
            "<Control-q>": lambda e: self.root.destroy(),
            "<Control-a>": lambda e: self.adicionar_acao(),
            "<Control-r>": lambda e: self.remover_acao(),
            "<Control-n>": lambda e: self.adicionar_coluna(),
            "<Delete>": lambda e: self.excluir_coluna()
        }
        self.habilitar_atalhos()

    def habilitar_atalhos(self):
        """Habilita todos os atalhos de teclado."""
        for tecla, funcao in self.atalhos_funcoes.items():
            self.root.bind(tecla, funcao)

    def desabilitar_atalhos(self):
        """Desabilita todos os atalhos de teclado."""
        for tecla in self.atalhos_funcoes.keys():
            self.root.unbind(tecla)
            self.root.bind(tecla, self.atalho_desabilitado)
        if hasattr(self, 'lbl_status'):
            self.atualizar_status("Atalhos de teclado desabilitados durante a extração", None)

    def atalho_desabilitado(self, event):
        """Função para atalhos desabilitados durante extração que mostra aviso."""
        if self.extracao_em_andamento:
            if not hasattr(self, '_ultimo_aviso_atalho') or \
               time.time() - self._ultimo_aviso_atalho > 5:
                self._ultimo_aviso_atalho = time.time()
                self.atualizar_status("⚠️ Atalhos desabilitados durante extração. Use o botão de cancelar se necessário.", None)

    def carregar_config(self):
        """Carrega as configurações do arquivo JSON."""
        default_config_values = {
            "acoes": [],
            "fiis": [],
            "colunas_personalizadas": [],
            "colunas_personalizadas_fiis": [],
            "headless": False,
            "tema": "escuro",
            "mostrar_mensagem_inicial": True
        }
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                if not isinstance(config_data, dict):
                    raise ValueError("O conteúdo do arquivo de configuração não é um dicionário válido.")
        except FileNotFoundError:
            return default_config_values.copy()
        except json.JSONDecodeError as e:
            messagebox.showerror("Erro de Configuração", f"Erro ao ler o arquivo {self.config_file}: {e}. Usando configuração padrão.")
            return default_config_values.copy()
        except ValueError as e:
            messagebox.showerror("Erro de Configuração", f"Erro no formato do arquivo {self.config_file}: {e}. Usando configuração padrão.")
            return default_config_values.copy()

        # Mesclar com padrões
        final_config = default_config_values.copy()
        final_config.update(config_data)

        # Normalizar dados
        if "acoes" in final_config and isinstance(final_config["acoes"], list):
            acoes_normalizadas = []
            for acao_item in final_config["acoes"]:
                if isinstance(acao_item, str):
                    acao_limpa = acao_item.strip().upper()
                    if acao_limpa:
                        acoes_normalizadas.append(acao_limpa)
            final_config["acoes"] = acoes_normalizadas
        else:
            final_config["acoes"] = []

        if "fiis" in final_config and isinstance(final_config["fiis"], list):
            fiis_normalizados = []
            for fii_item in final_config["fiis"]:
                if isinstance(fii_item, str):
                    fii_limpo = fii_item.strip().upper()
                    if fii_limpo:
                        fiis_normalizados.append(fii_limpo)
            final_config["fiis"] = fiis_normalizados
        else:
            final_config["fiis"] = []

        if not isinstance(final_config.get("colunas_personalizadas"), list):
            final_config["colunas_personalizadas"] = []

        if not isinstance(final_config.get("colunas_personalizadas_fiis"), list):
            final_config["colunas_personalizadas_fiis"] = []
        else:
            for coluna in final_config["colunas_personalizadas"]:
                coluna.setdefault("formato_excel", "Texto")

        if final_config.get("tema") not in ["claro", "escuro"]:
            final_config["tema"] = "escuro"

        self.tema_escuro = final_config["tema"] == "escuro"
        self.aplicar_tema()

        if hasattr(self, 'style'):
            self.configurar_estilos_ttk()

        return final_config

    def salvar_config(self):
        """Salva as configurações atuais no arquivo JSON."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def criar_interface(self):
        """Cria a interface gráfica principal da aplicação com design moderno e elegante."""
        # Frame principal com padding otimizado
        main_frame = tk.Frame(self.root, bg=self.cor_fundo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Criar notebook para abas de ações e FIIs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Aba de Ações
        self.tab_acoes = tk.Frame(self.notebook, bg=self.cor_fundo_secundario)
        self.notebook.add(self.tab_acoes, text="📈 Ações")

        # Aba de FIIs
        self.tab_fiis = tk.Frame(self.notebook, bg=self.cor_fundo_secundario)
        self.notebook.add(self.tab_fiis, text="🏢 FIIs")

        # Configurar interfaces das abas (SEM as opções compartilhadas)
        self.configurar_tab_acoes()
        self.configurar_tab_fiis()

        # Criar área compartilhada na parte inferior (ÚNICA)
        self._criar_area_compartilhada_inferior(main_frame)

        # Adicionar menu de ajuda
        self.criar_menu_ajuda()

    def criar_menu_ajuda(self):
        """Cria o menu de ajuda com informações sobre atalhos e uso."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Atalhos de Teclado", command=self.mostrar_atalhos)
        help_menu.add_separator()
        help_menu.add_command(label="Configuração Inicial", command=self.mostrar_configuracao_inicial)
        help_menu.add_separator()
        help_menu.add_command(label="☕ Buy me a Coffee", command=self.mostrar_buy_coffee)
        help_menu.add_separator()
        help_menu.add_command(label="Sobre", command=self.mostrar_sobre)

    def mostrar_atalhos(self):
        """Mostra uma janela com os atalhos de teclado disponíveis."""
        atalhos = """
        Atalhos de Teclado:

        Ctrl + S: Salvar Configurações
        Ctrl + E: Extrair Dados
        Ctrl + T: Alternar Tema
        Ctrl + Q: Sair
        Ctrl + A: Adicionar Ação
        Ctrl + R: Remover Ação
        Ctrl + N: Nova Coluna
        Delete: Excluir Coluna Selecionada

        Nota: Os atalhos são desabilitados
        automaticamente durante a extração
        de dados para evitar interferências.
        """
        messagebox.showinfo("Atalhos de Teclado", atalhos)

    def mostrar_sobre(self):
        """Mostra informações sobre o aplicativo."""
        sobre = """
        Extrator de Dados - Investidor10

        Versão 3.1

        Uma ferramenta para extrair dados de ações e carteiras
        do site Investidor10.

        Desenvolvido com Python e Tkinter.
        Arquitetura modular com separação de responsabilidades.
                """
        messagebox.showinfo("Sobre", sobre)

    def mostrar_buy_coffee(self):
        """Mostra a janela de apoio ao projeto com QR Code do PIX."""
        import os
        from tkinter import Label
        from PIL import Image, ImageTk

        # Criar janela personalizada
        janela_coffee = tk.Toplevel(self.root)
        janela_coffee.title("☕ Apoie o Projeto - Buy me a Coffee")
        janela_coffee.geometry("500x750")
        janela_coffee.resizable(False, False)
        janela_coffee.configure(bg=self.cor_fundo)

        # Centralizar a janela
        janela_coffee.transient(self.root)
        janela_coffee.grab_set()

        # Calcular posição central
        janela_coffee.update_idletasks()
        x = (janela_coffee.winfo_screenwidth() // 2) - (500 // 2)
        y = (janela_coffee.winfo_screenheight() // 2) - (750 // 2)
        janela_coffee.geometry(f"500x650+{x}+{y}")

        # Frame principal
        frame_principal = tk.Frame(janela_coffee, bg=self.cor_fundo, padx=30, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = tk.Label(frame_principal,
                         text="☕ Apoie o Projeto",
                         font=("Segoe UI", 18, "bold"),
                         bg=self.cor_fundo, fg=self.cor_texto)
        titulo.pack(pady=(0, 10))

        # Subtítulo
        subtitulo = tk.Label(frame_principal,
                           text="Buy me a Coffee",
                           font=("Segoe UI", 14),
                           bg=self.cor_fundo, fg=self.cor_texto_secundario)
        subtitulo.pack(pady=(0, 20))

        # Texto de motivação
        motivacao = """Se este projeto foi útil para você e quiser apoiar o
desenvolvimento contínuo, considere fazer uma doação via PIX! ❤️"""

        texto_motivacao = tk.Label(frame_principal,
                                 text=motivacao,
                                 font=("Segoe UI", 11),
                                 bg=self.cor_fundo, fg=self.cor_texto,
                                 wraplength=400, justify=tk.CENTER)
        texto_motivacao.pack(pady=(0, 20))

        # Tentar carregar e exibir a imagem do QR Code
        try:
            caminho_imagem = os.path.join("screenshots", "coffee.png")
            if os.path.exists(caminho_imagem):
                # Abrir imagem e redimensionar se necessário
                img = Image.open(caminho_imagem)

                # Redimensionar mantendo proporção (máximo 300x300)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                label_img = tk.Label(frame_principal, image=photo, bg=self.cor_fundo)
                label_img.image = photo  # Manter referência
                label_img.pack(pady=(0, 20))
            else:
                # Se a imagem não existir, mostrar texto alternativo
                label_img = tk.Label(frame_principal,
                                   text="📱 QR Code PIX\n\n(Imagem não encontrada: screenshots/coffee.png)",
                                   font=("Segoe UI", 12),
                                   bg=self.cor_fundo_secundario,
                                   fg=self.cor_texto,
                                   relief=tk.RIDGE,
                                   bd=1,
                                   padx=20,
                                   pady=30)
                label_img.pack(pady=(0, 20))
        except ImportError:
            # Se PIL não estiver disponível, mostrar texto
            label_img = tk.Label(frame_principal,
                               text="📱 QR Code PIX\n\n(Para visualizar o QR Code, instale a biblioteca Pillow:\npip install Pillow)",
                               font=("Segoe UI", 11),
                               bg=self.cor_fundo_secundario,
                               fg=self.cor_texto,
                               relief=tk.RIDGE,
                               bd=1,
                               padx=20,
                               pady=20,
                               wraplength=350,
                               justify=tk.CENTER)
            label_img.pack(pady=(0, 20))
        except Exception as e:
            # Em caso de outros erros
            label_img = tk.Label(frame_principal,
                               text=f"📱 QR Code PIX\n\n(Erro ao carregar imagem: {str(e)})",
                               font=("Segoe UI", 11),
                               bg=self.cor_fundo_secundario,
                               fg=self.cor_texto,
                               relief=tk.RIDGE,
                               bd=1,
                               padx=20,
                               pady=20,
                               wraplength=350,
                               justify=tk.CENTER)
            label_img.pack(pady=(0, 20))

        # Instrução
        instrucao = tk.Label(frame_principal,
                           text="📱 Escaneie o QR Code acima com seu app bancário",
                           font=("Segoe UI", 12, "bold"),
                           bg=self.cor_fundo, fg=self.cor_destaque)
        instrucao.pack(pady=(0, 15))

        # Benefícios
        beneficios = """🎯 Por que apoiar?

🚀 Desenvolvimento contínuo - Novas funcionalidades
🐛 Correção de bugs - Manutenção e estabilidade
📚 Documentação - Guias e tutoriais detalhados
💡 Suporte à comunidade - Resposta a dúvidas
🤖 Recursos de IA - Melhoria das funcionalidades"""

        texto_beneficios = tk.Label(frame_principal,
                                  text=beneficios,
                                  font=("Segoe UI", 10),
                                  bg=self.cor_fundo, fg=self.cor_texto_secundario,
                                  justify=tk.LEFT)
        texto_beneficios.pack(pady=(0, 20))

        # Botão fechar
        btn_fechar = tk.Button(frame_principal,
                              text="Fechar",
                              command=janela_coffee.destroy,
                              bg=self.cor_botao_ativo,
                              fg="white",
                              font=("Segoe UI", 12, "bold"),
                              padx=30,
                              pady=10,
                              relief=tk.FLAT,
                              cursor="hand2")
        btn_fechar.pack()



    def mostrar_configuracao_inicial(self):
        """Mostra a mensagem de configuração inicial e permite reativar as notificações."""
        import json
        import os

        # Carregar configurações atuais do config.json
        arquivo_config = "config.json"
        config_atual = self.config.copy()  # Usar configuração já carregada pela aplicação

        # Garantir que a chave existe
        if "mostrar_mensagem_inicial" not in config_atual:
            config_atual["mostrar_mensagem_inicial"] = True

        # Criar janela personalizada
        janela_config = tk.Toplevel(self.root)
        janela_config.title("Configuração Inicial - Investidor10")
        janela_config.geometry("600x450")
        janela_config.resizable(False, False)
        janela_config.configure(bg=self.cor_fundo)

        # Centralizar a janela
        janela_config.transient(self.root)
        janela_config.grab_set()

        # Calcular posição central
        janela_config.update_idletasks()
        x = (janela_config.winfo_screenwidth() // 2) - (600 // 2)
        y = (janela_config.winfo_screenheight() // 2) - (450 // 2)
        janela_config.geometry(f"600x450+{x}+{y}")

        # Frame principal
        frame_principal = tk.Frame(janela_config, bg=self.cor_fundo, padx=30, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = tk.Label(frame_principal,
                         text="🔧 Configuração Inicial",
                         font=("Segoe UI", 16, "bold"),
                         bg=self.cor_fundo, fg=self.cor_texto)
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
   • Conforme
   • O programa continuará automaticamente após o login

3. Dados que requerem login:
   • Informações detalhadas de algumas ações
   • Exportação da carteira pessoal
   • Dados premium do Investidor10

4. Após a primeira extração com login:
   • Você pode reabilitar o modo headless se desejar
   • O programa tentará manter sua sessão para próximas extrações

5. Configuração atual:
   • Modo headless está ATIVADO no config.json
   • Para dados pagos: desabilite manualmente na seção "Opções"
   • Para dados públicos: pode manter habilitado

⚠️ IMPORTANTE: Mantenha suas credenciais seguras e não compartilhe sua conta."""

        texto_msg = tk.Text(frame_principal,
                           wrap=tk.WORD,
                           height=12,
                           width=70,
                           font=("Segoe UI", 10),
                           bg=self.cor_fundo_secundario,
                           fg=self.cor_texto,
                           relief=tk.RIDGE,
                           bd=1,
                           padx=15,
                           pady=15)
        texto_msg.pack(pady=(0, 20), fill=tk.BOTH, expand=True)
        texto_msg.insert(tk.END, mensagem)
        texto_msg.config(state=tk.DISABLED)

        # Frame para configurações
        frame_config = tk.Frame(frame_principal, bg=self.cor_fundo)
        frame_config.pack(fill=tk.X, pady=(10, 0))

        # Status atual
        status_atual = "ATIVADA" if config_atual.get("mostrar_mensagem_inicial", True) else "DESATIVADA"
        lbl_status = tk.Label(frame_config,
                             text=f"Status atual da mensagem inicial: {status_atual}",
                             bg=self.cor_fundo,
                             fg=self.cor_texto_secundario,
                             font=("Segoe UI", 9))
        lbl_status.pack(pady=(0, 10))

        # Frame para botões
        frame_botoes = tk.Frame(frame_config, bg=self.cor_fundo)
        frame_botoes.pack(fill=tk.X)

        def reativar_mensagem():
            try:
                # Atualizar configuração local e global
                config_atual["mostrar_mensagem_inicial"] = True
                self.config["mostrar_mensagem_inicial"] = True

                # Salvar no arquivo config.json
                with open(arquivo_config, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)

                messagebox.showinfo("Sucesso", "Mensagem inicial reativada! Será exibida na próxima inicialização do programa.")
                janela_config.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar configuração: {e}")

        def fechar_janela():
            janela_config.destroy()

        # Botão para reativar
        btn_reativar = tk.Button(frame_botoes,
                               text="🔄 Reativar Mensagem",
                               command=reativar_mensagem,
                               bg=self.cor_sucesso,
                               fg="white",
                               font=("Segoe UI", 10, "bold"),
                               padx=20,
                               pady=8,
                               relief=tk.FLAT,
                               cursor="hand2")
        btn_reativar.pack(side=tk.LEFT, padx=(0, 10))

        # Botão fechar
        btn_fechar = tk.Button(frame_botoes,
                              text="Fechar",
                              command=fechar_janela,
                              bg=self.cor_botao,
                              fg=self.cor_texto,
                              font=("Segoe UI", 10),
                              padx=20,
                              pady=8,
                              relief=tk.FLAT,
                              cursor="hand2")
        btn_fechar.pack(side=tk.RIGHT)

    def configurar_tab_acoes(self):
        """Configura a aba de ações com layout moderno e responsivo."""
        # Container principal com padding otimizado
        container_principal = tk.Frame(self.tab_acoes, bg=self.cor_fundo_secundario)
        container_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Frame principal com duas colunas para Ações e Colunas Personalizadas
        config_frame_principal = tk.Frame(container_principal, bg=self.cor_fundo_secundario)
        config_frame_principal.pack(fill=tk.BOTH, expand=True)

        # Coluna esquerda - Ações
        self._criar_frame_acoes_ui(config_frame_principal)

        # Coluna direita - Colunas personalizadas
        self._criar_frame_colunas_ui(config_frame_principal)

        # Configurar grid weights para as colunas de Ações e Colunas Personalizadas
        config_frame_principal.grid_columnconfigure(0, weight=1)
        config_frame_principal.grid_columnconfigure(1, weight=2)  # Colunas personalizadas precisam de mais espaço
        config_frame_principal.grid_rowconfigure(0, weight=1)

        self.atualizar_contador_acoes()

    def configurar_tab_fiis(self):
        """Configura a aba de FIIs com layout moderno e responsivo."""
        # Container principal com padding otimizado
        container_principal = tk.Frame(self.tab_fiis, bg=self.cor_fundo_secundario)
        container_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Frame principal com duas colunas para FIIs e Colunas Personalizadas
        config_frame_principal = tk.Frame(container_principal, bg=self.cor_fundo_secundario)
        config_frame_principal.pack(fill=tk.BOTH, expand=True)

        # Coluna esquerda - FIIs
        self._criar_frame_fiis_ui(config_frame_principal)

        # Coluna direita - Colunas personalizadas para FIIs
        self._criar_frame_colunas_fiis_ui(config_frame_principal)

        # Configurar grid weights para as colunas de FIIs e Colunas Personalizadas
        config_frame_principal.grid_columnconfigure(0, weight=1)
        config_frame_principal.grid_columnconfigure(1, weight=2)  # Colunas personalizadas precisam de mais espaço
        config_frame_principal.grid_rowconfigure(0, weight=1)

        self.atualizar_contador_fiis()

    def _criar_frame_acoes_ui(self, parent_frame):
        """Cria o frame de ações com design moderno e elegante."""
        frame_acoes = tk.LabelFrame(parent_frame, text="📈  Ações", bg=self.cor_fundo_secundario,
                                   fg=self.cor_texto, font=self.title_font,
                                   relief=tk.FLAT, bd=2, highlightbackground=self.cor_borda,
                                   padx=15, pady=15)
        frame_acoes.grid(row=0, column=0, padx=(0, 15), pady=0, sticky="nsew")

        # Container para lista de ações com estilo moderno
        container_lista = tk.Frame(frame_acoes, bg=self.cor_fundo_secundario)
        container_lista.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Frame para lista e scrollbar
        frame_lista_acoes = tk.Frame(container_lista, bg=self.cor_fundo_secundario)
        frame_lista_acoes.pack(fill=tk.BOTH, expand=True)

        # Scrollbar com estilo moderno
        scrollbar = tk.Scrollbar(frame_lista_acoes, bg=self.cor_botao,
                                troughcolor=self.cor_fundo_terciario,
                                activebackground=self.cor_botao_hover,
                                width=14)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))

        self.listbox_acoes = tk.Listbox(frame_lista_acoes,
                                         bg=self.cor_lista,
                                         fg=self.cor_texto,
                                         selectbackground=self.cor_destaque,
                                         selectforeground="white",
                                         height=18,
                                         width=28,
                                         yscrollcommand=scrollbar.set,
                                         relief=tk.FLAT,
                                         bd=1,
                                         highlightthickness=1,
                                         highlightcolor=self.cor_borda_foco,
                                         font=self.default_font,
                                         activestyle='none')
        self.listbox_acoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox_acoes.yview)

        # Adicionar tooltip para a lista de ações
        ToolTip(self.listbox_acoes, "Lista de ações para extração de dados\nClique para selecionar")
        self.listbox_acoes.tooltip_shortcut = "Ctrl+A para adicionar, Ctrl+R para remover"

        for acao in self.config["acoes"]:
            self.listbox_acoes.insert(tk.END, acao)

        # Frame contador com estilo moderno
        frame_contador_acoes = tk.Frame(frame_acoes, bg=self.cor_fundo_secundario)
        frame_contador_acoes.pack(fill=tk.X, pady=(0, 10))

        self.lbl_contador_acoes = tk.Label(frame_contador_acoes, text="Ações: 0",
                                          bg=self.cor_fundo_secundario,
                                          fg=self.cor_texto_secundario,
                                          font=self.small_font)
        self.lbl_contador_acoes.pack(side=tk.LEFT)

        # Frame controle com layout moderno
        frame_controle_acoes = tk.Frame(frame_acoes, bg=self.cor_fundo_secundario)
        frame_controle_acoes.pack(fill=tk.X)

        # Campo de entrada com design moderno
        self.entry_acao = tk.Entry(frame_controle_acoes,
                                  bg=self.cor_entrada,
                                  fg=self.cor_texto,
                                  relief=tk.FLAT,
                                  bd=1,
                                  highlightthickness=2,
                                  highlightcolor=self.cor_borda_foco,
                                  highlightbackground=self.cor_borda,
                                  font=self.default_font,
                                  insertbackground=self.cor_texto)
        self.entry_acao.pack(fill=tk.X, pady=(0, 8))
        ToolTip(self.entry_acao, "Digite o código da ação (ex: PETR4)")

        # Frame para botões com design moderno
        frame_botoes_acoes = tk.Frame(frame_controle_acoes, bg=self.cor_fundo_secundario)
        frame_botoes_acoes.pack(fill=tk.X)

        btn_adicionar_acao = tk.Button(frame_botoes_acoes,
                                       text="➕  Adicionar",
                                       command=self.adicionar_acao,
                                       bg=self.cor_botao,
                                       fg=self.cor_texto,
                                       font=self.button_font,
                                       relief=tk.FLAT,
                                       bd=0,
                                       padx=15,
                                       pady=6,
                                       activebackground=self.cor_botao_hover,
                                       activeforeground=self.cor_texto,
                                       cursor="hand2")
        btn_adicionar_acao.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ToolTip(btn_adicionar_acao, "Adiciona uma nova ação à lista")
        btn_adicionar_acao.tooltip_shortcut = "Ctrl+A"

        btn_remover_acao = tk.Button(frame_botoes_acoes,
                                     text="➖  Remover",
                                     command=self.remover_acao,
                                     bg=self.cor_botao,
                                     fg=self.cor_texto,
                                     font=self.button_font,
                                     relief=tk.FLAT,
                                     bd=0,
                                     padx=15,
                                     pady=6,
                                     activebackground=self.cor_botao_hover,
                                     activeforeground=self.cor_texto,
                                     cursor="hand2")
        btn_remover_acao.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        ToolTip(btn_remover_acao, "Remove a ação selecionada da lista")
        btn_remover_acao.tooltip_shortcut = "Ctrl+R"

        return frame_acoes

    def _criar_frame_colunas_ui(self, parent_frame):
        """Cria o frame de colunas personalizadas com design moderno."""
        frame_colunas = tk.LabelFrame(parent_frame, text="🔧  Colunas Personalizadas",
                                     bg=self.cor_fundo_secundario, fg=self.cor_texto,
                                     font=self.title_font, relief=tk.FLAT, bd=2,
                                     highlightbackground=self.cor_borda, padx=15, pady=15)
        frame_colunas.grid(row=0, column=1, padx=(15, 0), pady=0, sticky="nsew")

        # Container para treeview com estilo moderno
        container_tree = tk.Frame(frame_colunas, bg=self.cor_fundo_secundario)
        container_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        frame_lista_colunas = tk.Frame(container_tree, bg=self.cor_fundo_secundario)
        frame_lista_colunas.pack(fill=tk.BOTH, expand=True)

        self.tree_colunas = ttk.Treeview(frame_lista_colunas,
                                        columns=("Nome", "Tipo", "Seletor CSS", "Formato Excel"),
                                        show="headings", height=15, style="Custom.Treeview")

        # Configurar cabeçalhos com ícones e melhor tipografia
        self.tree_colunas.heading("Nome", text="📝  Nome")
        self.tree_colunas.heading("Tipo", text="🔍  Tipo")
        self.tree_colunas.heading("Seletor CSS", text="🎯  Seletor CSS")
        self.tree_colunas.heading("Formato Excel", text="📊  Formato Excel")

        # Ajustar larguras das colunas com proporções melhores
        self.tree_colunas.column("Nome", width=140, minwidth=110)
        self.tree_colunas.column("Tipo", width=90, minwidth=80)
        self.tree_colunas.column("Seletor CSS", width=300, minwidth=220)
        self.tree_colunas.column("Formato Excel", width=130, minwidth=110)

        # Scrollbar moderno
        scrollbar_colunas = tk.Scrollbar(frame_lista_colunas,
                                        command=self.tree_colunas.yview,
                                        bg=self.cor_botao,
                                        troughcolor=self.cor_fundo_terciario,
                                        activebackground=self.cor_botao_hover,
                                        width=14)
        self.tree_colunas.configure(yscrollcommand=scrollbar_colunas.set)

        scrollbar_colunas.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        self.tree_colunas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ToolTip(self.tree_colunas, "Lista de colunas personalizadas para extração\nDuplo clique para editar")
        self.tree_colunas.tooltip_shortcut = "Ctrl+N para adicionar, Del para excluir"

        for coluna in self.config["colunas_personalizadas"]:
            self.tree_colunas.insert("", tk.END, values=(coluna["nome"], coluna["tipo"],
                                                        coluna.get("seletor_css", ""),
                                                        coluna.get("formato_excel", "Texto")))

        # Frame para botões com design moderno
        frame_botoes_colunas = tk.Frame(frame_colunas, bg=self.cor_fundo_secundario)
        frame_botoes_colunas.pack(fill=tk.X)

        # Primeira linha de botões - ações principais
        frame_botoes_linha1 = tk.Frame(frame_botoes_colunas, bg=self.cor_fundo_secundario)
        frame_botoes_linha1.pack(fill=tk.X, pady=(0, 8))

        btn_adicionar_coluna = tk.Button(frame_botoes_linha1,
                                        text="➕  Adicionar",
                                        command=self.adicionar_coluna,
                                        bg=self.cor_botao,
                                        fg=self.cor_texto,
                                        font=self.button_font,
                                        relief=tk.FLAT,
                                        bd=0,
                                        padx=12,
                                        pady=6,
                                        activebackground=self.cor_botao_hover,
                                        activeforeground=self.cor_texto,
                                        cursor="hand2")
        btn_adicionar_coluna.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ToolTip(btn_adicionar_coluna, "Adiciona uma nova coluna personalizada")
        btn_adicionar_coluna.tooltip_shortcut = "Ctrl+N"

        btn_editar_coluna = tk.Button(frame_botoes_linha1,
                                     text="✏️  Editar",
                                     command=self.editar_coluna,
                                     bg=self.cor_botao,
                                     fg=self.cor_texto,
                                     font=self.button_font,
                                     relief=tk.FLAT,
                                     bd=0,
                                     padx=12,
                                     pady=6,
                                     activebackground=self.cor_botao_hover,
                                     activeforeground=self.cor_texto,
                                     cursor="hand2")
        btn_editar_coluna.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))
        ToolTip(btn_editar_coluna, "Edita a coluna selecionada")

        btn_excluir_coluna = tk.Button(frame_botoes_linha1,
                                      text="🗑️  Excluir",
                                      command=self.excluir_coluna,
                                      bg=self.cor_botao,
                                      fg=self.cor_texto,
                                      font=self.button_font,
                                      relief=tk.FLAT,
                                      bd=0,
                                      padx=12,
                                      pady=6,
                                      activebackground=self.cor_botao_hover,
                                      activeforeground=self.cor_texto,
                                      cursor="hand2")
        btn_excluir_coluna.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        ToolTip(btn_excluir_coluna, "Exclui a coluna selecionada")
        btn_excluir_coluna.tooltip_shortcut = "Del"

        # Segunda linha de botões - movimentação
        frame_botoes_linha2 = tk.Frame(frame_botoes_colunas, bg=self.cor_fundo_secundario)
        frame_botoes_linha2.pack(fill=tk.X)

        btn_mover_cima = tk.Button(frame_botoes_linha2,
                                  text="⬆️  Mover Acima",
                                  command=lambda: self.mover_coluna(-1),
                                  bg=self.cor_botao,
                                  fg=self.cor_texto,
                                  font=self.button_font,
                                  relief=tk.FLAT,
                                  bd=0,
                                  padx=12,
                                  pady=6,
                                  activebackground=self.cor_botao_hover,
                                  activeforeground=self.cor_texto,
                                  cursor="hand2")
        btn_mover_cima.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ToolTip(btn_mover_cima, "Move a coluna selecionada para cima")

        btn_mover_baixo = tk.Button(frame_botoes_linha2,
                                   text="⬇️  Mover Abaixo",
                                   command=lambda: self.mover_coluna(1),
                                   bg=self.cor_botao,
                                   fg=self.cor_texto,
                                   font=self.button_font,
                                   relief=tk.FLAT,
                                   bd=0,
                                   padx=12,
                                   pady=6,
                                   activebackground=self.cor_botao_hover,
                                   activeforeground=self.cor_texto,
                                   cursor="hand2")
        btn_mover_baixo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        ToolTip(btn_mover_baixo, "Move a coluna selecionada para baixo")

        return frame_colunas

    def _criar_frame_fiis_ui(self, parent_frame):
        """Cria o frame de FIIs com design moderno e elegante."""
        frame_fiis = tk.LabelFrame(parent_frame, text="🏢  FIIs", bg=self.cor_fundo_secundario,
                                   fg=self.cor_texto, font=self.title_font,
                                   relief=tk.FLAT, bd=2, highlightbackground=self.cor_borda,
                                   padx=15, pady=15)
        frame_fiis.grid(row=0, column=0, padx=(0, 15), pady=0, sticky="nsew")

        # Container para lista de FIIs com estilo moderno
        container_lista = tk.Frame(frame_fiis, bg=self.cor_fundo_secundario)
        container_lista.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Frame para lista e scrollbar
        frame_lista_fiis = tk.Frame(container_lista, bg=self.cor_fundo_secundario)
        frame_lista_fiis.pack(fill=tk.BOTH, expand=True)

        # Scrollbar com estilo moderno
        scrollbar = tk.Scrollbar(frame_lista_fiis, bg=self.cor_botao,
                                troughcolor=self.cor_fundo_terciario,
                                activebackground=self.cor_botao_hover,
                                width=14)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))

        self.listbox_fiis = tk.Listbox(frame_lista_fiis,
                                         bg=self.cor_lista,
                                         fg=self.cor_texto,
                                         selectbackground=self.cor_destaque,
                                         selectforeground="white",
                                         height=18,
                                         width=28,
                                         yscrollcommand=scrollbar.set,
                                         relief=tk.FLAT,
                                         bd=1,
                                         highlightthickness=1,
                                         highlightcolor=self.cor_borda_foco,
                                         font=self.default_font,
                                         activestyle='none')
        self.listbox_fiis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox_fiis.yview)

        # Adicionar tooltip para a lista de FIIs
        ToolTip(self.listbox_fiis, "Lista de FIIs para extração de dados\nClique para selecionar")
        self.listbox_fiis.tooltip_shortcut = "Ctrl+F para adicionar, Ctrl+D para remover"

        for fii in self.config["fiis"]:
            self.listbox_fiis.insert(tk.END, fii)

        # Frame contador com estilo moderno
        frame_contador_fiis = tk.Frame(frame_fiis, bg=self.cor_fundo_secundario)
        frame_contador_fiis.pack(fill=tk.X, pady=(0, 10))

        self.lbl_contador_fiis = tk.Label(frame_contador_fiis, text="FIIs: 0",
                                          bg=self.cor_fundo_secundario,
                                          fg=self.cor_texto_secundario,
                                          font=self.small_font)
        self.lbl_contador_fiis.pack(side=tk.LEFT)

        # Frame controle com layout moderno
        frame_controle_fiis = tk.Frame(frame_fiis, bg=self.cor_fundo_secundario)
        frame_controle_fiis.pack(fill=tk.X)

        # Campo de entrada com design moderno
        self.entry_fii = tk.Entry(frame_controle_fiis,
                                  bg=self.cor_entrada,
                                  fg=self.cor_texto,
                                  relief=tk.FLAT,
                                  bd=1,
                                  highlightthickness=2,
                                  highlightcolor=self.cor_borda_foco,
                                  highlightbackground=self.cor_borda,
                                  font=self.default_font,
                                  insertbackground=self.cor_texto)
        self.entry_fii.pack(fill=tk.X, pady=(0, 8))
        ToolTip(self.entry_fii, "Digite o código do FII (ex: HGLG11)")

        # Frame para botões com design moderno
        frame_botoes_fiis = tk.Frame(frame_controle_fiis, bg=self.cor_fundo_secundario)
        frame_botoes_fiis.pack(fill=tk.X)

        btn_adicionar_fii = tk.Button(frame_botoes_fiis,
                                       text="➕  Adicionar",
                                       command=self.adicionar_fii,
                                       bg=self.cor_botao,
                                       fg=self.cor_texto,
                                       font=self.button_font,
                                       relief=tk.FLAT,
                                       bd=0,
                                       padx=15,
                                       pady=6,
                                       activebackground=self.cor_botao_hover,
                                       activeforeground=self.cor_texto,
                                       cursor="hand2")
        btn_adicionar_fii.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ToolTip(btn_adicionar_fii, "Adiciona um novo FII à lista")
        btn_adicionar_fii.tooltip_shortcut = "Ctrl+F"

        btn_remover_fii = tk.Button(frame_botoes_fiis,
                                     text="➖  Remover",
                                     command=self.remover_fii,
                                     bg=self.cor_botao,
                                     fg=self.cor_texto,
                                     font=self.button_font,
                                     relief=tk.FLAT,
                                     bd=0,
                                     padx=15,
                                     pady=6,
                                     activebackground=self.cor_botao_hover,
                                     activeforeground=self.cor_texto,
                                     cursor="hand2")
        btn_remover_fii.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        ToolTip(btn_remover_fii, "Remove o FII selecionado da lista")
        btn_remover_fii.tooltip_shortcut = "Ctrl+D"

        return frame_fiis

    def _criar_frame_colunas_fiis_ui(self, parent_frame):
        """Cria o frame de colunas personalizadas para FIIs com design moderno."""
        frame_colunas = tk.LabelFrame(parent_frame, text="🔧  Colunas Personalizadas (FIIs)",
                                     bg=self.cor_fundo_secundario, fg=self.cor_texto,
                                     font=self.title_font, relief=tk.FLAT, bd=2,
                                     highlightbackground=self.cor_borda, padx=15, pady=15)
        frame_colunas.grid(row=0, column=1, padx=(15, 0), pady=0, sticky="nsew")

        # Container para treeview com estilo moderno
        container_tree = tk.Frame(frame_colunas, bg=self.cor_fundo_secundario)
        container_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        frame_lista_colunas = tk.Frame(container_tree, bg=self.cor_fundo_secundario)
        frame_lista_colunas.pack(fill=tk.BOTH, expand=True)

        self.tree_colunas_fiis = ttk.Treeview(frame_lista_colunas,
                                        columns=("Nome", "Tipo", "Seletor CSS", "Formato Excel"),
                                        show="headings", height=15, style="Custom.Treeview")

        # Configurar cabeçalhos com ícones e melhor tipografia
        self.tree_colunas_fiis.heading("Nome", text="📝  Nome")
        self.tree_colunas_fiis.heading("Tipo", text="🔍  Tipo")
        self.tree_colunas_fiis.heading("Seletor CSS", text="🎯  Seletor CSS")
        self.tree_colunas_fiis.heading("Formato Excel", text="📊  Formato Excel")

        # Ajustar larguras das colunas com proporções melhores
        self.tree_colunas_fiis.column("Nome", width=140, minwidth=110)
        self.tree_colunas_fiis.column("Tipo", width=90, minwidth=80)
        self.tree_colunas_fiis.column("Seletor CSS", width=300, minwidth=220)
        self.tree_colunas_fiis.column("Formato Excel", width=130, minwidth=110)

        # Scrollbar moderno
        scrollbar_colunas = tk.Scrollbar(frame_lista_colunas,
                                        command=self.tree_colunas_fiis.yview,
                                        bg=self.cor_botao,
                                        troughcolor=self.cor_fundo_terciario,
                                        activebackground=self.cor_botao_hover,
                                        width=14)
        self.tree_colunas_fiis.configure(yscrollcommand=scrollbar_colunas.set)

        scrollbar_colunas.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        self.tree_colunas_fiis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ToolTip(self.tree_colunas_fiis, "Lista de colunas personalizadas para extração de FIIs\nDuplo clique para editar")
        self.tree_colunas_fiis.tooltip_shortcut = "Ctrl+M para adicionar, Del para excluir"

        for coluna in self.config["colunas_personalizadas_fiis"]:
            self.tree_colunas_fiis.insert("", tk.END, values=(coluna["nome"], coluna["tipo"],
                                                        coluna.get("seletor_css", ""),
                                                        coluna.get("formato_excel", "Texto")))

        # Frame para botões com design moderno
        frame_botoes_colunas = tk.Frame(frame_colunas, bg=self.cor_fundo_secundario)
        frame_botoes_colunas.pack(fill=tk.X)

        # Primeira linha de botões - ações principais
        frame_botoes_linha1 = tk.Frame(frame_botoes_colunas, bg=self.cor_fundo_secundario)
        frame_botoes_linha1.pack(fill=tk.X, pady=(0, 8))

        btn_adicionar_coluna = tk.Button(frame_botoes_linha1,
                                        text="➕  Adicionar",
                                        command=self.adicionar_coluna_fii,
                                        bg=self.cor_botao,
                                        fg=self.cor_texto,
                                        font=self.button_font,
                                        relief=tk.FLAT,
                                        bd=0,
                                        padx=12,
                                        pady=6,
                                        activebackground=self.cor_botao_hover,
                                        activeforeground=self.cor_texto,
                                        cursor="hand2")
        btn_adicionar_coluna.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ToolTip(btn_adicionar_coluna, "Adiciona uma nova coluna personalizada para FIIs")
        btn_adicionar_coluna.tooltip_shortcut = "Ctrl+M"

        btn_editar_coluna = tk.Button(frame_botoes_linha1,
                                     text="✏️  Editar",
                                     command=self.editar_coluna_fii,
                                     bg=self.cor_botao,
                                     fg=self.cor_texto,
                                     font=self.button_font,
                                     relief=tk.FLAT,
                                     bd=0,
                                     padx=12,
                                     pady=6,
                                     activebackground=self.cor_botao_hover,
                                     activeforeground=self.cor_texto,
                                     cursor="hand2")
        btn_editar_coluna.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))
        ToolTip(btn_editar_coluna, "Edita a coluna selecionada")

        btn_excluir_coluna = tk.Button(frame_botoes_linha1,
                                      text="🗑️  Excluir",
                                      command=self.excluir_coluna_fii,
                                      bg=self.cor_botao,
                                      fg=self.cor_texto,
                                      font=self.button_font,
                                      relief=tk.FLAT,
                                      bd=0,
                                      padx=12,
                                      pady=6,
                                      activebackground=self.cor_botao_hover,
                                      activeforeground=self.cor_texto,
                                      cursor="hand2")
        btn_excluir_coluna.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        ToolTip(btn_excluir_coluna, "Exclui a coluna selecionada")
        btn_excluir_coluna.tooltip_shortcut = "Del"

        # Segunda linha de botões - movimentação
        frame_botoes_linha2 = tk.Frame(frame_botoes_colunas, bg=self.cor_fundo_secundario)
        frame_botoes_linha2.pack(fill=tk.X)

        btn_mover_cima = tk.Button(frame_botoes_linha2,
                                  text="⬆️  Mover Acima",
                                  command=lambda: self.mover_coluna_fii(-1),
                                  bg=self.cor_botao,
                                  fg=self.cor_texto,
                                  font=self.button_font,
                                  relief=tk.FLAT,
                                  bd=0,
                                  padx=12,
                                  pady=6,
                                  activebackground=self.cor_botao_hover,
                                  activeforeground=self.cor_texto,
                                  cursor="hand2")
        btn_mover_cima.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ToolTip(btn_mover_cima, "Move a coluna selecionada para cima")

        btn_mover_baixo = tk.Button(frame_botoes_linha2,
                                   text="⬇️  Mover Abaixo",
                                   command=lambda: self.mover_coluna_fii(1),
                                   bg=self.cor_botao,
                                   fg=self.cor_texto,
                                   font=self.button_font,
                                   relief=tk.FLAT,
                                   bd=0,
                                   padx=12,
                                   pady=6,
                                   activebackground=self.cor_botao_hover,
                                   activeforeground=self.cor_texto,
                                   cursor="hand2")
        btn_mover_baixo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        ToolTip(btn_mover_baixo, "Move a coluna selecionada para baixo")

        return frame_colunas

    def _criar_area_compartilhada_inferior(self, parent):
        """Cria a área compartilhada na parte inferior com opções e botões globais."""
        # Separador visual elegante
        separador = tk.Frame(parent, height=2, bg=self.cor_borda, relief=tk.FLAT)
        separador.pack(fill=tk.X, pady=(10, 5))

        # Frame para a área compartilhada
        frame_compartilhado = tk.Frame(parent, bg=self.cor_fundo_secundario)
        frame_compartilhado.pack(fill=tk.X, pady=(0, 0))

        # Chamar o método original, mas apenas UMA vez
        self._criar_frame_opcoes_e_botoes_ui(frame_compartilhado)

    def _criar_frame_opcoes_e_botoes_ui(self, parent_tab):
        """Cria o frame de opções e botões principais com design moderno."""
        frame_opcoes = tk.Frame(parent_tab, bg=self.cor_fundo_secundario)
        frame_opcoes.pack(fill=tk.X, pady=(10, 0))

        # Frame para opções de configuração com design elegante
        frame_opcoes_config = tk.LabelFrame(frame_opcoes, text="⚙️  Opções",
                                           bg=self.cor_fundo_secundario, fg=self.cor_texto,
                                           font=self.title_font, relief=tk.FLAT, bd=2,
                                           highlightbackground=self.cor_borda, padx=12, pady=5)
        frame_opcoes_config.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        # Checkbox com estilo moderno
        self.var_headless = tk.BooleanVar(value=self.config["headless"])
        chk_headless = tk.Checkbutton(frame_opcoes_config,
                                     text="🚫  Headless (sem interface)",
                                     variable=self.var_headless,
                                     bg=self.cor_fundo_secundario,
                                     fg=self.cor_texto,
                                     selectcolor=self.cor_entrada,
                                     activebackground=self.cor_fundo_secundario,
                                     activeforeground=self.cor_texto,
                                     font=self.default_font,
                                     cursor="hand2")
        chk_headless.pack(anchor=tk.W, pady=(0, 5))
        ToolTip(chk_headless, "Executa o navegador em modo headless (sem interface gráfica)")

        # Botão tema com design moderno
        btn_tema = tk.Button(frame_opcoes_config,
                            text="🎨  Alternar Tema",
                            command=self.alternar_tema,
                            bg=self.cor_botao,
                            fg=self.cor_texto,
                            font=self.button_font,
                            relief=tk.FLAT,
                            bd=0,
                            padx=20,
                            pady=8,
                            activebackground=self.cor_botao_hover,
                            activeforeground=self.cor_texto,
                            cursor="hand2")
        btn_tema.pack(fill=tk.X, pady=(0, 5))
        ToolTip(btn_tema, "Alterna entre tema claro e escuro")
        btn_tema.tooltip_shortcut = "Ctrl+T"

        # Adicionar barra de status abaixo do botão de tema
        self.criar_barra_status(frame_opcoes_config)

        # Frame para ações principais com melhor layout
        frame_acoes_principais = tk.Frame(frame_opcoes, bg=self.cor_fundo_secundario)
        frame_acoes_principais.pack(side=tk.RIGHT)

        # Frame para botões de configuração com design vertical
        frame_config_botoes = tk.Frame(frame_acoes_principais, bg=self.cor_fundo_secundario)
        frame_config_botoes.pack(side=tk.LEFT, padx=(0, 15))

        btn_salvar = tk.Button(frame_config_botoes,
                              text="💾  Salvar Configurações",
                              command=self.salvar_configuracoes,
                              bg=self.cor_botao,
                              fg=self.cor_texto,
                              font=self.button_font,
                              relief=tk.FLAT,
                              bd=0,
                              padx=15,
                              pady=6,
                              width=22,
                              activebackground=self.cor_botao_hover,
                              activeforeground=self.cor_texto,
                              cursor="hand2")
        btn_salvar.pack(fill=tk.X, pady=(0, 3))
        ToolTip(btn_salvar, "Salva as configurações atuais")
        btn_salvar.tooltip_shortcut = "Ctrl+S"

        btn_fechar = tk.Button(frame_config_botoes,
                               text="❌  Fechar Aplicação",
                               command=self.root.destroy,
                               bg=self.cor_botao,
                               fg=self.cor_texto,
                               font=self.button_font,
                               relief=tk.FLAT,
                               bd=0,
                               padx=15,
                               pady=6,
                               width=22,
                               activebackground=self.cor_botao_hover,
                               activeforeground=self.cor_texto,
                               cursor="hand2")
        btn_fechar.pack(fill=tk.X)
        ToolTip(btn_fechar, "Fecha a aplicação")
        btn_fechar.tooltip_shortcut = "Ctrl+Q"

        # Botão principal de extração com destaque especial
        btn_extrair = tk.Button(frame_acoes_principais,
                               text="🚀  EXTRAIR DADOS",
                               command=self.start_combined_extraction,
                               bg=self.cor_botao_ativo,
                               fg="white",
                               font=self.large_button_font,
                               relief=tk.FLAT,
                               bd=0,
                               padx=20,
                               pady=12,
                               width=18,
                               activebackground=self.cor_botao_ativo_hover,
                               activeforeground="white",
                               cursor="hand2")
        btn_extrair.pack(side=tk.RIGHT)
        ToolTip(btn_extrair, "Inicia a extração de dados de ações e carteiras")
        btn_extrair.tooltip_shortcut = "Ctrl+E"

        return frame_opcoes

    def criar_barra_status(self, parent_frame=None):
        """Cria a barra de status com design moderno e elegante."""
        if parent_frame is None:
            parent_frame = self.root

        # Frame principal para barra de status com estilo moderno
        status_bg_color = self.cor_fundo_terciario if parent_frame == self.root else self.cor_fundo_secundario
        self.frame_status = tk.Frame(parent_frame, bg=status_bg_color,
                                    relief=tk.FLAT, bd=1, height=30)
        if parent_frame == self.root:
            self.frame_status.pack(fill=tk.X, side=tk.TOP, padx=20, pady=(5, 0))
        else:
            self.frame_status.pack(fill=tk.X, pady=(10, 5))
        self.frame_status.pack_propagate(False)  # Manter altura fixa

        # Frame interno para conteúdo da barra de status
        frame_interno = tk.Frame(self.frame_status, bg=status_bg_color)
        if parent_frame == self.root:
            frame_interno.pack(fill=tk.BOTH, expand=True, padx=15, pady=4)
        else:
            frame_interno.pack(fill=tk.BOTH, expand=True, padx=8, pady=3)

        # Container à esquerda para ícone e status
        frame_status_info = tk.Frame(frame_interno, bg=status_bg_color)
        frame_status_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Ícone de status com melhor design
        self.lbl_icone_status = tk.Label(frame_status_info, text="ℹ️",
                                        bg=status_bg_color,
                                        fg=self.cor_texto,
                                        font=self.default_font)
        self.lbl_icone_status.pack(side=tk.LEFT, padx=(0, 12))

        # Label para mensagens de status com melhor tipografia
        self.lbl_status = tk.Label(frame_status_info, text="✨ Pronto para iniciar",
                                   bg=status_bg_color,
                                   fg=self.cor_texto,
                                   anchor=tk.W,
                                   font=self.default_font)
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Frame para progresso com design moderno
        frame_progresso = tk.Frame(frame_interno, bg=status_bg_color)
        frame_progresso.pack(side=tk.RIGHT, padx=(15, 0))

        # Label para mostrar a porcentagem com estilo moderno
        self.lbl_porcentagem = tk.Label(frame_progresso, text="0%",
                                       bg=status_bg_color,
                                       fg=self.cor_texto_secundario,
                                       font=self.small_font,
                                       width=6)
        self.lbl_porcentagem.pack(side=tk.RIGHT, padx=(12, 0))

        # Barra de progresso com estilo moderno melhorado
        self.barra_progresso = ttk.Progressbar(frame_progresso,
                                              orient=tk.HORIZONTAL,
                                              length=200,
                                              mode="determinate",
                                              style="green.Horizontal.TProgressbar")
        self.barra_progresso.pack(side=tk.RIGHT)

        # Botão de cancelamento com design moderno (inicialmente oculto)
        self.btn_cancelar_extracao = tk.Button(frame_interno,
                                             text="❌  Cancelar Extração",
                                             command=self.cancelar_extracao_atual,
                                             bg=self.cor_erro,
                                             fg="white",
                                             font=self.button_font,
                                             relief=tk.FLAT,
                                             bd=0,
                                             padx=15,
                                             pady=6,
                                             activebackground="#dc2626",
                                             activeforeground="white",
                                             cursor="hand2")
        # Inicialmente oculto
        self.btn_cancelar_extracao.pack_forget()

        # Adicionar tooltips aprimorados
        ToolTip(self.lbl_status, "Mostra o status atual da operação em tempo real")
        ToolTip(self.barra_progresso, "Indica o progresso da operação atual")
        ToolTip(self.lbl_porcentagem, "Porcentagem de conclusão da operação")
        ToolTip(self.btn_cancelar_extracao, "Cancela a extração de dados em andamento")

    def atualizar_status(self, mensagem, progresso=None):
        """Atualiza a mensagem de status e a barra de progresso de forma thread-safe com feedback visual melhorado."""
        def _atualizar():
            try:
                self.lbl_status.config(text=mensagem)

                if progresso is not None:
                    self.barra_progresso["value"] = progresso
                    self.lbl_porcentagem.config(text=f"{int(progresso)}%")

                    # Atualizar a cor da barra de progresso e ícone baseado no valor
                    if progresso == 0:
                        self.barra_progresso["style"] = "red.Horizontal.TProgressbar"
                        self.lbl_icone_status.config(text="⏸️")
                    elif progresso < 30:
                        self.barra_progresso["style"] = "red.Horizontal.TProgressbar"
                        self.lbl_icone_status.config(text="🔄")
                    elif progresso < 70:
                        self.barra_progresso["style"] = "yellow.Horizontal.TProgressbar"
                        self.lbl_icone_status.config(text="⚡")
                    elif progresso < 100:
                        self.barra_progresso["style"] = "green.Horizontal.TProgressbar"
                        self.lbl_icone_status.config(text="🚀")
                    else:
                        self.barra_progresso["style"] = "green.Horizontal.TProgressbar"
                        self.lbl_icone_status.config(text="✅")
                else:
                    # Definir ícone baseado no tipo de mensagem quando não há progresso
                    if "erro" in mensagem.lower() or "❌" in mensagem:
                        self.lbl_icone_status.config(text="❌")
                    elif "sucesso" in mensagem.lower() or "✅" in mensagem:
                        self.lbl_icone_status.config(text="✅")
                    elif "cancelado" in mensagem.lower() or "⏳" in mensagem:
                        self.lbl_icone_status.config(text="⏹️")
                    elif "pronto" in mensagem.lower() or "✨" in mensagem:
                        self.lbl_icone_status.config(text="✨")
                    else:
                        self.lbl_icone_status.config(text="ℹ️")

                self.root.update_idletasks()
            except Exception as e:
                # Log do erro sem usar print
                import logging
                logging.error(f"Erro ao atualizar status: {e}")

        # Se estamos na thread principal, executar diretamente
        if threading.current_thread() == threading.main_thread():
            _atualizar()
        else:
            # Se estamos em uma thread secundária, usar after para thread safety
            self.root.after(0, _atualizar)

    def cancelar_extracao_atual(self):
        """Cancela a extração de dados em andamento."""
        if self.extracao_em_andamento:
            self.cancelar_extracao.set()
            self.atualizar_status("Cancelamento solicitado... Aguardando finalização segura.", 0)
            self.btn_cancelar_extracao.config(state='disabled', text="⏳  Cancelando...")

    def mostrar_botao_cancelar(self):
        """Mostra o botão de cancelar extração."""
        self.extracao_em_andamento = True
        self.cancelar_extracao.clear()
        self.btn_cancelar_extracao.config(state='normal', text="❌  Cancelar Extração")
        self.btn_cancelar_extracao.pack(side=tk.RIGHT, padx=(10, 0))

    def ocultar_botao_cancelar(self):
        """Oculta o botão de cancelar extração."""
        self.extracao_em_andamento = False
        self.btn_cancelar_extracao.pack_forget()

    def verificar_cancelamento(self):
        """Verifica se o cancelamento foi solicitado."""
        return self.cancelar_extracao.is_set()

    def adicionar_acao(self):
        """Adiciona uma nova ação à lista de ações e à interface."""
        acao = self.entry_acao.get().strip().upper()
        self.entry_acao.delete(0, tk.END)

        if not acao:
            messagebox.showwarning("Aviso", "O nome da ação não pode ser vazio.")
            return

        if acao not in self.config["acoes"]:
            self.config["acoes"].append(acao)
            self.listbox_acoes.insert(tk.END, acao)
            self.atualizar_contador_acoes()
            self.atualizar_status(f"✅ Ação {acao} adicionada com sucesso!", 100)
        else:
            messagebox.showinfo("Informação", f"Ação '{acao}' já existe na lista.")

    def remover_acao(self):
        """Remove a ação selecionada da lista de ações e da configuração."""
        try:
            indice_selecionado = self.listbox_acoes.curselection()[0]
            acao = self.listbox_acoes.get(indice_selecionado)

            # Solicitar confirmação antes de remover
            confirmacao = messagebox.askyesno(
                "Confirmar Remoção",
                f"Tem certeza que deseja remover a ação '{acao}'?\n\nEsta ação não pode ser desfeita.",
                icon='warning'
            )

            if not confirmacao:
                return

            self.listbox_acoes.delete(indice_selecionado)
            self.config["acoes"].remove(acao)
            self.atualizar_contador_acoes()
            self.atualizar_status(f"🗑️ Ação {acao} removida com sucesso!", 100)
        except (IndexError, ValueError):
            messagebox.showwarning("Aviso", "Selecione uma ação para remover ou ação não encontrada na configuração.")

    def atualizar_contador_acoes(self):
        num_acoes = len(self.config.get("acoes", []))
        self.lbl_contador_acoes.config(text=f"Ações: {num_acoes}")

    def adicionar_fii(self):
        """Adiciona um novo FII à lista de FIIs e à interface."""
        fii = self.entry_fii.get().strip().upper()
        self.entry_fii.delete(0, tk.END)

        if not fii:
            messagebox.showwarning("Aviso", "O nome do FII não pode ser vazio.")
            return

        if fii not in self.config["fiis"]:
            self.config["fiis"].append(fii)
            self.listbox_fiis.insert(tk.END, fii)
            self.atualizar_contador_fiis()
            self.atualizar_status(f"✅ FII {fii} adicionado com sucesso!", 100)
        else:
            messagebox.showinfo("Informação", f"FII '{fii}' já existe na lista.")

    def remover_fii(self):
        """Remove o FII selecionado da lista de FIIs e da configuração."""
        try:
            indice_selecionado = self.listbox_fiis.curselection()[0]
            fii = self.listbox_fiis.get(indice_selecionado)

            # Solicitar confirmação antes de remover
            confirmacao = messagebox.askyesno(
                "Confirmar Remoção",
                f"Tem certeza que deseja remover o FII '{fii}'?\n\nEsta ação não pode ser desfeita.",
                icon='warning'
            )

            if not confirmacao:
                return

            self.listbox_fiis.delete(indice_selecionado)
            self.config["fiis"].remove(fii)
            self.atualizar_contador_fiis()
            self.atualizar_status(f"🗑️ FII {fii} removido com sucesso!", 100)
        except (IndexError, ValueError):
            messagebox.showwarning("Aviso", "Selecione um FII para remover ou FII não encontrado na configuração.")

    def atualizar_contador_fiis(self):
        num_fiis = len(self.config.get("fiis", []))
        self.lbl_contador_fiis.config(text=f"FIIs: {num_fiis}")

    def adicionar_coluna_fii(self):
        """Abre um diálogo para adicionar uma nova coluna personalizada para FIIs."""
        dialog, entries, combos = self._criar_e_configurar_dialogo_coluna_ui("Adicionar Coluna para FIIs")

        frame_botoes = tk.Frame(dialog.winfo_children()[0], bg=self.cor_fundo)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=15)

        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=dialog.destroy,
                               bg=self.cor_botao, fg=self.cor_texto)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        btn_salvar = tk.Button(frame_botoes, text="Adicionar",
                             command=lambda: self.confirmar_adicionar_coluna_fii(
                                 entries["nome"].get(), combos["tipo"].get(),
                                 entries["classe_busca"].get(), entries["classe_retorno"].get(),
                                 entries["seletor_css"].get(), combos["formato_excel"].get(), dialog),
                             bg=self.cor_botao, fg=self.cor_texto)
        btn_salvar.pack(side=tk.LEFT, padx=5)

        ToolTip(btn_cancelar, "Cancela a adição da coluna")
        ToolTip(btn_salvar, "Adiciona a nova coluna para FIIs")

    def confirmar_adicionar_coluna_fii(self, nome, tipo, classe_busca, classe_retorno, seletor, formato_excel, dialog):
        """Confirma a adição de uma nova coluna personalizada para FIIs."""
        if not nome:
            messagebox.showwarning("Aviso", "O nome da coluna não pode ser vazio.")
            return

        # Verificar se o nome já existe
        for coluna in self.config["colunas_personalizadas_fiis"]:
            if coluna["nome"] == nome:
                messagebox.showwarning("Aviso", f"Já existe uma coluna com o nome '{nome}'.")
                return

        nova_coluna = {
            "nome": nome,
            "tipo": tipo,
            "classe_busca": classe_busca,
            "classe_retorno": classe_retorno,
            "seletor_css": seletor,
            "formato_excel": formato_excel
        }

        self.config["colunas_personalizadas_fiis"].append(nova_coluna)
        self.atualizar_treeview_colunas_fiis()
        self.atualizar_status(f"✅ Coluna '{nome}' adicionada para FIIs!", 100)
        dialog.destroy()

    def editar_coluna_fii(self):
        """Abre um diálogo para editar uma coluna personalizada de FIIs selecionada."""
        try:
            item = self.tree_colunas_fiis.selection()[0]
            valores = self.tree_colunas_fiis.item(item, "values")
            nome_coluna = valores[0]

            # Encontrar o índice da coluna
            indice = self.obter_indice_coluna_fii(nome_coluna)
            if indice == -1:
                messagebox.showerror("Erro", f"Coluna '{nome_coluna}' não encontrada.")
                return

            coluna_existente = self.config["colunas_personalizadas_fiis"][indice]

            dialog, entries, combos = self._criar_e_configurar_dialogo_coluna_ui("Editar Coluna FII", coluna_existente)

            frame_botoes = tk.Frame(dialog.winfo_children()[0], bg=self.cor_fundo)
            frame_botoes.grid(row=6, column=0, columnspan=2, pady=15)

            btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=dialog.destroy,
                                   bg=self.cor_botao, fg=self.cor_texto)
            btn_cancelar.pack(side=tk.LEFT, padx=5)

            btn_salvar = tk.Button(frame_botoes, text="Salvar",
                                 command=lambda: self.confirmar_editar_coluna_fii(
                                     indice, entries["nome"].get(), combos["tipo"].get(),
                                     entries["classe_busca"].get(), entries["classe_retorno"].get(),
                                     entries["seletor_css"].get(), combos["formato_excel"].get(), item, dialog),
                                 bg=self.cor_botao, fg=self.cor_texto)
            btn_salvar.pack(side=tk.LEFT, padx=5)

            ToolTip(btn_cancelar, "Cancela a edição")
            ToolTip(btn_salvar, "Salva as alterações na coluna")

        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma coluna para editar.")

    def confirmar_editar_coluna_fii(self, indice, nome, tipo, classe_busca, classe_retorno, seletor, formato_excel, item, dialog):
        """Confirma a edição de uma coluna personalizada de FIIs."""
        if not nome:
            messagebox.showwarning("Aviso", "O nome da coluna não pode ser vazio.")
            return

        # Verificar se o nome já existe (exceto para a própria coluna)
        for i, coluna in enumerate(self.config["colunas_personalizadas_fiis"]):
            if i != indice and coluna["nome"] == nome:
                messagebox.showwarning("Aviso", f"Já existe uma coluna com o nome '{nome}'.")
                return

        self.config["colunas_personalizadas_fiis"][indice] = {
            "nome": nome,
            "tipo": tipo,
            "classe_busca": classe_busca,
            "classe_retorno": classe_retorno,
            "seletor_css": seletor,
            "formato_excel": formato_excel
        }

        self.atualizar_treeview_colunas_fiis()
        self.atualizar_status(f"✅ Coluna '{nome}' atualizada!", 100)
        dialog.destroy()

    def excluir_coluna_fii(self):
        """Exclui a coluna personalizada de FIIs selecionada."""
        try:
            item = self.tree_colunas_fiis.selection()[0]
            valores = self.tree_colunas_fiis.item(item, "values")
            nome_coluna = valores[0]

            confirmacao = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir a coluna '{nome_coluna}'?\n\nEsta ação não pode ser desfeita.",
                icon='warning'
            )

            if not confirmacao:
                return

            indice = self.obter_indice_coluna_fii(nome_coluna)
            if indice != -1:
                del self.config["colunas_personalizadas_fiis"][indice]
                self.atualizar_treeview_colunas_fiis()
                self.atualizar_status(f"🗑️ Coluna '{nome_coluna}' excluída!", 100)
            else:
                messagebox.showerror("Erro", f"Coluna '{nome_coluna}' não encontrada.")

        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma coluna para excluir.")

    def mover_coluna_fii(self, direcao):
        """Move uma coluna de FIIs para cima (-1) ou para baixo (1)."""
        try:
            item = self.tree_colunas_fiis.selection()[0]
            valores = self.tree_colunas_fiis.item(item, "values")
            nome_coluna = valores[0]

            indice_atual = self.obter_indice_coluna_fii(nome_coluna)
            if indice_atual == -1:
                messagebox.showerror("Erro", f"Coluna '{nome_coluna}' não encontrada.")
                return

            novo_indice = indice_atual + direcao

            if 0 <= novo_indice < len(self.config["colunas_personalizadas_fiis"]):
                # Trocar posições
                colunas = self.config["colunas_personalizadas_fiis"]
                colunas[indice_atual], colunas[novo_indice] = colunas[novo_indice], colunas[indice_atual]

                self.atualizar_treeview_colunas_fiis()

                # Reselecionar o item movido
                for child in self.tree_colunas_fiis.get_children():
                    if self.tree_colunas_fiis.item(child, "values")[0] == nome_coluna:
                        self.tree_colunas_fiis.selection_set(child)
                        self.tree_colunas_fiis.focus(child)
                        break

                direcao_texto = "acima" if direcao == -1 else "abaixo"
                self.atualizar_status(f"↕️ Coluna '{nome_coluna}' movida para {direcao_texto}!", 100)
            else:
                direcao_texto = "início" if direcao == -1 else "fim"
                messagebox.showinfo("Informação", f"A coluna já está no {direcao_texto} da lista.")

        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma coluna para mover.")

    def atualizar_treeview_colunas_fiis(self):
        """Atualiza o Treeview de colunas personalizadas de FIIs."""
        # Limpar itens existentes
        for item in self.tree_colunas_fiis.get_children():
            self.tree_colunas_fiis.delete(item)

        # Repovoar com dados atualizados
        for coluna in self.config["colunas_personalizadas_fiis"]:
            self.tree_colunas_fiis.insert("", tk.END, values=(
                coluna["nome"],
                coluna["tipo"],
                coluna.get("seletor_css", ""),
                coluna.get("formato_excel", "Texto")
            ))

    def obter_indice_coluna_fii(self, nome_coluna):
        """Obtém o índice de uma coluna pelo nome para FIIs."""
        for i, coluna in enumerate(self.config["colunas_personalizadas_fiis"]):
            if coluna["nome"] == nome_coluna:
                return i
        return -1

    def alternar_tema(self):
        """Alterna o tema entre claro e escuro."""
        self.tema_escuro = not self.tema_escuro
        self.aplicar_tema()
        self.configurar_estilos_ttk()  # Reconfigurar estilos TTK com as novas cores
        self.atualizar_status(f"🎨 Tema alterado para {'escuro' if self.tema_escuro else 'claro'}", 100)

        # Recriar interface para aplicar o tema
        for widget in self.root.winfo_children():
            widget.destroy()
        self.criar_interface()
        self.config["tema"] = "escuro" if self.tema_escuro else "claro"

    def salvar_configuracoes(self, mostrar_mensagem=True):
        """Salva todas as configurações atuais da aplicação."""
        try:
            # Atualizar configurações
            self.config["headless"] = self.var_headless.get()
            self.config["tema"] = "escuro" if self.tema_escuro else "claro"

            # Salvar no arquivo
            self.salvar_config()

            if mostrar_mensagem:
                self.atualizar_status("💾 Configurações salvas com sucesso!", 100)
                messagebox.showinfo("Informação", "Configurações salvas com sucesso!")
        except Exception as e:
            self.atualizar_status(f"❌ Erro ao salvar configurações: {str(e)}", 0)
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")

    def start_combined_extraction(self):
        """Inicia a extração combinada de dados de ações, FIIs e carteiras."""
        if not self.config["acoes"] and not self.config["fiis"]:
            messagebox.showwarning("Aviso", "Nenhuma ação ou FII configurado para extração. A extração de carteiras prosseguirá se possível.")

        self.salvar_configuracoes(mostrar_mensagem=False)

        # Desabilitar o botão de extração durante o processo
        self.desabilitar_interface_durante_extracao(True)

        # Desabilitar atalhos de teclado durante a extração
        self.desabilitar_atalhos()

        # Mostrar botão de cancelamento
        self.mostrar_botao_cancelar()

        # Atualizar ícone de status para indicar processamento
        self.lbl_icone_status.config(text="⏳")

        # Executar a extração em uma thread separada
        extraction_thread = threading.Thread(target=self.perform_combined_extraction_logic, daemon=True)
        extraction_thread.start()

    def desabilitar_interface_durante_extracao(self, desabilitar=True):
        """Desabilita ou habilita elementos da interface durante a extração."""
        try:
            # Encontrar o botão de extração e outros elementos críticos
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for tab in widget.tabs():
                        tab_frame = widget.nametowidget(tab)
                        self._toggle_widgets_recursively(tab_frame, not desabilitar)
                else:
                    self._toggle_widgets_recursively(widget, not desabilitar)
        except Exception as e:
            import logging
            logging.error(f"Erro ao desabilitar interface: {e}")

    def _toggle_widgets_recursively(self, widget, enabled):
        """Recursivamente habilita/desabilita widgets."""
        try:
            if hasattr(widget, 'configure'):
                if isinstance(widget, (tk.Button, ttk.Button)):
                    widget.configure(state='normal' if enabled else 'disabled')
                elif isinstance(widget, (tk.Entry, tk.Entry, tk.Listbox, ttk.Treeview, ttk.Combobox)):
                    widget.configure(state='normal' if enabled else 'disabled')
                elif isinstance(widget, (tk.Checkbutton, ttk.Checkbutton)):
                    widget.configure(state='normal' if enabled else 'disabled')
                elif isinstance(widget, (tk.Text, tk.scrolledtext.ScrolledText)):
                    widget.configure(state='normal' if enabled else 'disabled')

            # Processar widgets filhos
            for child in widget.winfo_children():
                self._toggle_widgets_recursively(child, enabled)
        except Exception:
            pass  # Ignorar erros de widgets que não suportam state

    def perform_combined_extraction_logic(self):
        """
        Orquestra a lógica principal para a extração combinada de dados,
        incluindo configuração do WebDriver, login (se necessário),
        extração de dados de ações, FIIs e carteiras, e processamento/exportação dos resultados.
        """
        data_acoes_list = []
        data_fiis_list = []
        data_carteiras_list = []

        try:
            # Verificar se o cancelamento foi solicitado antes de começar
            if self.verificar_cancelamento():
                self.atualizar_status("Extração cancelada pelo usuário antes de iniciar.", 0)
                return

            # Criar instância do extrator de dados
            self.data_extractor = DataExtractor(
                config=self.config,
                status_callback=self.atualizar_status,
                cancelamento_event=self.cancelar_extracao
            )

            # Configurar driver
            self.data_extractor.setup_driver()

            # Verificar cancelamento após configurar o driver
            if self.verificar_cancelamento():
                self.atualizar_status("Extração cancelada pelo usuário.", 0)
                return

            # Acessar site e aguardar login
            self.data_extractor.access_site_and_await_login()

            # Extrair Dados de Ações
            if self.config.get("acoes"):
                data_acoes_list = self.data_extractor.extract_stock_data()
            else:
                self.atualizar_status("Nenhuma ação configurada, pulando extração de dados de ações.", 40)

            # Extrair Dados de FIIs
            if self.config.get("fiis"):
                data_fiis_list = self.data_extractor.extract_fiis_data()
            else:
                self.atualizar_status("Nenhum FII configurado, pulando extração de dados de FIIs.", 60)

            # Extrair Dados de Carteiras (Ações e FIIs separadamente)
            data_carteiras_acoes_list, data_carteiras_fiis_list = self.data_extractor.extract_portfolio_data()

            # Processar e Exportar Resultados
            self._process_and_export_data(data_acoes_list, data_fiis_list, data_carteiras_acoes_list, data_carteiras_fiis_list)

        except Exception as e:
            # Usar after para mostrar messagebox de forma thread-safe
            self.root.after(0, lambda: messagebox.showerror("Erro na Extração Combinada", f"Ocorreu um erro geral: {str(e)}"))
            self.atualizar_status(f"Erro geral na extração: {e}", 0)
        finally:
            if self.data_extractor:
                self.data_extractor.cleanup()
            # Ocultar botão de cancelamento
            self.root.after(0, self.ocultar_botao_cancelar)
            # Reabilitar interface de forma thread-safe
            self.root.after(0, lambda: self.desabilitar_interface_durante_extracao(False))
            # Reabilitar atalhos de teclado
            self.root.after(0, self.habilitar_atalhos)
            # Restaurar ícone de status
            self.root.after(0, lambda: self.lbl_icone_status.config(text="ℹ️"))

    def _process_and_export_data(self, data_acoes_list, data_fiis_list, data_carteiras_acoes_list, data_carteiras_fiis_list):
        """
        Processa os dados extraídos de ações, FIIs e carteiras, atualiza os DataFrames internos
        e chama a função para exportar para Excel.

        Args:
            data_acoes_list (list): Lista de dados de ações.
            data_fiis_list (list): Lista de dados de FIIs.
            data_carteiras_acoes_list (list): Lista de dados de carteiras de ações.
            data_carteiras_fiis_list (list): Lista de dados de carteiras de FIIs.
        """
        # Verificar se a extração foi cancelada
        if self.verificar_cancelamento():
            self.atualizar_status("Extração cancelada pelo usuário. Dados parciais não serão processados.", 0)
            return

        self.atualizar_status("Processando resultados...", 95)

        if data_acoes_list:
            self.df_acoes = pd.DataFrame(data_acoes_list)
        else:
            self.df_acoes = pd.DataFrame()

        if data_fiis_list:
            self.df_fiis = pd.DataFrame(data_fiis_list)
        else:
            self.df_fiis = pd.DataFrame()



        # Criar DataFrames separados para exportação
        if data_carteiras_acoes_list:
            self.df_carteiras_acoes = pd.DataFrame(data_carteiras_acoes_list)
        else:
            self.df_carteiras_acoes = pd.DataFrame()

        if data_carteiras_fiis_list:
            self.df_carteiras_fiis = pd.DataFrame(data_carteiras_fiis_list)
        else:
            self.df_carteiras_fiis = pd.DataFrame()

        if self.verificar_cancelamento():
            self.atualizar_status("Extração foi cancelada durante o processamento.", 0)
        else:
            self.atualizar_status("Extração combinada concluída!", 100)

        if (data_acoes_list or data_fiis_list or data_carteiras_acoes_list or data_carteiras_fiis_list) and not self.verificar_cancelamento():
            # Executar exportação na thread principal
            self.root.after(0, self.exportar_excel)
        elif self.verificar_cancelamento():
            # Usar after para mostrar messagebox de forma thread-safe
            self.root.after(0, lambda: messagebox.showinfo("Extração Cancelada", "A extração foi cancelada pelo usuário."))
        else:
            # Usar after para mostrar messagebox de forma thread-safe
            self.root.after(0, lambda: messagebox.showinfo("Extração Concluída", "Nenhum dado foi extraído (nem de ações, nem de FIIs, nem de carteiras)."))

    def exportar_excel(self):
        """Exporta os dados para Excel usando o ExcelExporter."""
        exporter = ExcelExporter(self.config)
        exporter.export_to_excel(self.df_acoes, self.df_fiis, self.df_carteiras_acoes, self.df_carteiras_fiis)

        # Abrir tela de visualização de dados após exportação
        if not self.df_acoes.empty or not self.df_fiis.empty or not self.df_carteiras_acoes.empty or not self.df_carteiras_fiis.empty:
            self.abrir_visualizador_dados()

    def abrir_visualizador_dados(self):
        """Abre a tela de visualização de dados."""
        try:
            viewer = DataViewer(self.root, self.df_acoes, self.config, self.df_fiis,
                              self.df_carteiras_acoes, self.df_carteiras_fiis)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir visualizador de dados: {str(e)}")

    # Métodos para gerenciamento de colunas personalizadas
    def _criar_e_configurar_dialogo_coluna_ui(self, titulo_dialogo, coluna_existente=None):
        """
        Cria e configura a UI base para o diálogo de adicionar/editar coluna.

        Args:
            titulo_dialogo (str): Título da janela de diálogo.
            coluna_existente (dict, optional): Dados da coluna existente (para edição). Defaults to None.

        Returns:
            tuple: Contendo (dialog, entries_dict, combos_dict)
        """
        dialog = tk.Toplevel(self.root)
        dialog.title(titulo_dialogo)
        dialog.geometry("600x280")
        dialog.configure(bg=self.cor_fundo)
        dialog.transient(self.root)
        dialog.grab_set()

        # Centralizar a janela de diálogo
        dialog_width = 600
        dialog_height = 280
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        position_x = root_x + (root_width // 2) - (dialog_width // 2)
        position_y = root_y + (root_height // 2) - (dialog_height // 2)
        dialog.geometry(f'{dialog_width}x{dialog_height}+{position_x}+{position_y}')

        frame = tk.Frame(dialog, bg=self.cor_fundo)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        labels_texts = ["Nome:", "Tipo:", "Classe Busca:", "Classe Retorno:", "Seletor CSS:", "Formato Excel:"]
        entries = {}
        combos = {}

        # Definir o mapeamento de campos antes de usar
        field_name_map = {
            "Nome:": "nome",
            "Classe Busca:": "classe_busca",
            "Classe Retorno:": "classe_retorno",
            "Seletor CSS:": "seletor_css"
        }

        for i, text in enumerate(labels_texts):
            tk.Label(frame, text=text, bg=self.cor_fundo, fg=self.cor_texto).grid(row=i, column=0, sticky=tk.W, pady=5)
            if text == "Tipo:":
                combo_tipo = ttk.Combobox(frame, values=["simples", "avancado"], width=38)
                combo_tipo.set(coluna_existente.get("tipo", "avancado") if coluna_existente else "avancado")
                combo_tipo.grid(row=i, column=1, sticky=tk.EW, pady=5)
                combos["tipo"] = combo_tipo
            elif text == "Formato Excel:":
                combo_formato_excel = ttk.Combobox(frame, values=["Texto", "Número", "Moeda", "Porcentagem"], width=38)
                combo_formato_excel.set(coluna_existente.get("formato_excel", "Texto") if coluna_existente else "Texto")
                combo_formato_excel.grid(row=i, column=1, sticky=tk.EW, pady=5)
                combos["formato_excel"] = combo_formato_excel
            else:
                entry = tk.Entry(frame, bg=self.cor_entrada, fg=self.cor_texto, width=40)
                if coluna_existente and text in field_name_map:
                    entry.insert(0, coluna_existente.get(field_name_map[text], ""))
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5)
                entries[field_name_map.get(text, text.lower().replace(":", "").replace(" ", "_"))] = entry

        frame.grid_columnconfigure(1, weight=1)
        return dialog, entries, combos

    def adicionar_coluna(self):
        """Abre um diálogo para adicionar uma nova coluna personalizada."""
        dialog, entries, combos = self._criar_e_configurar_dialogo_coluna_ui("Adicionar Coluna")

        frame_botoes = tk.Frame(dialog.winfo_children()[0], bg=self.cor_fundo)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=15)

        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=dialog.destroy,
                               bg=self.cor_botao, fg=self.cor_texto)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        btn_salvar = tk.Button(frame_botoes, text="Adicionar",
                             command=lambda: self.confirmar_adicionar_coluna(
                                 entries["nome"].get(), combos["tipo"].get(),
                                 entries["classe_busca"].get(), entries["classe_retorno"].get(),
                                 entries["seletor_css"].get(), combos["formato_excel"].get(), dialog),
                             bg=self.cor_botao, fg=self.cor_texto)
        btn_salvar.pack(side=tk.LEFT, padx=5)

        # Adicionar tooltips aos botões
        ToolTip(btn_cancelar, "Cancela a adição da coluna")
        ToolTip(btn_salvar, "Adiciona a nova coluna")

    def confirmar_adicionar_coluna(self, nome, tipo, classe_busca, classe_retorno, seletor, formato_excel, dialog):
        """Confirma e adiciona a nova coluna à configuração e à Treeview."""
        if not nome:
            messagebox.showwarning("Aviso", "O nome da coluna é obrigatório", parent=dialog)
            return

        nova_coluna = {
            "nome": nome,
            "tipo": tipo,
            "classe_busca": classe_busca,
            "classe_retorno": classe_retorno,
            "seletor_css": seletor,
            "formato_excel": formato_excel
        }

        self.config["colunas_personalizadas"].append(nova_coluna)
        self.tree_colunas.insert("", tk.END, values=(nome, tipo, seletor, formato_excel))
        dialog.destroy()
        self.atualizar_status(f"Coluna '{nome}' adicionada com sucesso!", 100)

    def excluir_coluna(self):
        """Exclui a coluna personalizada selecionada da configuração e da Treeview."""
        try:
            item = self.tree_colunas.selection()[0]
            valores = self.tree_colunas.item(item, "values")
            nome_coluna = valores[0]
            indice = self.obter_indice_coluna(nome_coluna)

            if indice == -1:
                messagebox.showwarning("Aviso", "Coluna não encontrada na configuração")
                return

            # Solicitar confirmação antes de excluir
            confirmacao = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir a coluna '{nome_coluna}'?\n\nEsta ação não pode ser desfeita.",
                icon='warning'
            )

            if not confirmacao:
                return

            self.config["colunas_personalizadas"].pop(indice)
            self.tree_colunas.delete(item)
            self.atualizar_status(f"Coluna '{nome_coluna}' removida com sucesso!", 100)
        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma coluna para excluir")

    def mover_coluna(self, direcao):
        """Move a coluna selecionada para cima ou para baixo na lista de configuração."""
        try:
            item = self.tree_colunas.selection()[0]
            valores = self.tree_colunas.item(item, "values")
            indice = self.obter_indice_coluna(valores[0])

            if indice == -1:
                messagebox.showwarning("Aviso", "Coluna não encontrada na configuração")
                return

            # Verificar limites
            novo_indice = indice + direcao
            if novo_indice < 0 or novo_indice >= len(self.config["colunas_personalizadas"]):
                return

            # Trocar posições
            colunas = self.config["colunas_personalizadas"]
            colunas[indice], colunas[novo_indice] = colunas[novo_indice], colunas[indice]

            # Atualizar treeview
            self.atualizar_treeview_colunas()

            # Reselecionar item movido
            items = self.tree_colunas.get_children()
            if 0 <= novo_indice < len(items):
                self.tree_colunas.selection_set(items[novo_indice])
                self.tree_colunas.see(items[novo_indice])

            self.atualizar_status(f"Coluna '{valores[0]}' movida com sucesso!", 100)

        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma coluna para mover")

    def atualizar_treeview_colunas(self):
        """Atualiza o treeview de colunas personalizadas."""
        # Limpar treeview
        for item in self.tree_colunas.get_children():
            self.tree_colunas.delete(item)

        # Preencher novamente
        for coluna in self.config["colunas_personalizadas"]:
            self.tree_colunas.insert("", tk.END, values=(
                coluna["nome"],
                coluna["tipo"],
                coluna.get("seletor_css", ""),
                coluna.get("formato_excel", "Texto")
            ))

    def editar_coluna(self):
        """Abre um diálogo para editar a coluna personalizada selecionada."""
        try:
            item_selecionado = self.tree_colunas.selection()[0]
            valores_atuais = self.tree_colunas.item(item_selecionado, "values")
            nome_coluna_atual = valores_atuais[0]
            indice_coluna = self.obter_indice_coluna(nome_coluna_atual)

            if indice_coluna == -1:
                messagebox.showwarning("Aviso", "Coluna não encontrada na configuração")
                return

            coluna_para_editar = self.config["colunas_personalizadas"][indice_coluna]

            dialog, entries, combos = self._criar_e_configurar_dialogo_coluna_ui("Editar Coluna", coluna_para_editar)

            frame_botoes = tk.Frame(dialog.winfo_children()[0], bg=self.cor_fundo)
            frame_botoes.grid(row=6, column=0, columnspan=2, pady=15)

            btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=dialog.destroy,
                                   bg=self.cor_botao, fg=self.cor_texto)
            btn_cancelar.pack(side=tk.LEFT, padx=5)

            btn_salvar_edicao = tk.Button(frame_botoes, text="Salvar",
                                 command=lambda: self.confirmar_editar_coluna(
                                     indice_coluna, entries["nome"].get(), combos["tipo"].get(),
                                     entries["classe_busca"].get(), entries["classe_retorno"].get(),
                                     entries["seletor_css"].get(), combos["formato_excel"].get(),
                                     item_selecionado, dialog),
                                 bg=self.cor_botao, fg=self.cor_texto)
            btn_salvar_edicao.pack(side=tk.LEFT, padx=5)

            # Adicionar tooltips aos botões
            ToolTip(btn_cancelar, "Cancela a edição da coluna")
            ToolTip(btn_salvar_edicao, "Salva as alterações na coluna")

        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma coluna para editar")

    def confirmar_editar_coluna(self, indice, nome, tipo, classe_busca, classe_retorno, seletor, formato_excel, item, dialog):
        """Confirma e salva as alterações da coluna editada na configuração e na Treeview."""
        if not nome:
            messagebox.showwarning("Aviso", "O nome da coluna é obrigatório", parent=dialog)
            return

        self.config["colunas_personalizadas"][indice].update({
            "nome": nome,
            "tipo": tipo,
            "classe_busca": classe_busca,
            "classe_retorno": classe_retorno,
            "seletor_css": seletor,
            "formato_excel": formato_excel
        })

        self.tree_colunas.item(item, values=(nome, tipo, seletor, formato_excel))
        dialog.destroy()
        self.atualizar_status(f"Coluna '{nome}' editada com sucesso!", 100)

    def obter_indice_coluna(self, nome_coluna):
        """Obtém o índice de uma coluna na lista de configuração pelo nome."""
        for i, coluna in enumerate(self.config["colunas_personalizadas"]):
            if coluna["nome"] == nome_coluna:
                return i
        return -1
