from django.core.management.base import BaseCommand
from umbrella360.models import Unidade, Viagem_Base, CheckPoint, Infrações
from django.db import transaction
from collections import defaultdict

class Command(BaseCommand):
    help = 'Encontra unidades duplicadas e deleta aquelas com IDs de maior comprimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra quais unidades seriam deletadas, sem executar a deleção',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a deleção das unidades encontradas',
        )
        parser.add_argument(
            '--zeros-only',
            action='store_true',
            help='Procura apenas unidades com ID começando com quatro zeros (0000)',
        )

    def handle(self, *args, **options):
        if options['zeros_only']:
            self.processar_unidades_zeros(options)
        else:
            self.processar_unidades_duplicadas(options)

    def processar_unidades_zeros(self, options):
        """Processa unidades com ID começando com quatro zeros"""
        # Buscar unidades com ID começando com quatro zeros
        unidades_problematicas = Unidade.objects.filter(id__startswith='0000')
        
        if not unidades_problematicas.exists():
            self.stdout.write(
                self.style.SUCCESS("✅ Nenhuma unidade com ID começando com '0000' foi encontrada.")
            )
            return

        self.stdout.write(f"🔍 Encontradas {unidades_problematicas.count()} unidades com ID começando com '0000':")
        self.listar_unidades(unidades_problematicas)
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f"🔍 DRY RUN: {unidades_problematicas.count()} unidades seriam deletadas.\n"
                    "Use --confirm para executar a deleção real."
                )
            )
            return

        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  ATENÇÃO: {unidades_problematicas.count()} unidades serão DELETADAS permanentemente!\n"
                    "Use --confirm para confirmar a deleção ou --dry-run para apenas visualizar."
                )
            )
            return

        self.deletar_unidades(unidades_problematicas)

    def processar_unidades_duplicadas(self, options):
        """Processa unidades duplicadas baseado em critérios de similaridade"""
        self.stdout.write("🔍 Analisando unidades duplicadas...")
        
        # Agrupar unidades por critérios de duplicação
        grupos_duplicados = self.encontrar_duplicadas()
        
        if not grupos_duplicados:
            self.stdout.write(
                self.style.SUCCESS("✅ Nenhuma unidade duplicada encontrada.")
            )
            return

        # Identificar quais unidades devem ser deletadas (IDs mais longos)
        unidades_para_deletar = []
        
        self.stdout.write(f"🔍 Encontrados {len(grupos_duplicados)} grupos de unidades duplicadas:")
        self.stdout.write("=" * 80)
        
        for grupo_key, unidades in grupos_duplicados.items():
            if len(unidades) > 1:
                self.stdout.write(f"\n📋 Grupo: {grupo_key}")
                self.stdout.write("-" * 60)
                
                # Ordenar por comprimento do ID (menor primeiro)
                unidades_ordenadas = sorted(unidades, key=lambda u: len(u.id))
                
                # Manter a primeira (ID mais curto), deletar as outras
                unidade_manter = unidades_ordenadas[0]
                unidades_deletar = unidades_ordenadas[1:]
                
                self.stdout.write(f"✅ MANTER: ID={unidade_manter.id} (length={len(unidade_manter.id)})")
                self.stdout.write(f"   Nome: {unidade_manter.nm or 'N/A'}")
                self.stdout.write(f"   Empresa: {unidade_manter.empresa.nome if unidade_manter.empresa else 'N/A'}")
                
                for unidade in unidades_deletar:
                    self.stdout.write(f"❌ DELETAR: ID={unidade.id} (length={len(unidade.id)})")
                    self.stdout.write(f"   Nome: {unidade.nm or 'N/A'}")
                    self.stdout.write(f"   Empresa: {unidade.empresa.nome if unidade.empresa else 'N/A'}")
                    
                    # Contar dados relacionados
                    viagens_count = Viagem_Base.objects.filter(unidade=unidade).count()
                    checkpoints_count = CheckPoint.objects.filter(unidade=unidade).count()
                    infracoes_count = Infrações.objects.filter(unidade=unidade).count()
                    
                    self.stdout.write(f"   Dados: {viagens_count} viagens, {checkpoints_count} checkpoints, {infracoes_count} infrações")
                    unidades_para_deletar.append(unidade)

        if not unidades_para_deletar:
            self.stdout.write(
                self.style.SUCCESS("✅ Nenhuma unidade precisa ser deletada.")
            )
            return

        self.stdout.write("=" * 80)
        self.stdout.write(f"📊 RESUMO: {len(unidades_para_deletar)} unidades serão deletadas")

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f"🔍 DRY RUN: {len(unidades_para_deletar)} unidades duplicadas seriam deletadas.\n"
                    "Use --confirm para executar a deleção real."
                )
            )
            return

        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  ATENÇÃO: {len(unidades_para_deletar)} unidades duplicadas serão DELETADAS!\n"
                    "Use --confirm para confirmar a deleção ou --dry-run para apenas visualizar."
                )
            )
            return

        self.deletar_unidades(unidades_para_deletar)

    def encontrar_duplicadas(self):
        """Encontra unidades duplicadas baseado em nome, placa ou empresa+classe"""
        todas_unidades = Unidade.objects.all()
        grupos = defaultdict(list)
        
        for unidade in todas_unidades:
            # Criar chaves de agrupamento para identificar duplicatas
            chaves = []
            
            # Agrupar por nome (se não for vazio)
            if unidade.nm and unidade.nm.strip():
                chaves.append(('nome', unidade.nm.strip().lower()))
            
            # Agrupar por placa (se não for vazio)
            if unidade.placa and unidade.placa.strip():
                chaves.append(('placa', unidade.placa.strip().upper()))
            
            # Agrupar por empresa+classe (se ambos existirem)
            if unidade.empresa and unidade.cls:
                chaves.append(('empresa_classe', f"{unidade.empresa.nome}_{unidade.cls}"))
            
            # Adicionar unidade a todos os grupos relevantes
            for chave in chaves:
                grupos[chave].append(unidade)
        
        # Filtrar apenas grupos com mais de uma unidade
        grupos_duplicados = {k: v for k, v in grupos.items() if len(v) > 1}
        
        return grupos_duplicados

    def listar_unidades(self, unidades):
        """Lista detalhes das unidades"""
        self.stdout.write("-" * 80)
        
        for unidade in unidades:
            self.stdout.write(f"ID: {unidade.id} (length: {len(unidade.id)})")
            self.stdout.write(f"  Nome: {unidade.nm or 'N/A'}")
            self.stdout.write(f"  Empresa: {unidade.empresa.nome if unidade.empresa else 'N/A'}")
            self.stdout.write(f"  Classe: {unidade.cls or 'N/A'}")
            self.stdout.write(f"  Marca: {unidade.marca or 'N/A'}")
            self.stdout.write(f"  Placa: {unidade.placa or 'N/A'}")
            
            # Contar dados relacionados
            viagens_count = Viagem_Base.objects.filter(unidade=unidade).count()
            checkpoints_count = CheckPoint.objects.filter(unidade=unidade).count()
            infracoes_count = Infrações.objects.filter(unidade=unidade).count()
            
            self.stdout.write(f"  Viagens: {viagens_count}")
            self.stdout.write(f"  CheckPoints: {checkpoints_count}")
            self.stdout.write(f"  Infrações: {infracoes_count}")
            self.stdout.write("-" * 40)

    def deletar_unidades(self, unidades):
        """Deleta as unidades especificadas"""
        try:
            with transaction.atomic():
                # Contar dados relacionados antes da deleção
                total_viagens = 0
                total_checkpoints = 0
                total_infracoes = 0
                
                for unidade in unidades:
                    total_viagens += Viagem_Base.objects.filter(unidade=unidade).count()
                    total_checkpoints += CheckPoint.objects.filter(unidade=unidade).count()
                    total_infracoes += Infrações.objects.filter(unidade=unidade).count()

                # Deletar as unidades (cascade deletará dados relacionados)
                unidades_deletadas = len(unidades)
                
                # Se for um queryset, usar delete()
                if hasattr(unidades, 'delete'):
                    unidades.delete()
                else:
                    # Se for uma lista, deletar uma por uma
                    for unidade in unidades:
                        unidade.delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Deleção concluída com sucesso!\n"
                        f"Unidades deletadas: {unidades_deletadas}\n"
                        f"Viagens deletadas: {total_viagens}\n"
                        f"CheckPoints deletados: {total_checkpoints}\n"
                        f"Infrações deletadas: {total_infracoes}"
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Erro durante a deleção: {str(e)}\n"
                    "A operação foi revertida (rollback)."
                )
            )
            raise