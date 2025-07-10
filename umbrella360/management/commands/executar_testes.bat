@echo off
echo ========================================
echo    EXECUTANDO TESTES UMBRELLA360
echo ========================================
echo.

cd /d "c:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE"

echo Executando testes basicos...
python manage.py test umbrella360 --verbosity=2

echo.
echo ========================================
echo    EXECUTANDO TESTES COM COBERTURA
echo ========================================
echo.

echo Instalando coverage se necessario...
pip install coverage

echo.
echo Executando testes com coverage...
coverage run --source='.' manage.py test umbrella360
coverage report
coverage html

echo.
echo ========================================
echo    RESULTADOS DOS TESTES
echo ========================================
echo.
echo - Testes executados com sucesso!
echo - Relatorio de cobertura gerado em htmlcov/index.html
echo.

pause
