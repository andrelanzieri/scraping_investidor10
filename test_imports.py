#!/usr/bin/env python3
"""
Script de teste para verificar se todas as importações necessárias estão funcionando.
Execute este script antes de criar o executável para garantir que não há problemas de importação.
"""

import sys

def test_imports():
    """Testa todas as importações necessárias para o projeto."""
    print("Testando importações...")

    failed_imports = []
    optional_imports = []

    # Lista de módulos para testar (essenciais)
    essential_modules = [
        # Selenium
        ('selenium', 'Selenium WebDriver'),
        ('selenium.webdriver', 'Selenium WebDriver Core'),
        ('selenium.webdriver.chrome.service', 'Selenium Chrome Service'),
        ('selenium.webdriver.chrome.options', 'Selenium Chrome Options'),
        ('selenium.webdriver.common.by', 'Selenium By'),
        ('selenium.webdriver.support.ui', 'Selenium WebDriverWait'),
        ('selenium.webdriver.support.expected_conditions', 'Selenium Expected Conditions'),

        # WebDriver Manager (essenciais)
        ('webdriver_manager', 'WebDriver Manager'),
        ('webdriver_manager.chrome', 'WebDriver Manager Chrome'),
        ('webdriver_manager.core', 'WebDriver Manager Core'),

        # Pandas e Excel
        ('pandas', 'Pandas'),
        ('openpyxl', 'OpenPyXL'),
        ('openpyxl.workbook', 'OpenPyXL Workbook'),
        ('openpyxl.styles', 'OpenPyXL Styles'),

        # XlsxWriter
        ('xlsxwriter', 'XlsxWriter'),
        ('xlsxwriter.workbook', 'XlsxWriter Workbook'),
        ('xlsxwriter.worksheet', 'XlsxWriter Worksheet'),

        # Tkinter
        ('tkinter', 'Tkinter'),
        ('tkinter.ttk', 'Tkinter TTK'),
        ('tkinter.filedialog', 'Tkinter File Dialog'),
        ('tkinter.messagebox', 'Tkinter Message Box'),

        # Requests e rede
        ('requests', 'Requests'),
        ('urllib3', 'urllib3'),

        # XML/HTML
        ('lxml', 'LXML'),

        # Imagens
        ('PIL', 'Pillow'),

        # Packaging
        ('packaging', 'Packaging'),
        ('packaging.version', 'Packaging Version'),
    ]

    # Módulos opcionais (podem não existir em todas as versões)
    optional_modules = [
        ('webdriver_manager.core.utils', 'WebDriver Manager Utils'),
        ('webdriver_manager.core.download_manager', 'WebDriver Manager Download'),
        ('webdriver_manager.core.driver_cache', 'WebDriver Manager Cache'),
        ('webdriver_manager.core.config_manager', 'WebDriver Manager Config'),
        ('webdriver_manager.core.logger', 'WebDriver Manager Logger'),
        ('webdriver_manager.core.os_manager', 'WebDriver Manager OS'),
    ]

    # Testa módulos essenciais
    for module_name, description in essential_modules:
        try:
            __import__(module_name)
            print(f"[OK] {description}")
        except ImportError as e:
            print(f"[ERRO] {description}: {e}")
            failed_imports.append((module_name, description, str(e)))
        except Exception as e:
            print(f"[ERRO] {description}: {e}")
            failed_imports.append((module_name, description, str(e)))

    # Testa módulos opcionais
    for module_name, description in optional_modules:
        try:
            __import__(module_name)
            print(f"[OK] {description}")
        except ImportError as e:
            print(f"[OPCIONAL] {description}: {e}")
            optional_imports.append((module_name, description, str(e)))
        except Exception as e:
            print(f"[OPCIONAL] {description}: {e}")
            optional_imports.append((module_name, description, str(e)))

    print("\n" + "="*60)

    if failed_imports:
        print(f"ERRO: {len(failed_imports)} importações essenciais falharam:")
        for module_name, description, error in failed_imports:
            print(f"   - {description} ({module_name}): {error}")
        print("\nInstale as dependências faltantes com:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("SUCESSO: Todas as importações essenciais foram bem-sucedidas!")
        if optional_imports:
            print(f"INFO: {len(optional_imports)} importações opcionais falharam (isso é normal):")
            for module_name, description, error in optional_imports[:3]:  # Mostra apenas as primeiras 3
                print(f"   - {description}")
            if len(optional_imports) > 3:
                print(f"   ... e mais {len(optional_imports) - 3}")
        print("O projeto está pronto para criar o executável.")
        return True


def test_webdriver_manager_specifically():
    """Teste específico para webdriver_manager."""
    print("\nTestando WebDriver Manager especificamente...")

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("[OK] ChromeDriverManager importado com sucesso")

        # Teste de instanciação (sem baixar)
        manager = ChromeDriverManager()
        print("[OK] ChromeDriverManager instanciado com sucesso")

        return True
    except Exception as e:
        print(f"[ERRO] Erro no WebDriver Manager: {e}")
        return False


def test_excel_engines():
    """Teste específico para engines de Excel."""
    print("\nTestando engines de Excel...")

    try:
        import pandas as pd

        # Testa openpyxl
        try:
            import openpyxl
            print("[OK] OpenPyXL disponível")
        except ImportError:
            print("[ERRO] OpenPyXL não disponível")
            return False

        # Testa xlsxwriter
        try:
            import xlsxwriter
            print("[OK] XlsxWriter disponível")
        except ImportError:
            print("[ERRO] XlsxWriter não disponível")
            return False

        # Testa criação de ExcelWriter
        try:
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                tmp_path = tmp.name

            try:
                with pd.ExcelWriter(tmp_path, engine='xlsxwriter') as writer:
                    df_test = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
                    df_test.to_excel(writer, sheet_name='Test', index=False)
                print("[OK] ExcelWriter com xlsxwriter funcional")

                # Remove arquivo temporário
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

                return True
            except Exception as e:
                print(f"[ERRO] Problema com ExcelWriter: {e}")
                return False

        except Exception as e:
            print(f"[ERRO] Erro no teste de Excel: {e}")
            return False

    except Exception as e:
        print(f"[ERRO] Erro geral no teste de Excel: {e}")
        return False


def main():
    """Função principal."""
    print("TESTE DE IMPORTAÇÕES - EXTRATOR INVESTIDOR10")
    print("="*60)

    # Teste geral de importações
    imports_ok = test_imports()

    # Teste específico do webdriver_manager
    webdriver_ok = test_webdriver_manager_specifically()

    # Teste específico dos engines de Excel
    excel_ok = test_excel_engines()

    print("\n" + "="*60)
    print("RESULTADO FINAL:")

    if imports_ok and webdriver_ok and excel_ok:
        print("SUCESSO: TODOS OS TESTES ESSENCIAIS PASSARAM!")
        print("Você pode prosseguir com a criação do executável.")
        return True
    else:
        print("ERRO: ALGUNS TESTES ESSENCIAIS FALHARAM!")
        print("Corrija os problemas antes de criar o executável.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)