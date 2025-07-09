import pandas as pd
import os
import subprocess
from tkinter import filedialog, messagebox

class ExcelExporter:
    """
    Classe responsável por exportar DataFrames para um arquivo Excel com formatação.
    """

    def __init__(self, config):
        """
        Inicializa o exportador de Excel.

        Args:
            config (dict): Configurações da aplicação, incluindo formatação de colunas.
        """
        self.config = config

    def export_to_excel(self, df_acoes, df_fiis=None, df_carteiras_acoes=None, df_carteiras_fiis=None):
        """Exporta os dados para Excel com formatação adequada."""
        if (df_acoes.empty and (df_fiis is None or df_fiis.empty) and
            (df_carteiras_acoes is None or df_carteiras_acoes.empty) and
            (df_carteiras_fiis is None or df_carteiras_fiis.empty)):
            messagebox.showwarning("Aviso", "Não há dados para exportar")
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
            df_fiis_export = df_fiis.copy() if df_fiis is not None and not df_fiis.empty else pd.DataFrame()
            df_carteiras_acoes_export = df_carteiras_acoes.copy() if df_carteiras_acoes is not None and not df_carteiras_acoes.empty else pd.DataFrame()
            df_carteiras_fiis_export = df_carteiras_fiis.copy() if df_carteiras_fiis is not None and not df_carteiras_fiis.empty else pd.DataFrame()

            # Remover coluna "Origem" se existir
            for df_export in [df_acoes_export, df_fiis_export, df_carteiras_acoes_export, df_carteiras_fiis_export]:
                if not df_export.empty and "Origem" in df_export.columns:
                    df_export.drop(columns=["Origem"], inplace=True)

            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                if not df_acoes_export.empty:
                    self._write_dataframe_to_excel_sheet(writer, df_acoes_export, 'Acoes', 'colunas_personalizadas')

                if not df_fiis_export.empty:
                    self._write_dataframe_to_excel_sheet(writer, df_fiis_export, 'FIIs', 'colunas_personalizadas_fiis')

                if not df_carteiras_acoes_export.empty:
                    self._write_dataframe_to_excel_sheet(writer, df_carteiras_acoes_export, 'Carteira_Acoes')

                if not df_carteiras_fiis_export.empty:
                    self._write_dataframe_to_excel_sheet(writer, df_carteiras_fiis_export, 'Carteira_FIIs')

            self._show_success_message(filepath, df_acoes_export, df_fiis_export, df_carteiras_acoes_export, df_carteiras_fiis_export)

        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Erro ao exportar os dados: {str(e)}")

    def _write_dataframe_to_excel_sheet(self, writer, df, sheet_name, config_key='colunas_personalizadas'):
        """Escreve um DataFrame em uma aba específica do Excel com formatação."""
        if df.empty:
            return

        workbook = writer.book
        format_text = workbook.add_format({'num_format': '@'})
        format_number = workbook.add_format({'num_format': '#,##0.00'})
        format_currency = workbook.add_format({'num_format': 'R$ #,##0.00'})
        format_percentage = workbook.add_format({'num_format': '0.00%'})

        coluna_configs = {col_conf["nome"]: col_conf for col_conf in self.config.get(config_key, [])}
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

    def _show_success_message(self, filepath, df_acoes, df_fiis=None, df_carteiras_acoes=None, df_carteiras_fiis=None):
        """Exibe a mensagem de sucesso e abre a pasta do arquivo."""
        tipos_exportados = []
        if not df_acoes.empty:
            tipos_exportados.append("AÇÕES")
        if df_fiis is not None and not df_fiis.empty:
            tipos_exportados.append("FIIs")
        if df_carteiras_acoes is not None and not df_carteiras_acoes.empty:
            tipos_exportados.append("CARTEIRA DE AÇÕES")
        if df_carteiras_fiis is not None and not df_carteiras_fiis.empty:
            tipos_exportados.append("CARTEIRA DE FIIs")


        if len(tipos_exportados) > 1:
            success_msg = f"Os dados de {', '.join(tipos_exportados[:-1])} e {tipos_exportados[-1]} foram exportados para:"
        elif len(tipos_exportados) == 1:
            success_msg = f"Os dados de {tipos_exportados[0]} foram exportados para:"
        else:
            success_msg = "Os dados foram exportados para:"

        try:
            if os.name == 'nt':  # Windows
                abs_filepath = os.path.abspath(filepath)
                messagebox.showinfo("Exportação Concluída",
                                  f"{success_msg}\n{abs_filepath}\n\nA pasta contendo o arquivo será aberta.")
                subprocess.Popen(f'explorer /select,"{abs_filepath}"', shell=True)
            else:
                messagebox.showinfo("Exportação Concluída",
                                  f"{success_msg} {filepath}.\nPor favor, navegue até a pasta para abrir o arquivo manualmente.")
        except Exception as e_open:
            messagebox.showwarning("Aviso de Abertura de Pasta",
                                 f"Dados exportados para {filepath}, mas ocorreu um erro ao tentar abrir a pasta: {str(e_open)}")
