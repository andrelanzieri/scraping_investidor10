import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import json
import threading
from datetime import datetime
import re

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

class DataViewer:
    """
    Tela para visualizar dados exportados e interagir com IA Google Gemini.
    """

    def __init__(self, parent, df_acoes, config, df_fiis=None, df_carteiras_acoes=None, df_carteiras_fiis=None):
        """
        Inicializa o visualizador de dados.

        Args:
            parent: Widget pai (janela principal)
            df_acoes: DataFrame com dados das ações
            config: Configurações da aplicação
            df_fiis: DataFrame com dados dos FIIs (opcional)
            df_carteiras_acoes: DataFrame com dados da carteira de ações (opcional)
            df_carteiras_fiis: DataFrame com dados da carteira de FIIs (opcional)
        """
        self.parent = parent
        self.df_acoes = df_acoes
        self.df_fiis = df_fiis if df_fiis is not None else pd.DataFrame()
        self.df_carteiras_acoes = df_carteiras_acoes if df_carteiras_acoes is not None else pd.DataFrame()
        self.df_carteiras_fiis = df_carteiras_fiis if df_carteiras_fiis is not None else pd.DataFrame()
        self.config = config
        self.ai_configured = False

        # Configurar tema baseado na configuração
        self.tema_escuro = config.get("tema", "escuro") == "escuro"
        self._aplicar_tema()

        # Inicializar IA se configurada
        self._init_ai()

        # Criar janela
        self.criar_janela()

    def _aplicar_tema(self):
        """Aplica o tema claro ou escuro."""
        if self.tema_escuro:
            self.cor_fundo = "#0f1419"
            self.cor_fundo_secundario = "#1a1f26"
            self.cor_fundo_terciario = "#252d38"
            self.cor_texto = "#e8eaed"
            self.cor_texto_secundario = "#9aa0a6"
            self.cor_botao = "#2d3748"
            self.cor_botao_ativo = "#3182ce"
            self.cor_entrada = "#1e2a38"
            self.cor_destaque = "#3b82f6"
            self.cor_sucesso = "#10b981"
            self.cor_aviso = "#f59e0b"
            self.cor_erro = "#ef4444"
        else:
            self.cor_fundo = "#f8fafc"
            self.cor_fundo_secundario = "#ffffff"
            self.cor_fundo_terciario = "#f1f5f9"
            self.cor_texto = "#1e293b"
            self.cor_texto_secundario = "#64748b"
            self.cor_botao = "#e2e8f0"
            self.cor_botao_ativo = "#3b82f6"
            self.cor_entrada = "#ffffff"
            self.cor_destaque = "#3b82f6"
            self.cor_sucesso = "#10b981"
            self.cor_aviso = "#f59e0b"
            self.cor_erro = "#ef4444"

    def _init_ai(self):
        """Inicializa a IA Google Gemini se configurada."""
        if not GENAI_AVAILABLE:
            self.ai_configured = False
            return

        api_key = self.config.get("gemini_api_key", "")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-pro')
                self.ai_configured = True
            except Exception as e:
                print(f"Erro ao configurar IA: {e}")
                self.ai_configured = False
        else:
            self.ai_configured = False

    def criar_janela(self):
        """Cria a janela principal do visualizador."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📊 Visualizador de Dados e IA")
        self.window.geometry("1400x800")
        self.window.configure(bg=self.cor_fundo)

        # Centralizar janela
        self.window.transient(self.parent)
        self.window.grab_set()

        # Criar notebook com abas
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Aba de dados
        self.criar_aba_dados()

        # Aba de IA
        self.criar_aba_ia()

        # Aba de configurações da IA
        self.criar_aba_config_ia()

    def criar_aba_dados(self):
        """Cria a aba de visualização de dados."""
        frame_dados = ttk.Frame(self.notebook)
        self.notebook.add(frame_dados, text="📈 Dados Exportados")

        # Frame principal
        main_frame = tk.Frame(frame_dados, bg=self.cor_fundo_secundario)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        titulo = tk.Label(main_frame, text="📊 Dados Exportados",
                         font=("Segoe UI", 16, "bold"),
                         bg=self.cor_fundo_secundario, fg=self.cor_texto)
        titulo.pack(pady=(0, 20))

        # Notebook para separar ações e carteiras
        dados_notebook = ttk.Notebook(main_frame)
        dados_notebook.pack(fill=tk.BOTH, expand=True)

        # Aba de ações
        if not self.df_acoes.empty:
            frame_acoes = ttk.Frame(dados_notebook)
            dados_notebook.add(frame_acoes, text=f"📈 Ações ({len(self.df_acoes)} registros)")
            self.criar_tabela_dados(frame_acoes, self.df_acoes)

        # Aba de FIIs
        if not self.df_fiis.empty:
            frame_fiis = ttk.Frame(dados_notebook)
            dados_notebook.add(frame_fiis, text=f"🏢 FIIs ({len(self.df_fiis)} registros)")
            self.criar_tabela_dados(frame_fiis, self.df_fiis)

        # Aba de carteira de ações
        if not self.df_carteiras_acoes.empty:
            frame_carteiras_acoes = ttk.Frame(dados_notebook)
            dados_notebook.add(frame_carteiras_acoes, text=f"💼 Carteira Ações ({len(self.df_carteiras_acoes)} registros)")
            self.criar_tabela_dados(frame_carteiras_acoes, self.df_carteiras_acoes)

        # Aba de carteira de FIIs
        if not self.df_carteiras_fiis.empty:
            frame_carteiras_fiis = ttk.Frame(dados_notebook)
            dados_notebook.add(frame_carteiras_fiis, text=f"🏢 Carteira FIIs ({len(self.df_carteiras_fiis)} registros)")
            self.criar_tabela_dados(frame_carteiras_fiis, self.df_carteiras_fiis)

        # Estatísticas gerais
        self.criar_estatisticas(main_frame)

    def criar_tabela_dados(self, parent, df):
        """Cria uma tabela para exibir os dados."""
        # Frame para a tabela
        frame_tabela = tk.Frame(parent, bg=self.cor_fundo_secundario)
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Criar Treeview
        colunas = list(df.columns)
        tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=15)

        # Configurar cabeçalhos
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=120, minwidth=80)

        # Adicionar dados
        for index, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))

        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tree.yview)
        scrollbar_h = ttk.Scrollbar(frame_tabela, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        # Layout
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)

    def criar_estatisticas(self, parent):
        """Cria um resumo estatístico dos dados."""
        frame_stats = tk.LabelFrame(parent, text="📊 Estatísticas",
                                   bg=self.cor_fundo_secundario, fg=self.cor_texto,
                                   font=("Segoe UI", 12, "bold"))
        frame_stats.pack(fill=tk.X, pady=(20, 0))

        # Texto com estatísticas
        stats_text = tk.Text(frame_stats, height=6, width=80,
                            bg=self.cor_fundo_terciario, fg=self.cor_texto,
                            font=("Consolas", 10))
        stats_text.pack(fill=tk.X, padx=10, pady=10)

        # Gerar estatísticas
        stats_info = []
        if not self.df_acoes.empty:
            stats_info.append(f"📈 AÇÕES: {len(self.df_acoes)} registros")
            stats_info.append(f"   Colunas: {', '.join(self.df_acoes.columns[:5])}{'...' if len(self.df_acoes.columns) > 5 else ''}")

        if not self.df_fiis.empty:
            stats_info.append(f"🏢 FIIs: {len(self.df_fiis)} registros")
            stats_info.append(f"   Colunas: {', '.join(self.df_fiis.columns[:5])}{'...' if len(self.df_fiis.columns) > 5 else ''}")



        stats_info.append(f"📅 Exportado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        stats_text.insert(tk.END, "\n".join(stats_info))
        stats_text.config(state=tk.DISABLED)

    def criar_aba_ia(self):
        """Cria a aba de interação com IA."""
        frame_ia = ttk.Frame(self.notebook)
        self.notebook.add(frame_ia, text="🤖 Chat com IA")

        # Frame principal
        main_frame = tk.Frame(frame_ia, bg=self.cor_fundo_secundario)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        titulo = tk.Label(main_frame, text="🤖 Chat com Google Gemini",
                         font=("Segoe UI", 16, "bold"),
                         bg=self.cor_fundo_secundario, fg=self.cor_texto)
        titulo.pack(pady=(0, 20))

        # Status da IA
        if not GENAI_AVAILABLE:
            status_text = "❌ Biblioteca google-generativeai não instalada"
            status_color = self.cor_erro
        elif self.ai_configured:
            status_text = "✅ IA Configurada"
            status_color = self.cor_sucesso
        else:
            status_text = "❌ IA Não Configurada"
            status_color = self.cor_erro

        status_label = tk.Label(main_frame, text=status_text,
                               font=("Segoe UI", 10, "bold"),
                               bg=self.cor_fundo_secundario, fg=status_color)
        status_label.pack(pady=(0, 10))

        # Área de chat
        chat_frame = tk.Frame(main_frame, bg=self.cor_fundo_secundario)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Área de conversa
        self.chat_area = scrolledtext.ScrolledText(chat_frame,
                                                  bg=self.cor_fundo_terciario,
                                                  fg=self.cor_texto,
                                                  font=("Segoe UI", 10),
                                                  wrap=tk.WORD,
                                                  state=tk.DISABLED)
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        # Configurar tags para formatação markdown
        self.configurar_tags_formatacao()

        # Frame de entrada
        entrada_frame = tk.Frame(main_frame, bg=self.cor_fundo_secundario)
        entrada_frame.pack(fill=tk.X, pady=(10, 0))

        # Campo de entrada
        self.entrada_ia = tk.Entry(entrada_frame,
                                  bg=self.cor_entrada, fg=self.cor_texto,
                                  font=("Segoe UI", 10))
        self.entrada_ia.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entrada_ia.bind("<Return>", self.enviar_mensagem)

        # Botões
        botoes_frame = tk.Frame(entrada_frame, bg=self.cor_fundo_secundario)
        botoes_frame.pack(side=tk.RIGHT)

        # Botão para enviar dados completos como CSV
        self.btn_dados_csv = tk.Button(botoes_frame, text="📋 Insights",
                                 command=self.enviar_dados_csv,
                                 bg=self.cor_botao, fg=self.cor_texto,
                                 font=("Segoe UI", 9),
                                 relief=tk.FLAT, cursor="hand2")
        self.btn_dados_csv.pack(side=tk.LEFT, padx=(0, 5))

        # Adicionar tooltip informativo
        def mostrar_info_csv():
            messagebox.showinfo("Análise Completa com IA",
                "🚀 **Análise Financeira Completa e Estratégica**\n\n" +
                "Este botão ativa uma análise profunda e abrangente de TODOS os seus dados:\n\n" +
                "📊 **Análise Fundamentalista:**\n" +
                "• Valuation e atratividade de preços\n" +
                "• Qualidade e rentabilidade das empresas\n" +
                "• Solidez financeira e estrutura de capital\n" +
                "• Política de dividendos e sustentabilidade\n\n" +
                "🎯 **Rankings e Recomendações:**\n" +
                "• Top picks para diferentes perfis\n" +
                "• Oportunidades de valor e crescimento\n" +
                "• Red flags e riscos específicos\n\n" +
                "💼 **Estratégias de Portfólio:**\n" +
                "• Diversificação setorial otimizada\n" +
                "• Estratégias para diferentes objetivos\n" +
                "• Análise de concentração e riscos\n\n" +
                "🔍 **Insights Únicos:**\n" +
                "• Correlações e padrões especiais\n" +
                "• Análise de cenários e sensibilidade\n" +
                "• Recomendações personalizadas\n\n" +
                "⚡ **A IA combinará rigor técnico com criatividade analítica!**")

        # Bind para mostrar info quando clicar com botão direito
        self.btn_dados_csv.bind("<Button-3>", lambda e: mostrar_info_csv())

        # Botão enviar
        self.btn_enviar = tk.Button(botoes_frame, text="📤 Enviar",
                              command=self.enviar_mensagem,
                              bg=self.cor_botao_ativo, fg="white",
                              font=("Segoe UI", 10, "bold"),
                              relief=tk.FLAT, cursor="hand2")
        self.btn_enviar.pack(side=tk.LEFT)

        # Mensagem inicial
        if not GENAI_AVAILABLE:
            self.adicionar_mensagem_chat("🤖 IA", "A biblioteca google-generativeai não está instalada. Execute: pip install google-generativeai", "bot")
        elif self.ai_configured:
            total_registros = len(self.df_acoes) + len(self.df_fiis) + len(self.df_carteiras_acoes) + len(self.df_carteiras_fiis)
            tipos_dados = []
            if len(self.df_acoes) > 0:
                tipos_dados.append(f"{len(self.df_acoes)} ações")
            if len(self.df_fiis) > 0:
                tipos_dados.append(f"{len(self.df_fiis)} FIIs")
            if len(self.df_carteiras_acoes) > 0:
                tipos_dados.append(f"{len(self.df_carteiras_acoes)} itens de carteira de ações")
            if len(self.df_carteiras_fiis) > 0:
                tipos_dados.append(f"{len(self.df_carteiras_fiis)} itens de carteira de FIIs")

            descricao_dados = ", ".join(tipos_dados[:-1]) + f" e {tipos_dados[-1]}" if len(tipos_dados) > 1 else tipos_dados[0] if tipos_dados else "nenhum dado"

            self.adicionar_mensagem_chat("🤖 IA", f"✨ **Analista Financeiro IA - Pronto para Ajudar!**\n\n📊 **Dados Disponíveis:** {total_registros} registros ({descricao_dados})\n\n🎯 **O que posso fazer:**\n• Análises fundamentalistas detalhadas\n• Identificação de oportunidades e riscos\n• Comparações setoriais e rankings\n• Estratégias de portfólio personalizadas\n• Insights criativos e correlações únicas\n• Recomendações baseadas nos seus dados\n• Análises específicas de FIIs e ações\n\n💡 **Dicas:**\n• Use o botão **'📋 Insights'** para análise automática completa\n• Faça perguntas específicas sobre ações, FIIs ou setores\n• Peça comparações, rankings ou cenários\n• Solicite estratégias para diferentes perfis de risco\n\n🚀 **Estou aqui para ser seu consultor financeiro pessoal!**", "bot")
        else:
            self.adicionar_mensagem_chat("🤖 IA", "Configure sua API key do Google Gemini na aba 'Configurações da IA' para começar a usar o chat.", "bot")

    def criar_aba_config_ia(self):
        """Cria a aba de configurações da IA."""
        frame_config = ttk.Frame(self.notebook)
        self.notebook.add(frame_config, text="⚙️ Configurações IA")

        # Frame principal
        main_frame = tk.Frame(frame_config, bg=self.cor_fundo_secundario)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        titulo = tk.Label(main_frame, text="⚙️ Configurações da IA Google Gemini",
                         font=("Segoe UI", 16, "bold"),
                         bg=self.cor_fundo_secundario, fg=self.cor_texto)
        titulo.pack(pady=(0, 30))

        # Instruções
        instrucoes = tk.Label(main_frame,
                             text="Para usar o chat com IA, você precisa configurar uma API key do Google Gemini.\n" +
                                  "Acesse https://aistudio.google.com/app/apikey para obter sua chave gratuita.\n\n" +
                                  "Funcionalidades da IA:\n" +
                                  "• Chat interativo com TODOS os dados extraídos\n" +
                                  "• Botão 'Insights' para análise automática completa\n" +
                                  "• Análise de tendências, comparações e recomendações\n" +
                                  "• Suporte a grandes volumes de dados (até 800k caracteres)",
                             font=("Segoe UI", 10),
                             bg=self.cor_fundo_secundario, fg=self.cor_texto_secundario,
                             wraplength=600, justify=tk.LEFT)
        instrucoes.pack(pady=(0, 20))

        # Campo para API key
        api_frame = tk.Frame(main_frame, bg=self.cor_fundo_secundario)
        api_frame.pack(fill=tk.X, pady=(0, 20))

        api_label = tk.Label(api_frame, text="API Key do Google Gemini:",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.cor_fundo_secundario, fg=self.cor_texto)
        api_label.pack(anchor=tk.W)

        self.api_entry = tk.Entry(api_frame,
                                 bg=self.cor_entrada, fg=self.cor_texto,
                                 font=("Segoe UI", 10), show="*", width=60)
        self.api_entry.pack(fill=tk.X, pady=(5, 0))

        # Carregar API key se existir
        if "gemini_api_key" in self.config:
            self.api_entry.insert(0, self.config["gemini_api_key"])

        # Botões
        botoes_frame = tk.Frame(main_frame, bg=self.cor_fundo_secundario)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))

        btn_testar = tk.Button(botoes_frame, text="🧪 Testar Conexão",
                              command=self.testar_api,
                              bg=self.cor_botao, fg=self.cor_texto,
                              font=("Segoe UI", 10), relief=tk.FLAT, cursor="hand2")
        btn_testar.pack(side=tk.LEFT, padx=(0, 10))

        btn_salvar = tk.Button(botoes_frame, text="💾 Salvar Configurações",
                              command=self.salvar_config_ia,
                              bg=self.cor_botao_ativo, fg="white",
                              font=("Segoe UI", 10, "bold"), relief=tk.FLAT, cursor="hand2")
        btn_salvar.pack(side=tk.LEFT)

        # Área de status
        self.status_config = tk.Label(main_frame, text="",
                                     bg=self.cor_fundo_secundario,
                                     font=("Segoe UI", 10))
        self.status_config.pack(pady=(20, 0))

    def testar_api(self):
        """Testa a conexão com a API do Google Gemini."""
        api_key = self.api_entry.get().strip()
        if not api_key:
            self.status_config.config(text="❌ Insira uma API key", fg=self.cor_erro)
            return

        self.status_config.config(text="🔄 Testando conexão...", fg=self.cor_aviso)

        def testar_thread():
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-pro')
                response = model.generate_content("Teste de conexão. Responda apenas: 'Conexão bem-sucedida!'")

                self.window.after(0, lambda: self.status_config.config(
                    text="✅ Conexão bem-sucedida!", fg=self.cor_sucesso))

            except Exception as e:
                self.window.after(0, lambda: self.status_config.config(
                    text=f"❌ Erro: {str(e)}", fg=self.cor_erro))

        threading.Thread(target=testar_thread, daemon=True).start()

    def salvar_config_ia(self):
        """Salva as configurações da IA."""
        api_key = self.api_entry.get().strip()

        # Atualizar configuração
        self.config["gemini_api_key"] = api_key

        # Salvar no arquivo
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)

            # Reinicializar IA
            self._init_ai()

            self.status_config.config(text="✅ Configurações salvas!", fg=self.cor_sucesso)

            # Mostrar informativo sobre segurança do config.json se a API key foi configurada
            # e o usuário não desativou o aviso
            if api_key and self.config.get("mostrar_aviso_seguranca", True):
                self.mostrar_informativo_seguranca()

        except Exception as e:
            self.status_config.config(text=f"❌ Erro ao salvar: {str(e)}", fg=self.cor_erro)

    def mostrar_informativo_seguranca(self):
        """Mostra informativo sobre segurança do arquivo config.json."""
        # Criar janela personalizada para o informativo
        janela_info = tk.Toplevel(self.window)
        janela_info.title("🔐 Importante - Segurança da API Key")
        janela_info.geometry("650x500")
        janela_info.resizable(False, False)
        janela_info.configure(bg=self.cor_fundo)

        # Centralizar a janela
        janela_info.transient(self.window)
        janela_info.grab_set()

        # Calcular posição central
        janela_info.update_idletasks()
        x = (janela_info.winfo_screenwidth() // 2) - (650 // 2)
        y = (janela_info.winfo_screenheight() // 2) - (500 // 2)
        janela_info.geometry(f"650x500+{x}+{y}")

        # Frame principal
        frame_principal = tk.Frame(janela_info, bg=self.cor_fundo, padx=30, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = tk.Label(frame_principal,
                         text="🔐 IMPORTANTE - Segurança da API Key",
                         font=("Segoe UI", 16, "bold"),
                         bg=self.cor_fundo, fg=self.cor_erro)
        titulo.pack(pady=(0, 20))

        # Texto do informativo
        mensagem = """⚠️ ATENÇÃO: Sua API key do Google Gemini foi salva no arquivo config.json

🚨 NUNCA COMPARTILHE ESTE ARQUIVO COM OUTRAS PESSOAS OU PUBLIQUE NO GIT!

📋 REGRAS DE SEGURANÇA IMPORTANTES:

✅ O que FAZER:
• Manter o arquivo config.json apenas no seu computador
• Adicionar config.json ao .gitignore se usar controle de versão
• Fazer backup seguro das suas configurações
• Manter sua API key privada e segura

❌ O que NÃO FAZER:
• Compartilhar o arquivo config.json com terceiros
• Publicar o arquivo config.json no GitHub ou outros repositórios
• Enviar o arquivo por email ou mensagem
• Deixar o arquivo em pastas compartilhadas

🔒 MOTIVO DA SEGURANÇA:
• Sua API key é pessoal e intransferível
• Terceiros podem usar sua API key indevidamente
• Uso não autorizado pode esgotar sua cota gratuita
• Possível cobrança por uso excessivo por terceiros

💡 DICAS IMPORTANTES:
• A API key fica salva localmente no seu computador
• Nenhum dado é enviado para outros serviços além do Google Gemini
• Você pode regenerar sua API key no Google AI Studio se necessário
• Mantenha sempre suas credenciais seguras

🛡️ LEMBRE-SE: Sua segurança digital é responsabilidade sua!"""

        # Área de texto com scroll
        texto_frame = tk.Frame(frame_principal, bg=self.cor_fundo)
        texto_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        texto_msg = tk.Text(texto_frame,
                           wrap=tk.WORD,
                           font=("Segoe UI", 10),
                           bg=self.cor_fundo_secundario,
                           fg=self.cor_texto,
                           relief=tk.RIDGE,
                           bd=1,
                           padx=15,
                           pady=15)

        # Scrollbar para o texto
        scrollbar = tk.Scrollbar(texto_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        texto_msg.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        texto_msg.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=texto_msg.yview)

        texto_msg.insert(tk.END, mensagem)
        texto_msg.config(state=tk.DISABLED)

        # Frame para checkbox e botões
        frame_inferior = tk.Frame(frame_principal, bg=self.cor_fundo)
        frame_inferior.pack(fill=tk.X, pady=(10, 0))

        # Checkbox para não mostrar novamente
        self.var_nao_mostrar_seguranca = tk.BooleanVar()
        checkbox = tk.Checkbutton(frame_inferior,
                                 text="Não mostrar este aviso novamente",
                                 variable=self.var_nao_mostrar_seguranca,
                                 bg=self.cor_fundo,
                                 fg=self.cor_texto,
                                 font=("Segoe UI", 9),
                                 activebackground=self.cor_fundo,
                                 selectcolor=self.cor_fundo_secundario)
        checkbox.pack(side=tk.LEFT)

        # Frame para botões
        frame_botoes = tk.Frame(frame_inferior, bg=self.cor_fundo)
        frame_botoes.pack(side=tk.RIGHT)

        def fechar_janela():
            # Salvar preferência se checkbox marcado
            if self.var_nao_mostrar_seguranca.get():
                self.config["mostrar_aviso_seguranca"] = False
                try:
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(self.config, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"Erro ao salvar preferência: {e}")
            janela_info.destroy()

        # Botão para mais informações
        def mostrar_mais_info():
            info_adicional = """INFORMAÇÕES TÉCNICAS ADICIONAIS:

🔧 SOBRE O ARQUIVO CONFIG.JSON:
• Contém todas as configurações da aplicação
• Inclui lista de ações, colunas personalizadas e tema
• Armazena sua API key do Google Gemini
• É atualizado automaticamente quando você salva configurações

🌐 SOBRE A API KEY:
• Chave única que identifica sua conta no Google Gemini
• Permite acesso aos serviços de IA do Google
• Tem cota gratuita generosa para uso pessoal
• Pode ser regenerada no Google AI Studio se comprometida

🔄 COMO REGENERAR SUA API KEY:
1. Acesse https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Revogue a API key atual (se necessário)
4. Crie uma nova API key
5. Substitua no programa

⚠️ SINAIS DE COMPROMETIMENTO:
• Uso inesperado da sua cota
• Notificações de uso não reconhecidas
• Comportamento estranho na aplicação

🆘 EM CASO DE PROBLEMAS:
• Regenere imediatamente sua API key
• Verifique se o arquivo config.json não foi compartilhado
• Entre em contato com o suporte do Google se necessário"""

            messagebox.showinfo("Informações Técnicas", info_adicional)

        btn_info = tk.Button(frame_botoes,
                            text="Mais Info",
                            command=mostrar_mais_info,
                            bg=self.cor_botao,
                            fg=self.cor_texto,
                            font=("Segoe UI", 9),
                            padx=15,
                            pady=8,
                            relief=tk.FLAT,
                            cursor="hand2")
        btn_info.pack(side=tk.RIGHT, padx=(0, 10))

        # Botão OK
        btn_ok = tk.Button(frame_botoes,
                          text="Entendi",
                          command=fechar_janela,
                          bg=self.cor_erro,
                          fg="white",
                          font=("Segoe UI", 10, "bold"),
                          padx=20,
                          pady=8,
                          relief=tk.FLAT,
                          cursor="hand2")
        btn_ok.pack(side=tk.RIGHT)

        # Aguardar fechamento da janela
        janela_info.wait_window()

    def enviar_mensagem(self, event=None):
        """Envia mensagem para a IA."""
        if not self.ai_configured:
            messagebox.showwarning("IA Não Configurada",
                                 "Configure a API key do Google Gemini primeiro.")
            return

        mensagem = self.entrada_ia.get().strip()
        if not mensagem:
            return

        # Limpar a caixa de texto ANTES de desabilitar a interface
        self.entrada_ia.delete(0, tk.END)

        # Desabilitar interface durante processamento
        self.desabilitar_chat_interface(True)

        # Adicionar mensagem do usuário
        self.adicionar_mensagem_chat("👤 Você", mensagem, "user")

        # Mostrar que a IA está "digitando"
        self.adicionar_mensagem_chat("🤖 IA", "🔄 Processando sua mensagem...", "bot")

        # Processar mensagem em thread separada
        threading.Thread(target=self.processar_mensagem_ia,
                        args=(mensagem,), daemon=True).start()

    def processar_mensagem_ia(self, mensagem):
        """Processa a mensagem com a IA."""
        try:
            # Preparar contexto com os dados
            contexto = self.preparar_contexto_dados()

            # Adicionar a pergunta do usuário ao prompt final
            prompt_completo = f"""{contexto}

**PERGUNTA DO USUÁRIO:**
{mensagem}
"""

            # Gerar resposta
            response = self.model.generate_content(prompt_completo)
            resposta = response.text

            # Atualizar UI na thread principal
            self.window.after(0, lambda: self.atualizar_resposta_ia(resposta))

        except Exception as e:
            self.window.after(0, lambda: self.atualizar_resposta_ia(f"Erro ao processar mensagem: {str(e)}"))
        finally:
            # Reabilitar interface após processamento
            self.window.after(0, lambda: self.desabilitar_chat_interface(False))
            # Garantir que o campo permaneça limpo após o processamento
            self.window.after(0, lambda: self.entrada_ia.delete(0, tk.END) if hasattr(self, 'entrada_ia') else None)

    def preparar_contexto_dados(self):
        """Prepara o contexto com TODOS os dados exportados, usando uma estrutura de prompt flexível e poderosa."""

        # --- ESTRUTURA DO PROMPT MELHORADA ---

        # 1. PERSONA APRIMORADA
        persona = """**PERSONA:**
Você é um analista financeiro experiente e consultor de investimentos com amplo conhecimento do mercado brasileiro. Você combina análise técnica rigorosa com insights práticos e perspectivas estratégicas. Seu objetivo é fornecer análises valiosas, insights acionáveis e orientações baseadas nos dados, sempre priorizando clareza e utilidade para o usuário."""

        # 2. CONTEXTO DOS DADOS EXPANDIDO
        contexto_dados = f"""**CONTEXTO DOS DADOS:**
Você tem acesso a dados financeiros fundamentalistas extraídos do site Investidor10.
- **Data da Extração:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- **Fonte:** Investidor10 - dados fundamentalistas atualizados
- **Escopo:** Informações sobre ações brasileiras e composição de carteiras de investimento
- **Propósito:** Análise para tomada de decisões de investimento informadas"""

        # 3. DADOS PARA ANÁLISE (em formato CSV para otimização)
        dados_analise = ["**DADOS DISPONÍVEIS PARA ANÁLISE:**"]
        MAX_CHARS = 800000

        # Adicionar dados de ações
        if not self.df_acoes.empty:
            header = f"\n**📈 DADOS DE AÇÕES ({len(self.df_acoes)} registros):**"
            csv_acoes = self.df_acoes.to_csv(index=False)
            dados_analise.append(header)
            dados_analise.append(csv_acoes)

        # Adicionar dados de FIIs
        if not self.df_fiis.empty:
            header = f"\n**🏢 DADOS DE FIIs ({len(self.df_fiis)} registros):**"
            csv_fiis = self.df_fiis.to_csv(index=False)
            dados_analise.append(header)
            dados_analise.append(csv_fiis)

        # Adicionar dados de carteira de ações
        if not self.df_carteiras_acoes.empty:
            header = f"\n**💼 DADOS DE CARTEIRA DE AÇÕES ({len(self.df_carteiras_acoes)} registros):**"
            csv_carteiras_acoes = self.df_carteiras_acoes.to_csv(index=False)
            dados_analise.append(header)
            dados_analise.append(csv_carteiras_acoes)

        # Adicionar dados de carteira de FIIs
        if not self.df_carteiras_fiis.empty:
            header = f"\n**🏢 DADOS DE CARTEIRA DE FIIs ({len(self.df_carteiras_fiis)} registros):**"
            csv_carteiras_fiis = self.df_carteiras_fiis.to_csv(index=False)
            dados_analise.append(header)
            dados_analise.append(csv_carteiras_fiis)



        dados_str = "\n".join(dados_analise)

        # Truncar se necessário
        if len(dados_str) > MAX_CHARS:
            dados_str = dados_str[:MAX_CHARS] + "\n... [DADOS TRUNCADOS PARA OTIMIZAÇÃO - Análise baseada na amostra mais representativa]"

        # 4. RESUMO ESTATÍSTICO INTELIGENTE
        resumo_estatistico_list = ["\n**📊 RESUMO ESTATÍSTICO:**"]
        if not self.df_acoes.empty:
            resumo_estatistico_list.append(f"\n**Ações:** {len(self.df_acoes)} registros disponíveis")
            # Adicionar insights sobre as colunas disponíveis
            colunas_numericas = self.df_acoes.select_dtypes(include=['number']).columns
            if len(colunas_numericas) > 0:
                resumo_estatistico_list.append(f"Métricas numéricas: {', '.join(colunas_numericas.tolist())}")
                resumo_estatistico_list.append("\nEstatísticas descritivas:")
                resumo_estatistico_list.append(self.df_acoes.describe().to_string())

        if not self.df_fiis.empty:
            resumo_estatistico_list.append(f"\n**FIIs:** {len(self.df_fiis)} registros disponíveis")
            # Adicionar insights sobre as colunas disponíveis
            colunas_numericas = self.df_fiis.select_dtypes(include=['number']).columns
            if len(colunas_numericas) > 0:
                resumo_estatistico_list.append(f"Métricas numéricas: {', '.join(colunas_numericas.tolist())}")
                resumo_estatistico_list.append("\nEstatísticas descritivas:")
                resumo_estatistico_list.append(self.df_fiis.describe().to_string())

        if not self.df_carteiras_acoes.empty:
            resumo_estatistico_list.append(f"\n**Carteira de Ações:** {len(self.df_carteiras_acoes)} itens")
            colunas_numericas = self.df_carteiras_acoes.select_dtypes(include=['number']).columns
            if len(colunas_numericas) > 0:
                resumo_estatistico_list.append(f"Métricas numéricas: {', '.join(colunas_numericas.tolist())}")
                resumo_estatistico_list.append("\nEstatísticas descritivas:")
                resumo_estatistico_list.append(self.df_carteiras_acoes.describe().to_string())

        if not self.df_carteiras_fiis.empty:
            resumo_estatistico_list.append(f"\n**Carteira de FIIs:** {len(self.df_carteiras_fiis)} itens")
            colunas_numericas = self.df_carteiras_fiis.select_dtypes(include=['number']).columns
            if len(colunas_numericas) > 0:
                resumo_estatistico_list.append(f"Métricas numéricas: {', '.join(colunas_numericas.tolist())}")
                resumo_estatistico_list.append("\nEstatísticas descritivas:")
                resumo_estatistico_list.append(self.df_carteiras_fiis.describe().to_string())



        resumo_estatistico = "\n".join(resumo_estatistico_list)

        # 5. DIRETRIZES DE RESPOSTA FLEXÍVEIS
        diretrizes = """\n**DIRETRIZES DE RESPOSTA:**

**🎯 Objetivo Principal:**
Forneça análises úteis, insights valiosos e orientações práticas baseadas nos dados. Seja o consultor financeiro que o usuário precisa.

**💡 Abordagem:**
- **Priorize a utilidade:** Foque no que é mais útil e acionável para o usuário
- **Use sua expertise:** Aplique conhecimento de mercado, tendências e melhores práticas de investimento
- **Seja contextual:** Considere o cenário econômico brasileiro e características do mercado local
- **Formato inteligente:** Use Markdown para organizar informações (tabelas, listas, destaques)

**📋 Flexibilidade de Conteúdo:**
- **Dados primários:** Base suas análises nos dados fornecidos
- **Conhecimento complementar:** Adicione contexto de mercado, explicações de conceitos e perspectivas quando relevante
- **Perguntas abertas:** Para questões fora do escopo financeiro, responda normalmente e conecte de volta aos dados quando apropriado
- **Criatividade analítica:** Explore correlações, padrões e insights únicos nos dados

**🔍 Tipos de Análise Sugeridos:**
- Comparações e rankings personalizados
- Identificação de oportunidades e riscos
- Análise setorial e de diversificação
- Projeções e cenários baseados nos fundamentos
- Recomendações de alocação e estratégia
- Alertas e pontos de atenção específicos

**⚖️ Responsabilidade:**
Suas análises são para fins educacionais e informativos. Encoraje o usuário a fazer sua própria pesquisa e considerar seu perfil de risco, mas forneça insights valiosos que ajudem na tomada de decisão.

---"""

        # --- MONTAGEM FINAL DO PROMPT ---
        prompt_final = "\n\n".join([persona, contexto_dados, dados_str, resumo_estatistico, diretrizes])

        return prompt_final

    def atualizar_resposta_ia(self, resposta):
        """Atualiza a resposta da IA no chat."""
        # Remover mensagem "Digitando..."
        self.chat_area.config(state=tk.NORMAL)
        content = self.chat_area.get("1.0", tk.END)
        lines = content.split('\n')

        # Procurar e remover a última linha "Digitando..."
        for i in range(len(lines) - 1, -1, -1):
            if "Digitando..." in lines[i]:
                lines.pop(i)
                break

        # Recriar o conteúdo
        self.chat_area.delete("1.0", tk.END)
        self.chat_area.insert(tk.END, '\n'.join(lines))
        self.chat_area.config(state=tk.DISABLED)

        # Adicionar resposta da IA
        self.adicionar_mensagem_chat("🤖 IA", resposta, "bot")

    def configurar_tags_formatacao(self):
        """Configura as tags de formatação para o widget de texto."""
        # Tag para texto em negrito
        self.chat_area.tag_configure("negrito", font=("Segoe UI", 10, "bold"))

        # Tag para texto em itálico
        self.chat_area.tag_configure("italico", font=("Segoe UI", 10, "italic"))

        # Tag para código
        self.chat_area.tag_configure("codigo",
                                   font=("Consolas", 9),
                                   background=self.cor_fundo if self.tema_escuro else "#f0f0f0",
                                   foreground=self.cor_destaque)

        # Tag para tabelas (fonte monoespaçada para alinhamento)
        self.chat_area.tag_configure("tabela",
                                     font=("Consolas", 9),
                                     lmargin1=20, lmargin2=20)

        # Tag para títulos
        self.chat_area.tag_configure("titulo",
                                   font=("Segoe UI", 12, "bold"),
                                   foreground=self.cor_destaque,
                                   spacing3=5) # Espaço abaixo do título

        # Tag para listas
        self.chat_area.tag_configure("lista",
                                   lmargin1=20, lmargin2=20)

        # Tag para texto destacado
        self.chat_area.tag_configure("destaque",
                                   foreground=self.cor_destaque)

    def renderizar_markdown(self, texto):
        """Processa texto markdown e retorna lista de segmentos com formatação."""
        segmentos = []
        linhas = texto.split('\n')

        for linha in linhas:
            # Lidar com linhas vazias
            if not linha.strip():
                segmentos.append(("\n", "normal"))
                continue

            # Títulos (ex: ### Título)
            match_titulo = re.match(r'^(#{1,6})\s+(.*)', linha)
            if match_titulo:
                conteudo = match_titulo.group(2).strip()
                segmentos.extend(self.processar_formatacao_inline(conteudo))
                segmentos.append(("\n", "titulo"))
                continue

            # Tabelas (linhas que começam e terminam com |)
            if linha.strip().startswith('|') and linha.strip().endswith('|'):
                if '---' in linha: # Ignorar a linha de separação
                    continue
                # Adicionar a linha da tabela com a tag de tabela
                segmentos.append((linha.strip() + "\n", "tabela"))
                continue

            # Listas não ordenadas (ex: * item or - item)
            match_lista_nao_ord = re.match(r'^\s*([-\*])\s+(.*)', linha)
            if match_lista_nao_ord:
                conteudo = match_lista_nao_ord.group(2).strip()
                segmentos.append(("• ", "lista")) # Adiciona o marcador
                segmentos.extend(self.processar_formatacao_inline(conteudo))
                segmentos.append(("\n", "lista"))
                continue

            # Listas ordenadas (ex: 1. item)
            match_lista_ord = re.match(r'^\s*(\d+\.)\s+(.*)', linha)
            if match_lista_ord:
                marcador = match_lista_ord.group(1)
                conteudo = match_lista_ord.group(2).strip()
                segmentos.append((f"{marcador} ", "lista")) # Mantém o número
                segmentos.extend(self.processar_formatacao_inline(conteudo))
                segmentos.append(("\n", "lista"))
                continue

            # Linha horizontal (---, ***, ___)
            if re.match(r'^\s*([-*_]){3,}\s*$', linha):
                segmentos.append(("\n" + "─" * 80 + "\n", "normal"))
                continue

            # Parágrafo normal
            segmentos.extend(self.processar_formatacao_inline(linha.strip()))
            segmentos.append(("\n", "normal"))

        return segmentos

    def processar_formatacao_inline(self, texto):
        """Processa formatação inline como negrito, itálico e código."""
        # A ordem dos padrões é crucial para que `**` seja verificado antes de `*`.
        patterns = re.compile(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)')
        segmentos = []

        # Usa re.split para quebrar o texto pelos padrões de formatação, mantendo os delimitadores
        parts = patterns.split(texto)

        for part in parts:
            if not part:
                continue

            # Verifica se a parte corresponde a um dos padrões de formatação
            if part.startswith('**') and part.endswith('**'):
                segmentos.append((part[2:-2], 'negrito'))
            elif part.startswith('*') and part.endswith('*'):
                segmentos.append((part[1:-1], 'italico'))
            elif part.startswith('`') and part.endswith('`'):
                segmentos.append((part[1:-1], 'codigo'))
            else:
                # Se não for um padrão conhecido, é texto normal
                segmentos.append((part, 'normal'))

        return segmentos

    def adicionar_mensagem_chat(self, remetente, mensagem, tipo):
        """Adiciona uma mensagem ao chat com formatação Markdown aprimorada."""
        self.chat_area.config(state=tk.NORMAL)

        # Adicionar espaço se não for a primeira mensagem
        if self.chat_area.get("1.0", tk.END).strip():
            self.chat_area.insert(tk.END, "\n\n")

        # Inserir cabeçalho da mensagem
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_area.insert(tk.END, f"[{timestamp}] {remetente}:\n", ("negrito",))

        # Processar e inserir a mensagem
        if tipo == "bot":
            # Limpar a resposta de caracteres indesejados que a IA pode retornar
            mensagem_limpa = re.sub(r'```markdown|```', '', mensagem).strip()
            segmentos = self.renderizar_markdown(mensagem_limpa)
            for texto, tag in segmentos:
                self.chat_area.insert(tk.END, texto, (tag,) if tag != "normal" else ())
        else: # tipo == "user"
            self.chat_area.insert(tk.END, mensagem)

        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def enviar_dados_csv(self):
        """Envia todos os dados em formato CSV para a IA."""
        if not self.ai_configured:
            messagebox.showwarning("IA Não Configurada",
                                 "Configure a API key do Google Gemini primeiro.")
            return

        # Desabilitar interface durante processamento
        self.desabilitar_chat_interface(True)

        # Preparar dados em formato CSV
        dados_csv = self.preparar_dados_csv()

        # Adicionar mensagem do usuário
        self.adicionar_mensagem_chat("👤 Você", "Enviando TODOS os dados para análise completa", "user")

        # Mostrar que a IA está "digitando"
        self.adicionar_mensagem_chat("🤖 IA", "🔄 Processando os dados...", "bot")

        # Processar dados em thread separada
        threading.Thread(target=self.processar_dados_csv,
                        args=(dados_csv,), daemon=True).start()

    def preparar_dados_csv(self):
        """Prepara todos os dados em formato CSV otimizado."""
        dados_completos = ""

        if not self.df_acoes.empty:
            dados_completos += "=== DADOS DE AÇÕES ===\n"
            # Converter para CSV string
            csv_acoes = self.df_acoes.to_csv(index=False)
            dados_completos += csv_acoes + "\n"



        # Adicionar resumo estatístico
        dados_completos += "=== RESUMO ESTATÍSTICO ===\n"

        if not self.df_acoes.empty:
            dados_completos += f"AÇÕES: {len(self.df_acoes)} registros\n"
            numeric_cols = self.df_acoes.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                dados_completos += self.df_acoes[numeric_cols].describe().to_csv()
                dados_completos += "\n"



        return dados_completos

    def processar_dados_csv(self, dados_csv):
        """Processa os dados com a IA."""
        try:
            # Prompt para análise dos dados CSV aprimorado
            prompt_csv = f"""
**PERSONA:**
Você é um analista financeiro sênior e estrategista de investimentos, especializado no mercado brasileiro. Sua expertise inclui análise fundamentalista, gestão de portfólio, identificação de tendências e avaliação de riscos. Você fornece insights valiosos que combinam rigor técnico com perspectiva prática do mercado.

**CONTEXTO:**
Você está analisando dados fundamentalistas extraídos do Investidor10, focando em ações brasileiras e composição de carteiras. O objetivo é fornecer uma análise completa que ajude na tomada de decisões de investimento.

**DADOS PARA ANÁLISE:**
```csv
{dados_csv}
```

**MISSÃO:**
Realize uma análise financeira abrangente e estratégica. Seja criativo, perspicaz e útil. Explore os dados de múltiplas perspectivas e forneça insights que vão além do óbvio. Use sua expertise para identificar oportunidades, riscos e padrões únicos.

---

## 📋 ESTRUTURA SUGERIDA (Adapte conforme necessário)

### 🎯 1. VISÃO GERAL ESTRATÉGICA
**Análise do universo de investimentos:**
- Perfil das empresas (setores, tamanhos, características)
- Qualidade geral do portfólio/lista de ações
- Pontos fortes e fracos do conjunto
- Oportunidades e desafios identificados

### 📊 2. ANÁLISE FUNDAMENTALISTA PROFUNDA

#### **Valuation e Atratividade**
- Ações com melhor relação preço/valor
- Múltiplos atrativos vs. caros
- Comparação com médias históricas (quando relevante)

#### **Qualidade e Rentabilidade**
- Empresas com melhor geração de valor
- Eficiência operacional e financeira
- Sustentabilidade dos resultados

#### **Solidez Financeira**
- Saúde do balanço e estrutura de capital
- Capacidade de enfrentar cenários adversos
- Flexibilidade financeira

#### **Política de Dividendos**
- Melhores pagadoras e sustentabilidade
- Análise de payout e histórico
- Potencial de crescimento dos proventos

### 🏆 3. RANKINGS E RECOMENDAÇÕES

#### **Top Picks (Oportunidades de Destaque)**
Liste as melhores oportunidades com justificativas sólidas baseadas nos dados.

#### **Ações para Monitorar**
Empresas com potencial mas que requerem acompanhamento.

#### **Red Flags e Cuidados**
Identifique riscos específicos e ações que merecem cautela.

### 🎯 4. ESTRATÉGIAS DE PORTFÓLIO

#### **Diversificação Setorial**
- Concentração por setor
- Sugestões de balanceamento
- Riscos de concentração

#### **Perfis de Investimento**
- Estratégia para dividendos
- Estratégia para crescimento
- Estratégia para valor
- Estratégia equilibrada

### 🔍 5. INSIGHTS ÚNICOS E CORRELAÇÕES
Explore padrões interessantes, correlações inesperadas ou insights únicos que você identifica nos dados.

### ⚠️ 6. CENÁRIOS E RISCOS
- Análise de sensibilidade
- Principais riscos a monitorar
- Impactos de diferentes cenários econômicos

### 💡 7. CONCLUSÕES E PRÓXIMOS PASSOS
- Principais takeaways
- Ações recomendadas para o investidor
- Pontos de atenção para acompanhamento

---

## 🎨 DIRETRIZES CRIATIVAS

**Seja Abrangente:** Não se limite apenas aos dados - use seu conhecimento do mercado brasileiro para contextualizar e enriquecer a análise.

**Seja Prático:** Foque em insights acionáveis e recomendações que o investidor possa implementar.

**Seja Inovador:** Explore ângulos únicos de análise e correlações interessantes.

**Use Visualização:** Crie tabelas comparativas, rankings e estruture informações de forma clara.

**Contextualize:** Considere o momento atual do mercado brasileiro e tendências relevantes.

**Personalize:** Adapte a estrutura conforme os dados disponíveis - se não há dados de certo tipo, foque no que está disponível.

---

**LEMBRE-SE:** Sua análise será usada para decisões reais de investimento. Seja rigoroso com os dados, mas criativo na interpretação e apresentação dos insights.
"""

            # Gerar resposta
            response = self.model.generate_content(prompt_csv)
            resposta = response.text

            # Atualizar UI na thread principal
            self.window.after(0, lambda: self.atualizar_resposta_ia(resposta))

        except Exception as e:
            self.window.after(0, lambda: self.atualizar_resposta_ia(f"Erro ao processar dados CSV: {str(e)}"))
        finally:
            # Reabilitar interface após processamento
            self.window.after(0, lambda: self.desabilitar_chat_interface(False))

    def desabilitar_chat_interface(self, desabilitar=True):
        """Desabilita ou habilita a interface de chat durante processamento da IA."""
        try:
            estado = 'disabled' if desabilitar else 'normal'

            # Desabilitar/habilitar campo de entrada
            if hasattr(self, 'entrada_ia'):
                self.entrada_ia.configure(state=estado)
                # Quando reabilitar, garantir que o campo esteja focado e pronto
                if not desabilitar:
                    self.entrada_ia.focus_set()

            # Desabilitar/habilitar botões
            if hasattr(self, 'btn_enviar'):
                self.btn_enviar.configure(state=estado)
                if desabilitar:
                    self.btn_enviar.configure(text="⏳ Processando...")
                else:
                    self.btn_enviar.configure(text="📤 Enviar")

            if hasattr(self, 'btn_dados_csv'):
                self.btn_dados_csv.configure(state=estado)
                if desabilitar:
                    self.btn_dados_csv.configure(text="⏳ Processando...")
                else:
                    self.btn_dados_csv.configure(text="📋 Insights")

        except Exception as e:
            print(f"Erro ao desabilitar chat interface: {e}")