import json
import tkinter as tk
from tkinter import messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import os
import re
import subprocess
import threading
import time


class DataExtractor:
    """
    Classe responsável por toda a lógica de extração de dados do site Investidor10.
    Inclui configuração do WebDriver, extração de dados de ações e carteiras,
    processamento de seletores CSS e exportação para Excel.
    """

    def __init__(self, config, status_callback=None, cancelamento_event=None):
        """
        Inicializa o extrator de dados.

        Args:
            config (dict): Configurações da aplicação
            status_callback (callable): Função para atualizar status na interface
            cancelamento_event (threading.Event): Evento para controlar cancelamento
        """
        self.config = config
        self.status_callback = status_callback or (lambda msg, prog: print(msg))
        self.cancelamento_event = cancelamento_event or threading.Event()
        self.driver = None

    def setup_driver(self):
        """Configura e inicia o WebDriver do Chrome."""
        chrome_options = Options()
        if self.config["headless"]:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("detach", False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--enable-unsafe-swiftshader')
        chrome_options.add_argument('--disk-cache-size=52428800')
        chrome_options.add_argument('--disable-application-cache=false')

        profile_path = os.path.join(os.getcwd(), "chrome_profile")
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        chrome_options.add_argument(f"user-data-dir={profile_path}")

        self.status_callback("Iniciando navegador...", 10)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.implicitly_wait(5)
        return self.driver

    def verificar_cancelamento(self):
        """Verifica se o cancelamento foi solicitado."""
        return self.cancelamento_event.is_set()

    def access_site_and_await_login(self):
        """Acessa o site Investidor10 e aguarda o login do usuário, se necessário."""
        self.status_callback("Acessando o site Investidor10...", 20)
        self.driver.get("https://investidor10.com.br/")
        if not self.config["headless"]:
            messagebox.showinfo("Login Necessário",
                              "Faça login no site Investidor10. Clique em OK quando estiver pronto para continuar com a extração.")
        self.status_callback("Login confirmado, iniciando extrações...", 25)

    def extract_stock_data(self):
        """
        Realiza a extração de dados para as ações configuradas.

        Returns:
            list: Lista de dicionários, cada um representando os dados de uma ação.
        """
        self.status_callback("Iniciando extração de dados de AÇÕES...", 30)
        dados_acoes = []
        acoes = self.config["acoes"]
        colunas_personalizadas = self.config["colunas_personalizadas"]

        if not acoes:
            self.status_callback("Nenhuma ação para processar na extração de ações.", 40)
            return dados_acoes

        total_acoes = len(acoes)
        progresso_por_acao = 30 / total_acoes if total_acoes > 0 else 0
        progresso_base_acoes = 30

        for i, acao in enumerate(acoes):
            if self.verificar_cancelamento():
                self.status_callback("Extração de ações cancelada pelo usuário.", 0)
                break

            progresso_atual = progresso_base_acoes + (i * progresso_por_acao)
            self.status_callback(f"Processando ação {acao} ({i+1}/{total_acoes})...", int(progresso_atual))

            try:
                url = f"https://investidor10.com.br/acoes/{acao}/"
                self.driver.get(url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                resultado_acao = {"Ticker": acao, "Origem": "Ação"}
                if colunas_personalizadas:
                    self.extrair_colunas_personalizadas_otimizado(colunas_personalizadas, resultado_acao)
                dados_acoes.append(resultado_acao)
            except Exception as e:
                messagebox.showwarning("Erro Ação", f"Erro ao processar ação {acao}: {str(e)}")
                dados_acoes.append({"Ticker": acao, "Origem": "Ação", "Erro": str(e)})

        self.status_callback("Extração de dados de AÇÕES concluída.", 60)
        return dados_acoes

    def extract_portfolio_data(self):
        """
        Realiza a extração de dados para as carteiras configuradas.

        Returns:
            list: Lista de dicionários, cada um representando os dados de uma carteira.
        """
        if self.verificar_cancelamento():
            self.status_callback("Extração de carteiras cancelada pelo usuário.", 0)
            return []

        self.status_callback("Iniciando extração de dados de CARTEIRAS...", 65)
        dados_carteiras = []

        try:
            self.status_callback("Acessando página de carteiras...", 70)

            if self.verificar_cancelamento():
                self.status_callback("Extração de carteiras cancelada pelo usuário.", 0)
                return []

            self.driver.get("https://investidor10.com.br/carteiras/resumo/")

            if self.verificar_cancelamento():
                self.status_callback("Extração de carteiras cancelada pelo usuário.", 0)
                return []

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#Ticker-tickers_wrapper > div:nth-child(3)"))
            )

            self.status_callback("Extraindo dados da tabela de carteiras...", 80)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Ticker-tickers"))
                )
                raw_data_carteiras = self.extrair_dados_tabela(id_tabela="Ticker-tickers")
            except:
                self.status_callback("Fallback para seletor de tabela de carteiras...", 82)
                try:
                    tabela_wrapper = self.driver.find_element(By.CSS_SELECTOR, "#Ticker-tickers_wrapper")
                    WebDriverWait(tabela_wrapper, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )
                    raw_data_carteiras = self.extrair_dados_tabela(seletor_tabela="#Ticker-tickers_wrapper table#Ticker-tickers")
                    if not raw_data_carteiras:
                        raw_data_carteiras = self.extrair_dados_tabela(seletor_tabela="#Ticker-tickers_wrapper table")
                except Exception as e_fallback:
                    messagebox.showwarning("Erro Carteiras",
                                         f"Não foi possível localizar a tabela de carteiras após fallback: {str(e_fallback)}")
                    raw_data_carteiras = []

            # Adicionar "Origem" aos dados da carteira
            for linha_dict in raw_data_carteiras:
                linha_dict["Origem"] = "Carteira"
            dados_carteiras.extend(raw_data_carteiras)

            self.status_callback("Extração de dados de CARTEIRAS concluída.", 90)

        except Exception as e:
            messagebox.showerror("Erro Carteiras", f"Erro ao extrair dados das carteiras: {str(e)}")
            self.status_callback(f"Erro na extração de carteiras: {e}", 85)

        return dados_carteiras

    def extrair_colunas_personalizadas_otimizado(self, colunas_personalizadas, resultado_acao):
        """
        Otimiza a extração de múltiplas colunas personalizadas usando JavaScript
        e reduzindo o número de interações com o DOM
        """
        try:
            # Separar colunas por tipo para processamento em lote
            colunas_simples = [col for col in colunas_personalizadas if col["tipo"] == "simples"]
            colunas_avancadas = [col for col in colunas_personalizadas if col["tipo"] != "simples"]

            # Processar colunas simples em lote
            if colunas_simples:
                classes_busca = set(col["classe_busca"] for col in colunas_simples if "classe_busca" in col)
                elementos_por_classe = {}
                for classe in classes_busca:
                    elementos_por_classe[classe] = self.driver.find_elements(By.CLASS_NAME, classe)

                for coluna in colunas_simples:
                    try:
                        valor = "N/A"
                        if "classe_busca" in coluna and "classe_retorno" in coluna:
                            elementos = elementos_por_classe.get(coluna["classe_busca"], [])
                            if elementos:
                                for elem in elementos:
                                    try:
                                        valor_elem = elem.find_element(By.CLASS_NAME, coluna["classe_retorno"]).text
                                        if valor_elem:
                                            valor = valor_elem
                                            break
                                    except:
                                        continue
                        resultado_acao[coluna["nome"]] = valor
                    except:
                        resultado_acao[coluna["nome"]] = "N/A"

            # Processar colunas avançadas usando JavaScript quando possível
            if colunas_avancadas:
                seletores = [col["seletor_css"] for col in colunas_avancadas if col.get("seletor_css")]

                if seletores:
                    script = """
                    const results = {};
                    const seletores = arguments[0];

                    for (let i = 0; i < seletores.length; i++) {
                        try {
                            const elemento = document.querySelector(seletores[i]);
                            results[seletores[i]] = elemento ? elemento.textContent.trim() : 'N/A';
                        } catch (e) {
                            results[seletores[i]] = 'N/A';
                        }
                    }

                    return results;
                    """

                    resultados_js = self.driver.execute_script(script, seletores)

                    for coluna in colunas_avancadas:
                        if coluna.get("seletor_css") and coluna.get("seletor_css") in resultados_js:
                            resultado_acao[coluna["nome"]] = resultados_js[coluna["seletor_css"]]
                        else:
                            try:
                                if coluna.get("seletor_css"):
                                    resultado_acao[coluna["nome"]] = self.extrair_seletor_complexo(coluna["seletor_css"])
                                else:
                                    resultado_acao[coluna["nome"]] = "N/A"
                            except:
                                resultado_acao[coluna["nome"]] = "N/A"

        except Exception as e:
            # Em caso de erro, extrair cada coluna individualmente
            for coluna in colunas_personalizadas:
                try:
                    valor = "N/A"
                    if coluna["tipo"] == "simples":
                        if "classe_busca" in coluna and "classe_retorno" in coluna:
                            elementos = self.driver.find_elements(By.CLASS_NAME, coluna["classe_busca"])
                            if elementos:
                                for elem in elementos:
                                    try:
                                        valor_elem = elem.find_element(By.CLASS_NAME, coluna["classe_retorno"]).text
                                        if valor_elem:
                                            valor = valor_elem
                                            break
                                    except:
                                        continue
                        else:
                            valor = "Configuração de coluna simples incompleta"
                    else:
                        if coluna.get("seletor_css"):
                            valor = self.extrair_seletor_complexo(coluna["seletor_css"])
                        else:
                            valor = "Seletor CSS não definido"

                    resultado_acao[coluna["nome"]] = valor
                except Exception as e_col:
                    resultado_acao[coluna["nome"]] = f"Erro ao extrair coluna: {e_col}"

    def extrair_seletor_complexo(self, seletor_css):
        """
        Identifica e processa seletores complexos, particularmente aqueles relacionados a tabelas.
        """
        try:
            script = f"""
            try {{
                const element = document.querySelector('{seletor_css.replace("'", "\\'")}');
                return element ? element.textContent.trim() : 'N/A';
            }} catch (e) {{
                return 'N/A';
            }}
            """
            resultado = self.driver.execute_script(script)
            if resultado and resultado != "N/A":
                return resultado
        except Exception as e:
            pass

        try:
            elemento = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, seletor_css))
            )
            if elemento:
                return elemento.text.strip() or "N/A"
        except Exception as e:
            pass

        if ('tr' in seletor_css and 'td' in seletor_css) or \
           ('tr' in seletor_css and 'th' in seletor_css):
            linha_match = re.search(r'tr[^>]*nth-child\((\d+)\)', seletor_css)
            coluna_match = re.search(r'(?:td|th)[^>]*nth-child\((\d+)\)', seletor_css)

            linha = int(linha_match.group(1)) if linha_match else 1
            coluna = int(coluna_match.group(1)) if coluna_match else 1

            classe_linha = None
            classe_match = re.search(r'tr\.([a-zA-Z0-9_-]+)', seletor_css)
            if classe_match:
                classe_linha = classe_match.group(1)

            if classe_linha:
                if 'visible-even' in classe_linha:
                    return self.extrair_seletor_tr_visible_even(linha, coluna)
                else:
                    return self.extrair_celula_com_classe(linha, coluna, classe_linha)
            else:
                return self.extrair_celula_tabela(linha - 1, coluna - 1)

        return "N/A"

    def extrair_seletor_tr_visible_even(self, numero_linha, numero_coluna):
        """Função específica para tratar o seletor tr.visible-even:nth-child(X) > td:nth-child(Y)."""
        try:
            xpath = f"//tbody/tr[{numero_linha}]/td[{numero_coluna}]"
            try:
                elemento = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if elemento.is_displayed():
                    return elemento.text.strip() or "N/A"
            except:
                pass

            try:
                linhas = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                linhas_visiveis = [linha for linha in linhas if linha.is_displayed()]
                linhas_pares = [linha for i, linha in enumerate(linhas_visiveis) if i % 2 == 1]

                if len(linhas_pares) >= numero_linha // 2:
                    linha_index = (numero_linha // 2) - 1
                    if linha_index < len(linhas_pares):
                        linha = linhas_pares[linha_index]
                        celulas = linha.find_elements(By.TAG_NAME, "td")
                        if numero_coluna <= len(celulas):
                            return celulas[numero_coluna-1].text.strip() or "N/A"
            except:
                pass

            return self.extrair_celula_tabela(numero_linha-1, numero_coluna-1)

        except Exception as e:
            return "N/A"

    def extrair_celula_com_classe(self, linha, coluna, classe):
        """Extrai o texto de uma célula em uma linha com uma classe específica."""
        try:
            linhas = self.driver.find_elements(By.CSS_SELECTOR, f"tr.{classe}")
            linhas_visiveis = [l for l in linhas if l.is_displayed()]

            if len(linhas_visiveis) >= linha:
                linha_alvo = linhas_visiveis[linha-1]
                celulas = linha_alvo.find_elements(By.TAG_NAME, "td")

                if len(celulas) >= coluna:
                    return celulas[coluna-1].text.strip() or "N/A"

            return self.extrair_celula_tabela(linha-1, coluna-1)

        except Exception as e:
            return "N/A"

    def extrair_celula_tabela(self, linha, coluna, id_tabela=None):
        """Extrai uma célula específica de uma tabela."""
        try:
            seletor_xpath = f"//tbody/tr[{linha+1}]/td[{coluna+1}]"

            if id_tabela:
                seletor_xpath = f"//table[@id='{id_tabela}']{seletor_xpath}"

            elemento = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, seletor_xpath))
            )

            return elemento.text.strip()
        except:
            try:
                dados_tabela = self.extrair_dados_tabela(id_tabela)
                if dados_tabela and linha < len(dados_tabela):
                    row_data = dados_tabela[linha]
                    chaves = list(row_data.keys())
                    if coluna < len(chaves):
                        return row_data[chaves[coluna]]
            except:
                pass

            return "N/A"

    def extrair_dados_tabela(self, id_tabela=None, seletor_tabela=None):
        """Extrai todos os dados de uma tabela com desempenho otimizado."""
        return self._extrair_dados_tabela_selenium(id_tabela, seletor_tabela)

    def _extrair_dados_tabela_selenium(self, id_tabela=None, seletor_tabela=None):
        """Método de fallback para extrair tabela usando Selenium puro."""
        try:
            # Localizar a tabela
            tabela = None
            if id_tabela:
                tabela = self.driver.find_element(By.ID, id_tabela)
            elif seletor_tabela:
                tabela = self.driver.find_element(By.CSS_SELECTOR, seletor_tabela)
            else:
                seletores_comuns = [
                    "table",
                    "div.table",
                    ".table-responsive table",
                    ".dataTables_wrapper table",
                    "#Ticker-tickers"
                ]

                for seletor in seletores_comuns:
                    try:
                        tabela = self.driver.find_element(By.CSS_SELECTOR, seletor)
                        break
                    except:
                        continue

                if tabela is None:
                    try:
                        tabela = self.driver.find_element(By.TAG_NAME, "table")
                    except:
                        return []

            # Obter cabeçalhos
            headers_text = []
            try:
                headers = tabela.find_elements(By.CSS_SELECTOR, "thead th")
                if headers:
                    headers_text = [h.text.strip() for h in headers if h.text.strip()]
            except:
                pass

            if not headers_text:
                try:
                    primeira_linha = tabela.find_element(By.CSS_SELECTOR, "tr:first-child")
                    headers = primeira_linha.find_elements(By.TAG_NAME, "th")
                    if headers:
                        headers_text = [h.text.strip() for h in headers if h.text.strip()]
                    else:
                        headers = primeira_linha.find_elements(By.TAG_NAME, "td")
                        if headers:
                            headers_text = [h.text.strip() for h in headers if h.text.strip()]
                except:
                    pass

            # Obter linhas e dados
            rows = []
            try:
                tbody = tabela.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
            except:
                if headers_text:
                    rows = tabela.find_elements(By.CSS_SELECTOR, "tr:not(:first-child)")
                else:
                    rows = tabela.find_elements(By.TAG_NAME, "tr")

            rows = [row for row in rows if row.is_displayed()]

            # Extrair dados
            result = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue

                row_data = {}
                if headers_text:
                    for i, cell in enumerate(cells):
                        key = headers_text[i] if i < len(headers_text) else f"Coluna {i+1}"
                        row_data[key] = cell.text.strip()
                else:
                    for i, cell in enumerate(cells):
                        row_data[f"Coluna {i+1}"] = cell.text.strip()

                result.append(row_data)

            return result

        except Exception as e:
            print(f"Erro no fallback de extração de tabela: {str(e)}")
            return []

    def export_to_excel(self, df_acoes, df_carteiras):
        """Exporta os dados para Excel com formatação adequada."""
        if df_acoes.empty and df_carteiras.empty:
            messagebox.showwarning("Aviso", "Não há dados para exportar (nem ações, nem carteiras)")
            return

        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Salvar dados como"
            )

            if not filepath:
                return

            df_acoes_export = df_acoes.copy() if not df_acoes.empty else pd.DataFrame()
            df_carteiras_export = df_carteiras.copy() if not df_carteiras.empty else pd.DataFrame()

            if not df_acoes_export.empty and "Origem" in df_acoes_export.columns:
                df_acoes_export.drop(columns=["Origem"], inplace=True)
            if not df_carteiras_export.empty and "Origem" in df_carteiras_export.columns:
                df_carteiras_export.drop(columns=["Origem"], inplace=True)

            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                self._write_dataframe_to_excel_sheet(writer, df_acoes_export, 'Acoes')
                self._write_dataframe_to_excel_sheet(writer, df_carteiras_export, 'Carteiras')

            try:
                if os.name == 'nt':  # Windows
                    abs_filepath = os.path.abspath(filepath)
                    messagebox.showinfo("Exportação Concluída",
                                      f"Os dados foram exportados para:\n{abs_filepath}\n\nA pasta contendo o arquivo será aberta.")
                    subprocess.Popen(f'explorer /select,"{abs_filepath}"', shell=True)
                else:
                    messagebox.showinfo("Exportação Concluída",
                                      f"Dados exportados para {filepath}.\nPor favor, navegue até a pasta para abrir o arquivo manualmente.")
            except Exception as e_open:
                messagebox.showwarning("Aviso de Abertura de Pasta",
                                     f"Dados exportados para {filepath}, mas ocorreu um erro ao tentar abrir a pasta: {str(e_open)}")

        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Erro ao exportar os dados: {str(e)}")

    def _write_dataframe_to_excel_sheet(self, writer, df, sheet_name):
        """Escreve um DataFrame em uma aba específica do Excel com formatação."""
        if df.empty:
            return

        workbook = writer.book
        format_text = workbook.add_format({'num_format': '@'})
        format_number = workbook.add_format({'num_format': '#,##0.00'})
        format_currency = workbook.add_format({'num_format': 'R$ #,##0.00'})
        format_percentage = workbook.add_format({'num_format': '0.00%'})

        coluna_configs = {col_conf["nome"]: col_conf for col_conf in self.config.get("colunas_personalizadas", [])}
        df_processed = df.copy()

        for col_name in df_processed.columns:
            col_conf = coluna_configs.get(col_name)
            formato_excel = col_conf.get("formato_excel", "Texto") if col_conf else "Texto"

            if formato_excel in ["Número", "Moeda", "Porcentagem"]:
                original_series = df_processed[col_name].copy()
                try:
                    current_col_as_str = df_processed[col_name].astype(str)
                    cleaned_col = current_col_as_str.str.replace('R$', '', regex=False)
                    cleaned_col = cleaned_col.str.replace('%', '', regex=False)
                    cleaned_col = cleaned_col.str.strip()
                    cleaned_col = cleaned_col.str.replace(r'(?<=\d)\.(?=\d{3}(?!\d))', '', regex=True)
                    cleaned_col = cleaned_col.str.replace(',', '.', regex=False)

                    numeric_series = pd.to_numeric(cleaned_col, errors='coerce')

                    if formato_excel == "Porcentagem":
                        df_processed[col_name] = numeric_series / 100.0
                    else:
                        df_processed[col_name] = numeric_series

                    if df_processed[col_name].isnull().all() and not original_series.isnull().all():
                        df_processed[col_name] = original_series
                except Exception:
                    df_processed[col_name] = original_series

        df_processed.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]

        for col_num, column_title in enumerate(df_processed.columns):
            col_conf = coluna_configs.get(column_title)
            formato_excel = col_conf.get("formato_excel", "Texto") if col_conf else "Texto"

            is_numeric_and_valid = pd.api.types.is_numeric_dtype(df_processed[column_title]) and not df_processed[column_title].isnull().all()
            if df[column_title].isnull().all() and formato_excel != "Texto":
                is_numeric_and_valid = False

            if formato_excel == "Moeda" and is_numeric_and_valid:
                worksheet.set_column(col_num, col_num, 18, format_currency)
            elif formato_excel == "Porcentagem" and is_numeric_and_valid:
                worksheet.set_column(col_num, col_num, 12, format_percentage)
            elif formato_excel == "Número" and is_numeric_and_valid:
                worksheet.set_column(col_num, col_num, 15, format_number)
            else:
                worksheet.set_column(col_num, col_num, 15, format_text)

    def cleanup(self):
        """Limpa recursos do extrator."""
        if self.driver:
            self.driver.quit()
            self.driver = None