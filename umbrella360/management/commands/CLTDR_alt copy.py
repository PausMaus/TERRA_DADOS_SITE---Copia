from django.core.management.base import BaseCommand
from umbrella360.FERRAMENTAS.umbrellab import Wialon
from umbrella360.FERRAMENTAS.umbrellab import base
from umbrella360.FERRAMENTAS.umbrellab.Wialon import *
from umbrella360.FERRAMENTAS.umbrellab.base import  search_units, unidades_simples
from umbrella360.models import Empresa, Unidade, Viagem_CAM, Caminhao
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

        self.principal(WIALON_TOKEN_BRAS, "CPBRASCELL")
        #self.principal(WIALON_TOKEN_PLAC, "PLACIDO")


    def principal(self, token, empresa_nome):
        self.stdout.write(self.style.SUCCESS(f'Iniciando importação de dados para a empresa: {empresa_nome}'))


        # Inicia a sessão Wialon
        self.stdout.write(self.style.SUCCESS(f'Iniciando sessão Wialon para {empresa_nome}...'))

        sid = Wialon.authenticate_with_wialon(token)
        if not sid:
                self.stdout.write(self.style.ERROR('Falha ao iniciar sessão Wialon.'))
                return


        #processa as unidades
        self.process_units(sid)






        # Encerra a sessão Wialon
        Wialon.wialon_logout(sid)

        self.stdout.write(self.style.SUCCESS(f'Sessão Wialon encerrada para {empresa_nome}.'))


        #######################################################################################

    def atualiza_unidades(self, sid, empresa_nome):
                 # Busca unidades
        unidades = unidades_simples(sid)
        if not unidades:
            self.stdout.write(self.style.ERROR('Nenhuma unidade encontrada.'))
            return
        


        #coloca os dados em um dataframe
        df_unidades = pd.DataFrame(unidades)
        print(f'Unidades encontradas:' , colored(f'{len(df_unidades)}', 'green'))
        print(f'Unidades: {df_unidades}')
        for unidade in df_unidades.itertuples(index=False):
            unidade_id = unidade.id
            unidade_nome = unidade.nm
            #separa o nome da unidade por delimitadores '_'(underline). a primeira parte antes do primeiro underline é a placa, que devemos considerar como o novo nome do veículo.
            partes_nome = unidade_nome.split('_')
            placa = partes_nome[0].strip() if partes_nome else ''
            restante_nome = ' '.join([parte.strip() for parte in partes_nome[1:]]) if len(partes_nome) > 1 else ''
    
            #checa se 'restante_nome' possui o valor 'Scania', se sim, define 'marca' como Scania
            if 'Scania' in restante_nome:
                marca = 'Scania'
            else:
                marca = 'Volvo'

            cls = 'Veículo'
            #retorna a instância da empresa correspondente
            empresa = Empresa.objects.filter(nome=empresa_nome).first()
            if not empresa:
                self.stdout.write(self.style.ERROR(f'Empresa {empresa_nome} não encontrada no banco de dados.'))
                return

            print(f'Unidade: {placa} | ID: {unidade_id} | Restante do nome: {restante_nome} | Marca: {marca} | Classe: {cls} | Empresa: {empresa.nome}')

            # Atualiza a unidade no banco de dados
            Unidade.objects.update_or_create(
                id=unidade_id,
                defaults={
                    'nm': unidade_nome,
                    'placa': placa,
                    'marca': marca,
                    'cls': cls,
                    'descricao': restante_nome if restante_nome else placa,
                    'empresa': empresa
                }
            )



    def process_units(self, sid):
        """Função para executar a coleta de dados de unidades por relatórios"""
        # Recupera as unidades do banco de dados
        unidades_db = Unidade.objects.all()
        unidades_db_ids = [unidade.id for unidade in unidades_db]
        print(f'Unidades no banco de dados:', colored(f'{len(unidades_db_ids)}', 'green'))

        # Separa as 10 primeiras unidades para teste
        unidades_db = unidades_db[:10]  # Aumentei para 10 para ver mais casos
        
        contador_sucesso = 0
        contador_erro = 0
        contador_sem_dados = 0
        
        # Lista para armazenar todos os DataFrames
        lista_dataframes = []

        # Coleta dados de relatório para 7 dias
        for unidade in unidades_db:
            unidade_id = unidade.id
            unidade_nome = unidade.nm
            
            self.stdout.write(f'🔄 Processando unidade: {unidade_nome} (ID: {unidade_id})')

            try:
                # Coleta dados de relatório para 7 dias
                resultado = Wialon.Colheitadeira_JSON(
                    sid, 
                    unidade_id, 
                    id_relatorio=59, 
                    tempo_dias=7, 
                    periodo='Ultimos 7 dias'
                )
                
                if resultado is not None and not resultado.empty:
                    contador_sucesso += 1
                    
                    # Adiciona informações da unidade ao DataFrame
                    resultado['unidade_nome'] = unidade_nome
                    resultado['unidade_placa'] = getattr(unidade, 'placa', 'N/A')
                    resultado['unidade_marca'] = getattr(unidade, 'marca', 'N/A')
                    resultado['unidade_empresa'] = unidade.empresa.nome if unidade.empresa else 'N/A'
                    
                    # Adiciona o DataFrame à lista
                    lista_dataframes.append(resultado)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Dados coletados para {unidade_nome}')
                    )
                    
                else:
                    contador_sem_dados += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Sem dados para {unidade_nome}')
                    )
                    
            except Exception as e:
                contador_erro += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao processar {unidade_nome}: {str(e)}')
                )
            
            # Limpa o resultado da memória do servidor
            Wialon.clean_up_result(sid)
            time.sleep(1)  # Pausa para evitar sobrecarga
        
        # Concatena todos os DataFrames
        if lista_dataframes:
            df_consolidado = pd.concat(lista_dataframes, ignore_index=True)
            self.gerar_estatisticas(df_consolidado)
            #self.salvar_dados_consolidados(df_consolidado)
        else:
            self.stdout.write(self.style.WARNING('⚠️ Nenhum dado foi coletado para análise.'))
        
        # Resumo final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'📊 RESUMO DO PROCESSAMENTO:')
        self.stdout.write(f'✅ Sucessos: {contador_sucesso}')
        self.stdout.write(f'⚠️ Sem dados: {contador_sem_dados}')
        self.stdout.write(f'❌ Erros: {contador_erro}')
        self.stdout.write(f'📱 Total processado: {contador_sucesso + contador_sem_dados + contador_erro}')
        self.stdout.write('='*50)

    def gerar_estatisticas(self, df):
        """
        Gera estatísticas detalhadas sobre os dados coletados
        """
        self.stdout.write('\n' + '='*60)
        self.stdout.write(colored('📊 ESTATÍSTICAS GERAIS', 'cyan', attrs=['bold']))
        self.stdout.write('='*60)
        
        # Informações básicas
        total_unidades = len(df)
        self.stdout.write(f'🚛 Total de unidades com dados: {colored(str(total_unidades), "green")}')
        
        # Processa quilometragem
        if 'Quilometragem' in df.columns:
            # Remove unidades de medida e converte para float
            df['km_numerico'] = pd.to_numeric(
                df['Quilometragem'].str.replace(' km', '').str.replace(',', '.'),
                errors='coerce'
            ).fillna(0)
            
            total_km = df['km_numerico'].sum()
            media_km = df['km_numerico'].mean()
            max_km = df['km_numerico'].max()
            min_km = df['km_numerico'].min()
            
            self.stdout.write(f'🛣️  QUILOMETRAGEM:')
            self.stdout.write(f'   Total: {colored(f"{total_km:,.2f} km", "yellow")}')
            self.stdout.write(f'   Média: {colored(f"{media_km:,.2f} km", "yellow")}')
            self.stdout.write(f'   Máxima: {colored(f"{max_km:,.2f} km", "green")}')
            self.stdout.write(f'   Mínima: {colored(f"{min_km:,.2f} km", "red")}')
        
        # Processa consumo de combustível
        if 'Consumido por AbsFCS' in df.columns:
            # Remove unidades e converte, tratando valores problemáticos
            df['combustivel_numerico'] = pd.to_numeric(
                df['Consumido por AbsFCS'].str.replace(' l', '').str.replace(',', '.').str.replace('-----', '0'),
                errors='coerce'
            ).fillna(0)
            
            total_combustivel = df['combustivel_numerico'].sum()
            media_combustivel = df['combustivel_numerico'].mean()
            
            # Verifica se há valores extremos (possíveis erros de dados)
            valores_validos = df[df['combustivel_numerico'] > 0]['combustivel_numerico']
            if len(valores_validos) > 0:
                max_combustivel = valores_validos.max()
                min_combustivel = valores_validos.min()
                
                # Se há valores muito altos (acima de 10.000L), considera como erro
                if max_combustivel > 10000:
                    self.stdout.write(f'⚠️  ATENÇÃO: Detectados valores de combustível extremos (máx: {max_combustivel:,.2f}L)')
                    # Filtra valores razoáveis para estatísticas mais precisas
                    valores_razoaveis = df[(df['combustivel_numerico'] > 0) & (df['combustivel_numerico'] <= 5000)]['combustivel_numerico']
                    if len(valores_razoaveis) > 0:
                        total_combustivel_filtrado = valores_razoaveis.sum()
                        media_combustivel_filtrado = valores_razoaveis.mean()
                        
                        self.stdout.write(f'⛽ COMBUSTÍVEL (valores filtrados até 5.000L):')
                        self.stdout.write(f'   Total consumido: {colored(f"{total_combustivel_filtrado:,.2f} litros", "green")}')
                        self.stdout.write(f'   Média por unidade: {colored(f"{media_combustivel_filtrado:,.2f} litros", "green")}')
                        
                        # Calcula eficiência com valores filtrados
                        if 'km_numerico' in df.columns:
                            df_filtrado = df[(df['combustivel_numerico'] > 0) & (df['combustivel_numerico'] <= 5000) & (df['km_numerico'] > 0)]
                            if len(df_filtrado) > 0:
                                df_filtrado['eficiencia_km_l'] = df_filtrado['km_numerico'] / df_filtrado['combustivel_numerico']
                                eficiencia_media = df_filtrado['eficiencia_km_l'].mean()
                                self.stdout.write(f'   Eficiência média: {colored(f"{eficiencia_media:.2f} km/l", "cyan")}')
                    else:
                        self.stdout.write(f'⛽ COMBUSTÍVEL: Todos os valores parecem estar fora do padrão')
                else:
                    # Valores normais
                    self.stdout.write(f'⛽ COMBUSTÍVEL:')
                    self.stdout.write(f'   Total consumido: {colored(f"{total_combustivel:,.2f} litros", "orange")}')
                    self.stdout.write(f'   Média por unidade: {colored(f"{media_combustivel:,.2f} litros", "orange")}')
                    
                    # Calcula eficiência se tiver ambos os dados
                    if 'km_numerico' in df.columns:
                        df_validos = df[(df['combustivel_numerico'] > 0) & (df['km_numerico'] > 0)]
                        if len(df_validos) > 0:
                            df_validos['eficiencia_km_l'] = df_validos['km_numerico'] / df_validos['combustivel_numerico']
                            eficiencia_media = df_validos['eficiencia_km_l'].mean()
                            self.stdout.write(f'   Eficiência média: {colored(f"{eficiencia_media:.2f} km/l", "cyan")}')
            else:
                self.stdout.write(f'⛽ COMBUSTÍVEL: Nenhum valor válido encontrado')
        
        # Processa velocidade média
        if 'Velocidade média' in df.columns:
            df['velocidade_numerica'] = pd.to_numeric(
                df['Velocidade média'].str.replace(' km/h', '').str.replace(',', '.').str.replace('-----', '0'),
                errors='coerce'
            ).fillna(0)
            
            velocidades_validas = df[df['velocidade_numerica'] > 0]['velocidade_numerica']
            if len(velocidades_validas) > 0:
                velocidade_media = velocidades_validas.mean()
                self.stdout.write(f'🏃 Velocidade média geral: {colored(f"{velocidade_media:.2f} km/h", "blue")}')
        
        # Processa horas de motor
        if 'Horas de motor' in df.columns:
            # Converte formato HH:MM:SS para horas decimais
            def converter_tempo_para_horas(tempo_str):
                try:
                    if tempo_str == '-----' or pd.isna(tempo_str):
                        return 0
                    partes = str(tempo_str).split(':')
                    horas = float(partes[0])
                    minutos = float(partes[1]) / 60 if len(partes) > 1 else 0
                    segundos = float(partes[2]) / 3600 if len(partes) > 2 else 0
                    return horas + minutos + segundos
                except:
                    return 0
            
            df['horas_motor_numerico'] = df['Horas de motor'].apply(converter_tempo_para_horas)
            total_horas = df['horas_motor_numerico'].sum()
            media_horas = df['horas_motor_numerico'].mean()
            
            self.stdout.write(f'⏰ HORAS DE MOTOR:')
            self.stdout.write(f'   Total: {colored(f"{total_horas:.2f} horas", "magenta")}')
            self.stdout.write(f'   Média: {colored(f"{media_horas:.2f} horas", "magenta")}')
        
        # Processa RPM médio
        if 'RPM médio do motor' in df.columns:
            df['rpm_numerico'] = pd.to_numeric(
                df['RPM médio do motor'].str.replace('-----', '0'),
                errors='coerce'
            ).fillna(0)
            
            rpms_validos = df[df['rpm_numerico'] > 0]['rpm_numerico']
            if len(rpms_validos) > 0:
                rpm_medio = rpms_validos.mean()
                self.stdout.write(f'🔧 RPM médio do motor: {colored(f"{rpm_medio:.0f} RPM", "cyan")}')
        
        # Processa temperatura média
        if 'Temperatura média' in df.columns:
            df['temp_numerica'] = pd.to_numeric(
                df['Temperatura média'].str.replace(' °C', '').str.replace(',', '.').str.replace('-----', '0'),
                errors='coerce'
            ).fillna(0)
            
            temps_validas = df[df['temp_numerica'] > 0]['temp_numerica']
            if len(temps_validas) > 0:
                temp_media = temps_validas.mean()
                self.stdout.write(f'🌡️  Temperatura média: {colored(f"{temp_media:.1f} °C", "red")}')
        
        # Estatísticas por empresa
        if 'unidade_empresa' in df.columns:
            self.stdout.write(f'\n📈 ESTATÍSTICAS POR EMPRESA:')
            
            for empresa in df['unidade_empresa'].unique():
                dados_empresa = df[df['unidade_empresa'] == empresa]
                self.stdout.write(f'   🏢 {empresa}:')
                self.stdout.write(f'      Unidades: {len(dados_empresa)}')
                if 'km_numerico' in df.columns:
                    self.stdout.write(f'      Total KM: {dados_empresa["km_numerico"].sum():,.2f}')
                if 'combustivel_numerico' in df.columns:
                    # Mostra combustível filtrado se necessário
                    combustivel_empresa = dados_empresa['combustivel_numerico'].sum()
                    if combustivel_empresa > 50000:  # Valor suspeito
                        combustivel_filtrado = dados_empresa[(dados_empresa['combustivel_numerico'] > 0) & 
                                                           (dados_empresa['combustivel_numerico'] <= 5000)]['combustivel_numerico'].sum()
                        self.stdout.write(f'      Total Combustível (filtrado): {combustivel_filtrado:,.2f}L')
                    else:
                        self.stdout.write(f'      Total Combustível: {combustivel_empresa:,.2f}L')
        
        # Top 5 unidades por quilometragem
        if 'km_numerico' in df.columns and 'unidade_nome' in df.columns:
            self.stdout.write(f'\n🏆 TOP 5 UNIDADES POR QUILOMETRAGEM:')
            top_km = df.nlargest(5, 'km_numerico')[['unidade_nome', 'unidade_placa', 'km_numerico', 'unidade_empresa']]
            
            for i, (idx, row) in enumerate(top_km.iterrows(), 1):
                self.stdout.write(f'   {i}. {row["unidade_nome"]} ({row["unidade_placa"]}) - {row["km_numerico"]:,.2f} km - {row["unidade_empresa"]}')
        
        # Processa emissões de CO2 com tratamento de valores inválidos
        if 'Emissões de CO2' in df.columns:
            # Trata valores problemáticos antes da conversão
            df['co2_str_limpo'] = df['Emissões de CO2'].str.replace(' t', '').str.replace(',', '.').str.replace('-----', '0')
            df['co2_numerico'] = pd.to_numeric(df['co2_str_limpo'], errors='coerce').fillna(0)
            
            total_co2 = df['co2_numerico'].sum()
            co2_validos = df[df['co2_numerico'] > 0]
            
            if len(co2_validos) > 0:
                self.stdout.write(f'🌍 Emissões de CO2:')
                self.stdout.write(f'   Total: {colored(f"{total_co2:.2f} toneladas", "red")}')
                self.stdout.write(f'   Unidades com dados válidos: {len(co2_validos)}/{len(df)}')
            else:
                self.stdout.write(f'🌍 Emissões de CO2: Nenhum dado válido encontrado')
        
        # Mostra algumas estatísticas de qualidade dos dados
        self.stdout.write(f'\n📋 QUALIDADE DOS DADOS:')
        for col in ['Quilometragem', 'Consumido por AbsFCS', 'Velocidade média', 'Emissões de CO2']:
            if col in df.columns:
                valores_com_traco = df[df[col].str.contains('-----', na=False)].shape[0]
                if valores_com_traco > 0:
                    self.stdout.write(f'   ⚠️  {col}: {valores_com_traco} valores sem dados (-----)')
        
        self.stdout.write('='*60)

    def salvar_dados_consolidados(self, df):
        """
        Salva o DataFrame consolidado em arquivo Excel
        """
        try:
            import os
            if not os.path.exists(deposito):
                os.makedirs(deposito)
            
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            arquivo_excel = os.path.join(deposito, f"relatorio_consolidado_{timestamp}.xlsx")
            
            # Cria um arquivo Excel com múltiplas abas
            with pd.ExcelWriter(arquivo_excel, engine='openpyxl') as writer:
                # Aba principal com todos os dados
                df.to_excel(writer, sheet_name='Dados_Completos', index=False)
                
                # Aba com resumo por empresa
                if 'unidade_empresa' in df.columns:
                    resumo_empresa = df.groupby('unidade_empresa').agg({
                        'unidade_nome': 'count',
                        'km_numerico': ['sum', 'mean'] if 'km_numerico' in df.columns else 'count',
                        'combustivel_numerico': ['sum', 'mean'] if 'combustivel_numerico' in df.columns else 'count'
                    }).round(2)
                    resumo_empresa.to_excel(writer, sheet_name='Resumo_por_Empresa')
                
                # Aba com ranking de unidades
                if 'km_numerico' in df.columns:
                    ranking = df.sort_values('km_numerico', ascending=False)[
                        ['unidade_nome', 'unidade_placa', 'km_numerico', 'combustivel_numerico', 'unidade_empresa']
                    ]
                    ranking.to_excel(writer, sheet_name='Ranking_Quilometragem', index=False)
            
            self.stdout.write(f'💾 Dados consolidados salvos em: {colored(arquivo_excel, "green")}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao salvar dados consolidados: {str(e)}'))

    def salvar_relatorio_no_banco(self, df_relatorio, unidade):
        """
        Método opcional para salvar os dados do relatório no banco de dados
        """
        try:
            # Aqui você pode criar uma model para salvar os dados de relatório
            # Por exemplo, criar uma model Relatorio_Unidade
            pass
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao salvar relatório no banco: {str(e)}')
            )
