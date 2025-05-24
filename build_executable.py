te#!/usr/bin/env python3
"""
Script para criar executável do Extrator de Dados - Investidor10
Versão 2.0 - Janeiro 2025

Este script automatiza o processo de criação do executável usando PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def test_imports():
    """Testa se todas as importações necessárias estão funcionando."""
    print("🧪 Testando importações antes do build...")

    try:
        # Executa o script de teste
        result = subprocess.run([sys.executable, "test_imports.py"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Teste de importações passou!")
            return True
        else:
            print("❌ Teste de importações falhou:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar teste de importações: {e}")
        return False


def check_pyinstaller():
    """Verifica se o PyInstaller está instalado."""
    try:
        import PyInstaller
        print("✓ PyInstaller encontrado")
        return True
    except ImportError:
        print("✗ PyInstaller não encontrado")
        return False


def install_pyinstaller():
    """Instala o PyInstaller."""
    print("Instalando PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller instalado com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("✗ Erro ao instalar PyInstaller")
        return False


def clean_build_dirs():
    """Remove diretórios de build anteriores."""
    dirs_to_clean = ['build', 'dist', '__pycache__']

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removendo diretório: {dir_name}")
            shutil.rmtree(dir_name)


def ensure_hooks_directory():
    """Garante que o diretório de hooks existe."""
    hooks_dir = Path("hooks")
    if not hooks_dir.exists():
        hooks_dir.mkdir()
        print("✓ Diretório hooks criado")
    return True


def build_executable():
    """Constrói o executável usando PyInstaller."""
    print("Iniciando build do executável...")

    try:
        # Comando para build usando o arquivo .spec
        cmd = [sys.executable, "-m", "PyInstaller", "build_exe.spec", "--clean"]

        print("Executando comando:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Executável criado com sucesso!")
            print("Localização: dist/ExtractorInvestidor10.exe")
            return True
        else:
            print("✗ Erro durante o build:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        return False


def create_release_package():
    """Cria um pacote de release com o executável e arquivos necessários."""
    release_dir = Path("release")

    # Remove diretório de release anterior
    if release_dir.exists():
        shutil.rmtree(release_dir)

    # Cria novo diretório de release
    release_dir.mkdir()

    # Copia executável
    exe_path = Path("dist/ExtractorInvestidor10.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "ExtractorInvestidor10.exe")
        print("✓ Executável copiado para release/")

    # Copia arquivos importantes
    files_to_copy = ["README.md", "config.json"]
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir / file_name)
            print(f"✓ {file_name} copiado para release/")

    # Cria diretório screenshots se não existir
    screenshots_dir = release_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    # Copia screenshots se existirem
    if os.path.exists("screenshots"):
        for item in os.listdir("screenshots"):
            src = Path("screenshots") / item
            dst = screenshots_dir / item
            if src.is_file():
                shutil.copy2(src, dst)
        print("✓ Screenshots copiados para release/")

    print(f"✓ Pacote de release criado em: {release_dir.absolute()}")


def main():
    """Função principal."""
    print("=" * 60)
    print("CRIADOR DE EXECUTÁVEL - EXTRATOR INVESTIDOR10")
    print("=" * 60)

    # Verifica se está no diretório correto
    if not os.path.exists("main.py"):
        print("✗ Erro: Execute este script no diretório raiz do projeto")
        return False

    # Testa importações antes de prosseguir
    if not test_imports():
        print("✗ Erro: Problemas com importações detectados")
        print("💡 Execute 'pip install -r requirements.txt' para corrigir")
        return False

    # Verifica/instala PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False

    # Garante que o diretório hooks existe
    ensure_hooks_directory()

    # Limpa diretórios de build anteriores
    clean_build_dirs()

    # Constrói o executável
    if not build_executable():
        return False

    # Cria pacote de release
    create_release_package()

    print("\n" + "=" * 60)
    print("BUILD CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("O executável está disponível em:")
    print("- dist/ExtractorInvestidor10.exe")
    print("- release/ExtractorInvestidor10.exe (pacote completo)")
    print("\nO pacote 'release/' contém tudo que você precisa para distribuir.")
    print("\n💡 Teste o executável antes de publicar:")
    print("   cd release && ExtractorInvestidor10.exe")

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n✗ Build falhou. Verifique os erros acima.")
        sys.exit(1)