from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab import base
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.FERRAMENTAS.umbrellab.base import  search_units, unidades_simples
from umbrella360.models import Empresa, Unidade
import json
import pandas as pd
import time
from termcolor import colored


deposito = rf"C:\TERRA DADOS\laboratorium\Site\terra_dados_site\TERRA_DADOS_SITE\umbrella360\deposito"

WIALON_TOKEN_BRAS = "517e0e42b9a966f628a9b8cffff3ffc3F57FA748F075501F5667A26AFA278AC983E1C616"

WIALON_TOKEN_PLAC = "82fee29da11ea1312f1c8235247a0d82DC991707A4435C60FE7FFB27BD0D0F32BF59B709"


# Tokens para diferentes ambientes
Tokens_Wialon = {
    "CPBRASCELL": WIALON_TOKEN_BRAS,
    "PLACIDO": WIALON_TOKEN_PLAC
}


class Command(BaseCommand):
    help = 'Importa dados da API Wialon'
    
    def handle(self, *args, **kwargs):
        # Processa cada empresa em sequência
        empresas = [
            (WIALON_TOKEN_BRAS, "CPBRASCELL"),
            (WIALON_TOKEN_PLAC, "PLACIDO")
        ]
        
        for token, empresa_nome in empresas:
            self.stdout.write(
                self.style.WARNING(f'\n{"="*60}')
            )
            self.stdout.write(
                self.style.WARNING(f'PROCESSANDO EMPRESA: {empresa_nome}')
            )
            self.stdout.write(
                self.style.WARNING(f'{"="*60}')
            )
            
            try:
                self.principal(token, empresa_nome)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {empresa_nome} processada com sucesso!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao processar {empresa_nome}: {e}')
                )
            
            # Pausa entre empresas para evitar sobrecarga
            time.sleep(2)

    def principal(self, token, empresa_nome):
        self.stdout.write(self.style.SUCCESS(f'Iniciando importação de dados para a empresa: {empresa_nome}'))
        
        # Cria ou atualiza a empresa no banco de dados e obtém a instância
        empresa_obj = self.create_or_update_empresas(empresa_nome)
        if not empresa_obj:
            self.stdout.write(self.style.ERROR(f'Falha ao criar/obter empresa {empresa_nome}'))
            return

        # Inicia a sessão Wialon
        self.stdout.write(self.style.SUCCESS(f'Iniciando sessão Wialon para {empresa_nome}...'))

        sid = Wialon.authenticate_with_wialon(token)
        if not sid:
            self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
            return

        try:
            # Obtém unidades do banco de dados para esta empresa
            unidades_db = Unidade.objects.filter(empresa=empresa_obj)
            self.stdout.write(f'Unidades já cadastradas para {empresa_nome}: {len(unidades_db)}')

            # Busca unidades na API
            unidades = search_units(sid)
            if not unidades:
                self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada na API.'))
                return

            # Coloca os dados em um dataframe
            df_unidades = pd.DataFrame(unidades)
            self.stdout.write(f'Unidades encontradas na API: {colored(str(len(df_unidades)), "green")}')
            
            # Processa e limpa os dados das unidades
            for unidade in unidades:
                unidade_id = unidade['id']
                unidade_nome = unidade['nm']
                
                # Separa o nome da unidade por delimitadores '_'
                partes_nome = unidade_nome.split('_')
                placa = partes_nome[0].strip() if partes_nome else ''
                restante_nome = ' '.join([parte.strip() for parte in partes_nome[1:]]) if len(partes_nome) > 1 else ''
                
                # Atualiza os dados da unidade
                unidade['placa'] = placa
                unidade['nm_original'] = unidade_nome
                unidade['nm'] = restante_nome if restante_nome else placa
                
                self.stdout.write(f'Unidade: {unidade["nm"]} | Placa: {placa} (ID: {unidade_id}) - Empresa: {empresa_nome}')

            # Compara as unidades com o banco de dados
            unidades_db_ids = [unidade.id for unidade in unidades_db]
            unidades_novas = [unidade for unidade in unidades if unidade['id'] not in unidades_db_ids]
            
            self.stdout.write(f'Unidades no banco de dados: {colored(str(len(unidades_db_ids)), "green")}')
            self.stdout.write(f'Unidades novas: {colored(str(len(unidades_novas)), "green")}')

            # Cria as novas unidades no banco de dados
            if unidades_novas:
                self.create_or_update_units(unidades_novas, empresa_obj)
            else:
                self.stdout.write(self.style.SUCCESS('Nenhuma unidade nova para cadastrar.'))

            # Salva dados em arquivo para backup
            self.salvar_dados_empresa(df_unidades, empresa_nome)

        finally:
            # Encerra a sessão Wialon
            Wialon.wialon_logout(sid)
            self.stdout.write(self.style.SUCCESS(f'Sessão Wialon encerrada para {empresa_nome}.'))

    def create_or_update_units(self, unidades_novas, empresa_obj):
        """
        Cria ou atualiza unidades no banco de dados
        :param unidades_novas: Lista de dicionários com dados das unidades
        :param empresa_obj: Instância da model Empresa
        """
        contador_criadas = 0
        contador_erros = 0
        
        for unidade in unidades_novas:
            try:
                # Verifica se a unidade já existe (dupla verificação)
                if Unidade.objects.filter(id=unidade['id']).exists():
                    self.stdout.write(f'Unidade {unidade["id"]} já existe, pulando...')
                    continue
                
                nova_unidade = Unidade.objects.create(
                    id=unidade['id'],
                    empresa=empresa_obj,  # Passa a instância da empresa, não a string
                    nome=unidade.get('nm', ''),
                    placa=unidade.get('placa', ''),
                    # Adicione outros campos conforme sua model
                    # cls=unidade.get('cls', ''),
                    # descricao=unidade.get('descricao', ''),
                )
                contador_criadas += 1
                self.stdout.write(f'✅ Unidade criada: {nova_unidade.nome} (ID: {nova_unidade.id})')
                
            except Exception as e:
                contador_erros += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao criar unidade {unidade.get("id", "N/A")}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Resumo: {contador_criadas} unidades criadas, {contador_erros} erros')
        )

    def create_or_update_empresas(self, empresa_nome):
        """
        Cria ou atualiza empresas e retorna a instância
        :param empresa_nome: Nome da empresa
        :return: Instância da empresa ou None em caso de erro
        """
        try:
            empresa, created = Empresa.objects.get_or_create(nome=empresa_nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Empresa {empresa_nome} criada.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Empresa {empresa_nome} já existe.'))
            return empresa
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao criar/obter empresa {empresa_nome}: {e}'))
            return None

    def salvar_dados_empresa(self, df_unidades, empresa_nome):
        """
        Salva dados da empresa em arquivo Excel
        """
        try:
            import os
            if not os.path.exists(deposito):
                os.makedirs(deposito)
            
            arquivo = os.path.join(deposito, f"unidades_{empresa_nome}_{time.strftime('%Y%m%d_%H%M%S')}.xlsx")
            df_unidades.to_excel(arquivo, index=False, engine='openpyxl')
            self.stdout.write(self.style.SUCCESS(f'Dados salvos em: {arquivo}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao salvar dados: {e}'))

    def process_units(self, sid, unidades, empresa_nome):
        """
        Processa relatórios para as unidades (método opcional)
        """
        for unidade in unidades:
            unidade_id = unidade['id']
            unidade_nome = unidade['nm']
            self.stdout.write(f'Processando unidade: {unidade_nome} (ID: {unidade_id}) - {empresa_nome}')

            try:
                # Coleta dados de relatório para 7 dias
                resultado = Wialon.Colheitadeira_JSON(sid, unidade_id, id_relatorio=59, tempo_dias=7, periodo='Ultimos 7 dias')
                if resultado:
                    self.stdout.write(f'✅ Relatório processado para {unidade_nome}')
                else:
                    self.stdout.write(f'⚠️ Nenhum dado de relatório para {unidade_nome}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao processar relatório de {unidade_nome}: {e}'))