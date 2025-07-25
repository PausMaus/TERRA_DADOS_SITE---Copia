#!/usr/bin/env python
"""
Script para executar testes do sistema Umbrella360
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TERRA_DADOS_SITE.settings')
    django.setup()
    
    # Configurar runner de testes
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Executar testes específicos do umbrella360
    failures = test_runner.run_tests(["umbrella360"])
    
    if failures:
        sys.exit(1)
    else:
        print("\n✅ Todos os testes passaram com sucesso!")
        sys.exit(0)
