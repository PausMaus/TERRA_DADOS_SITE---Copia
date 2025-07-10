@echo off
REM Script de demonstração para os comandos de importação
REM Execute este script para ver os comandos em ação

echo.
echo ================================================
echo    DEMONSTRAÇÃO DOS COMANDOS DE IMPORTAÇÃO
echo ================================================
echo.

REM Navegar para o diretório do projeto
cd /d "c:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE"

echo 1. Configurando ambiente Python...
echo.
call conda activate myenv
if %errorlevel% neq 0 (
    echo Erro: Não foi possível ativar o ambiente conda
    pause
    exit /b 1
)

echo 2. Testando os comandos com dados de exemplo...
echo.
python umbrella360\management\commands\test_import_commands.py

echo.
echo ================================================
echo    COMANDOS DISPONÍVEIS PARA USO MANUAL
echo ================================================
echo.
echo Para usar os comandos manualmente, execute:
echo.
echo 1. IMPORTAÇÃO DE MOTORISTAS:
echo    python manage.py IMP_L_MOT caminho\para\arquivo.xlsx
echo    python manage.py IMP_L_MOT caminho\para\arquivo.xlsx --dry-run
echo    python manage.py IMP_L_MOT caminho\para\arquivo.xlsx --update
echo.
echo 2. IMPORTAÇÃO DE CAMINHÕES:
echo    python manage.py IMP_CAM caminho\para\arquivo.xlsx
echo    python manage.py IMP_CAM caminho\para\arquivo.xlsx --dry-run
echo    python manage.py IMP_CAM caminho\para\arquivo.xlsx --update
echo.
echo 3. VERIFICAR DADOS NO ADMIN:
echo    python manage.py runserver
echo    Acesse: http://localhost:8000/admin/
echo.
echo ================================================
echo    ARQUIVOS DE DOCUMENTAÇÃO
echo ================================================
echo.
echo - README_IMPORT_COMMANDS.md     : Documentação completa
echo - EXEMPLO_PRATICO_IMPORT.md     : Exemplo prático de uso
echo - test_import_commands.py       : Script de teste
echo.
echo Para visualizar a documentação, abra os arquivos .md em:
echo umbrella360\management\commands\
echo.

pause
