@echo off
REM Script completo para importar todos os dados do Umbrella360
REM Execute este script para importar: motoristas, caminhões, viagens de motoristas e viagens de caminhões

echo.
echo ================================================================
echo           IMPORTAÇÃO COMPLETA - UMBRELLA360
echo ================================================================
echo.

REM Navegar para o diretório do projeto
cd /d "c:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE"

REM Configurar variáveis de caminho dos arquivos
set "CAMINHO_DADOS=C:\TERRA DADOS\laboratorium\Site\Deposito\Apresentação"
set "MOTORISTAS=%CAMINHO_DADOS%\Lista_Motoristas.xlsx"
set "CAMINHOES=%CAMINHO_DADOS%\Lista_Caminhoes.xlsx"
set "VIAGENS_MOT=%CAMINHO_DADOS%\Viagens_Motoristas.xlsx"
set "VIAGENS_CAM=%CAMINHO_DADOS%\Viagens_Caminhoes.xlsx"

echo 1. Ativando ambiente Python...
call conda activate VENV_01
if %errorlevel% neq 0 (
    echo Erro: Não foi possível ativar o ambiente conda
    pause
    exit /b 1
)

echo.
echo ================================================================
echo    PASSO 1: IMPORTAR MOTORISTAS
echo ================================================================
echo.

REM Verificar se arquivo existe
if not exist "%MOTORISTAS%" (
    echo ❌ Arquivo não encontrado: %MOTORISTAS%
    echo Verifique se o arquivo existe no caminho especificado.
    pause
    exit /b 1
)

echo 🧪 Simulando importação de motoristas...
python manage.py IMP_L_MOT "%MOTORISTAS%" --dry-run

echo.
echo Pressione qualquer tecla para confirmar a importação real...
pause

echo 📝 Importando motoristas...
python manage.py IMP_L_MOT "%MOTORISTAS%"

if %errorlevel% neq 0 (
    echo ❌ Erro na importação de motoristas
    pause
    exit /b 1
)

echo.
echo ================================================================
echo    PASSO 2: IMPORTAR CAMINHÕES
echo ================================================================
echo.

REM Verificar se arquivo existe
if not exist "%CAMINHOES%" (
    echo ❌ Arquivo não encontrado: %CAMINHOES%
    echo Verifique se o arquivo existe no caminho especificado.
    pause
    exit /b 1
)

echo 🧪 Simulando importação de caminhões...
python manage.py IMP_CAM "%CAMINHOES%" --dry-run

echo.
echo Pressione qualquer tecla para confirmar a importação real...
pause

echo 🚛 Importando caminhões...
python manage.py IMP_CAM "%CAMINHOES%"

if %errorlevel% neq 0 (
    echo ❌ Erro na importação de caminhões
    pause
    exit /b 1
)

echo.
echo ================================================================
echo    PASSO 3: IMPORTAR VIAGENS DE MOTORISTAS
echo ================================================================
echo.

REM Verificar se arquivo existe
if not exist "%VIAGENS_MOT%" (
    echo ❌ Arquivo não encontrado: %VIAGENS_MOT%
    echo Verifique se o arquivo existe no caminho especificado.
    pause
    exit /b 1
)

echo 🧪 Simulando importação de viagens de motoristas...
python manage.py importar_viagens_motoristas "%VIAGENS_MOT%" --dry-run

echo.
echo Pressione qualquer tecla para confirmar a importação real...
pause

echo 📊 Importando viagens de motoristas...
python manage.py importar_viagens_motoristas "%VIAGENS_MOT%"

if %errorlevel% neq 0 (
    echo ❌ Erro na importação de viagens de motoristas
    pause
    exit /b 1
)

echo.
echo ================================================================
echo    PASSO 4: IMPORTAR VIAGENS DE CAMINHÕES
echo ================================================================
echo.

REM Verificar se arquivo existe
if not exist "%VIAGENS_CAM%" (
    echo ❌ Arquivo não encontrado: %VIAGENS_CAM%
    echo Verifique se o arquivo existe no caminho especificado.
    pause
    exit /b 1
)

echo 🧪 Simulando importação de viagens de caminhões...
python manage.py importar_viagens_caminhoes "%VIAGENS_CAM%" --dry-run

echo.
echo Pressione qualquer tecla para confirmar a importação real...
pause

echo 📊 Importando viagens de caminhões...
python manage.py importar_viagens_caminhoes "%VIAGENS_CAM%"

if %errorlevel% neq 0 (
    echo ❌ Erro na importação de viagens de caminhões
    pause
    exit /b 1
)

echo.
echo ================================================================
echo                    IMPORTAÇÃO CONCLUÍDA
echo ================================================================
echo.

echo 🎉 TODAS AS IMPORTAÇÕES FORAM CONCLUÍDAS COM SUCESSO!
echo.
echo Resumo do que foi importado:
echo ✅ Motoristas únicos
echo ✅ Caminhões únicos  
echo ✅ Viagens de motoristas
echo ✅ Viagens de caminhões
echo.
echo 📊 Para verificar os dados importados:
echo 1. Execute: python manage.py runserver
echo 2. Acesse: http://localhost:8000/admin/
echo 3. Navegue para: Umbrella360
echo.
echo 📁 Arquivos processados:
echo   - %MOTORISTAS%
echo   - %CAMINHOES%
echo   - %VIAGENS_MOT%
echo   - %VIAGENS_CAM%
echo.

pause
