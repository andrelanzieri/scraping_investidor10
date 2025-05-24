@echo off
echo ============================================================
echo CRIADOR DE EXECUTAVEL - EXTRATOR INVESTIDOR10
echo ============================================================
echo.

REM Ativa o ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
)

REM Executa o script de build
echo Executando script de build...
python build_executable.py

echo.
echo Pressione qualquer tecla para fechar...
pause > nul