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

    def __init__(self, parent, df_acoes, df_carteiras, config):
        """
        Inicializa o visualizador de dados.

        Args:
            parent: Widget pai (janela principal)
            df_acoes: DataFrame com dados das ações
            df_carteiras: DataFrame com dados das carteiras
            config: Configurações da aplicação
        """
        self.parent = parent
        self.df_acoes = df_acoes
        self.df_carteiras = df_carteiras
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

        # Aba de carteiras
        if not self.df_carteiras.empty:
            frame_carteiras = ttk.Frame(dados_notebook)
            dados_notebook.add(frame_carteiras, text=f"💼 Carteiras ({len(self.df_carteiras)} registros)")
            self.criar_tabela_dados(frame_carteiras, self.df_carteiras)

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

        if not self.df_carteiras.empty:
            stats_info.append(f"💼 CARTEIRAS: {len(self.df_carteiras)} registros")
            stats_info.append(f"   Colunas: {', '.join(self.df_carteiras.columns[:5])}{'...' if len(self.df_carteiras.columns) > 5 else ''}")

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
            messagebox.showinfo("Insights",
                "Este botão envia TODOS os dados extraídos em formato CSV para a IA fazer uma análise completa automática.\n\n" +
                "A IA fornecerá:\n" +
                "• Resumo geral dos dados\n" +
                "• Insights e tendências\n" +
                "• Comparações detalhadas\n" +
                "• Recomendações de investimento\n" +
                "• Identificação de oportunidades\n" +
                "• Análise de riscos")

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
            total_registros = len(self.df_acoes) + len(self.df_carteiras)
            self.adicionar_mensagem_chat("🤖 IA", f"Olá! Estou pronto para ajudar com análise dos seus dados financeiros. Tenho acesso a TODOS os {total_registros} registros extraídos ({len(self.df_acoes)} ações e {len(self.df_carteiras)} itens de carteira). Posso fazer análises completas, comparações detalhadas, identificar tendências e fornecer recomendações baseadas em todos os dados disponíveis. Você pode me fazer qualquer pergunta sobre os dados!", "bot")
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

            # Prompt completo
            prompt_completo = f"""{contexto}

Pergunta do usuário: {mensagem}

Responda de forma clara e objetiva, baseando-se nos dados fornecidos quando relevante. Se a pergunta não estiver relacionada aos dados, responda normalmente mas mencione que você tem acesso aos dados financeiros exportados."""

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
        """Prepara o contexto com TODOS os dados exportados, otimizando para grandes volumes."""
        contexto = "Contexto completo dos dados financeiros exportados:\n\n"

        # Calcular limite estimado para evitar exceder tokens da IA
        # Gemini 2.5 Pro tem limite de ~1M tokens, deixamos margem para pergunta/resposta
        MAX_CHARS = 800000  # Limite conservador em caracteres
        contexto_chars = 0

        if not self.df_acoes.empty:
            contexto += f"DADOS DE AÇÕES ({len(self.df_acoes)} registros):\n"
            contexto += f"Colunas: {', '.join(self.df_acoes.columns)}\n"

            # Adicionar TODOS os dados de ações
            contexto += "TODOS OS DADOS DE AÇÕES:\n"
            for i, (_, row) in enumerate(self.df_acoes.iterrows()):
                linha_dados = f"  {i+1}. {dict(row)}\n"
                if contexto_chars + len(linha_dados) > MAX_CHARS:
                    contexto += f"  ... [DADOS TRUNCADOS - Mostrando {i} de {len(self.df_acoes)} registros para evitar limite de tokens]\n"
                    break
                contexto += linha_dados
                contexto_chars += len(linha_dados)
            contexto += "\n"

        if not self.df_carteiras.empty and contexto_chars < MAX_CHARS:
            contexto += f"DADOS DE CARTEIRAS ({len(self.df_carteiras)} registros):\n"
            contexto += f"Colunas: {', '.join(self.df_carteiras.columns)}\n"

            # Adicionar TODOS os dados de carteiras
            contexto += "TODOS OS DADOS DE CARTEIRAS:\n"
            for i, (_, row) in enumerate(self.df_carteiras.iterrows()):
                linha_dados = f"  {i+1}. {dict(row)}\n"
                if contexto_chars + len(linha_dados) > MAX_CHARS:
                    contexto += f"  ... [DADOS TRUNCADOS - Mostrando {i} de {len(self.df_carteiras)} registros para evitar limite de tokens]\n"
                    break
                contexto += linha_dados
                contexto_chars += len(linha_dados)
            contexto += "\n"

        # Adicionar estatísticas resumidas
        contexto += "RESUMO ESTATÍSTICO:\n"
        if not self.df_acoes.empty:
            contexto += f"- Total de ações analisadas: {len(self.df_acoes)}\n"
            # Adicionar estatísticas específicas se houver colunas numéricas
            numeric_cols = self.df_acoes.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                contexto += f"- Colunas numéricas: {', '.join(numeric_cols)}\n"
                # Adicionar estatísticas descritivas para colunas numéricas
                for col in numeric_cols:
                    if not self.df_acoes[col].empty:
                        try:
                            stats = self.df_acoes[col].describe()
                            contexto += f"  {col}: Média={stats['mean']:.2f}, Min={stats['min']:.2f}, Max={stats['max']:.2f}\n"
                        except:
                            pass

        if not self.df_carteiras.empty:
            contexto += f"- Total de itens em carteiras: {len(self.df_carteiras)}\n"
            # Adicionar estatísticas específicas se houver colunas numéricas
            numeric_cols = self.df_carteiras.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                contexto += f"- Colunas numéricas: {', '.join(numeric_cols)}\n"
                # Adicionar estatísticas descritivas para colunas numéricas
                for col in numeric_cols:
                    if not self.df_carteiras[col].empty:
                        try:
                            stats = self.df_carteiras[col].describe()
                            contexto += f"  {col}: Média={stats['mean']:.2f}, Min={stats['min']:.2f}, Max={stats['max']:.2f}\n"
                        except:
                            pass

        contexto += f"\nVocê tem acesso ao máximo de dados possível (limitado por tokens da IA). Total de caracteres do contexto: {len(contexto)}. Use todos os dados disponíveis para fornecer análises financeiras detalhadas, comparações precisas, identificação de tendências, recomendações de investimento, análise de risco, e qualquer análise que o usuário solicitar.\n\n"

        return contexto

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

        # Tag para títulos
        self.chat_area.tag_configure("titulo",
                                   font=("Segoe UI", 12, "bold"),
                                   foreground=self.cor_destaque)

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
            linha = linha.strip()
            if not linha:
                segmentos.append(("\n", "normal"))
                continue

            # Títulos (# texto)
            if re.match(r'^#{1,6}\s+', linha):
                titulo_texto = re.sub(r'^#{1,6}\s+', '', linha)
                segmentos.append((titulo_texto + "\n", "titulo"))

            # Listas (- item ou 1. item)
            elif re.match(r'^[-\*\+]\s+', linha):
                lista_texto = re.sub(r'^[-\*\+]\s+', '• ', linha)
                segmentos.append((lista_texto + "\n", "lista"))

            elif re.match(r'^\d+\.\s+', linha):
                lista_texto = re.sub(r'^\d+\.\s+', '→ ', linha)
                segmentos.append((lista_texto + "\n", "lista"))

            else:
                # Processar formatação inline
                self.processar_formatacao_inline(linha + "\n", segmentos)

        return segmentos

    def processar_formatacao_inline(self, texto, segmentos):
        """Processa formatação inline como negrito, itálico e código."""
        pos = 0

        # Procurar por padrões de markdown
        patterns = [
            (r'\*\*(.*?)\*\*', 'negrito'),  # **texto**
            (r'\*(.*?)\*', 'italico'),      # *texto*
            (r'`(.*?)`', 'codigo')          # `texto`
        ]

        # Encontrar todas as ocorrências
        matches = []
        for pattern, tag in patterns:
            for match in re.finditer(pattern, texto):
                matches.append((match.start(), match.end(), match.group(1), tag))

        # Ordenar por posição
        matches.sort(key=lambda x: x[0])

        # Processar texto com formatação
        for start, end, content, tag in matches:
            # Adicionar texto antes da formatação
            if pos < start:
                segmentos.append((texto[pos:start], "normal"))

            # Adicionar texto formatado
            segmentos.append((content, tag))
            pos = end

        # Adicionar texto restante
        if pos < len(texto):
            segmentos.append((texto[pos:], "normal"))

    def adicionar_mensagem_chat(self, remetente, mensagem, tipo):
        """Adiciona uma mensagem ao chat."""
        self.chat_area.config(state=tk.NORMAL)

        # Adicionar timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Inserir cabeçalho da mensagem
        self.chat_area.insert(tk.END, f"\n[{timestamp}] {remetente}:\n")

        # Processar markdown se for resposta da IA
        if tipo == "bot":
            segmentos = self.renderizar_markdown(mensagem)
            for texto, tag in segmentos:
                if tag == "normal":
                    self.chat_area.insert(tk.END, texto)
                else:
                    start_pos = self.chat_area.index(tk.END + "-1c")
                    self.chat_area.insert(tk.END, texto)
                    end_pos = self.chat_area.index(tk.END + "-1c")
                    self.chat_area.tag_add(tag, start_pos, end_pos)
        else:
            self.chat_area.insert(tk.END, mensagem)

        self.chat_area.insert(tk.END, "\n")

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

        if not self.df_carteiras.empty:
            dados_completos += "=== DADOS DE CARTEIRAS ===\n"
            # Converter para CSV string
            csv_carteiras = self.df_carteiras.to_csv(index=False)
            dados_completos += csv_carteiras + "\n"

        # Adicionar resumo estatístico
        dados_completos += "=== RESUMO ESTATÍSTICO ===\n"

        if not self.df_acoes.empty:
            dados_completos += f"AÇÕES: {len(self.df_acoes)} registros\n"
            numeric_cols = self.df_acoes.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                dados_completos += self.df_acoes[numeric_cols].describe().to_csv()
                dados_completos += "\n"

        if not self.df_carteiras.empty:
            dados_completos += f"CARTEIRAS: {len(self.df_carteiras)} registros\n"
            numeric_cols = self.df_carteiras.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                dados_completos += self.df_carteiras[numeric_cols].describe().to_csv()

        return dados_completos

    def processar_dados_csv(self, dados_csv):
        """Processa os dados com a IA."""
        try:
            # Prompt para análise dos dados CSV
            prompt_csv = f"""Você é um analista financeiro especializado em ações brasileiras. Analise os seguintes dados financeiros extraídos do site Investidor10:

{dados_csv}

## ANÁLISE SOLICITADA:

### 1. RESUMO EXECUTIVO
- Visão geral das empresas analisadas
- Número total de ações e setores representados
- Principais características do portfólio

### 2. ANÁLISE FUNDAMENTALISTA
- **Valuation**: Análise de P/L, P/VP, EV/EBITDA
- **Rentabilidade**: ROE, ROA, ROIC e margens
- **Crescimento**: Evolução de receitas e lucros
- **Solidez**: Endividamento e liquidez
- **Dividendos**: Dividend Yield e payout

### 3. RANKING DE QUALIDADE
- Top 5 melhores oportunidades (justifique com múltiplos)
- Top 5 ações com maior risco (identifique red flags)
- Ações com melhor relação risco/retorno

### 4. ANÁLISE SETORIAL
- Concentração por setor
- Setores mais atrativos vs. setores em alerta
- Comparação de múltiplos dentro dos setores

### 5. RECOMENDAÇÕES ESTRATÉGICAS
- **COMPRA FORTE**: Ações subvalorizadas com fundamentos sólidos
- **MANTER**: Ações bem posicionadas mas com preço justo
- **EVITAR**: Ações supervalorizadas ou com problemas fundamentais
- Sugestão de peso ideal para cada ação no portfólio

### 6. ALERTAS E RISCOS
- Empresas com métricas preocupantes
- Setores com risco elevado
- Concentração excessiva em determinados segmentos

### 7. OPORTUNIDADES ESPECIAIS
- Ações com potencial de recuperação
- Dividendos acima da média
- Empresas em crescimento sustentável

**IMPORTANTE**: Base suas análises exclusivamente nos dados fornecidos. Seja específico ao mencionar números e métricas. Priorize clareza e objetividade nas recomendações."""

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