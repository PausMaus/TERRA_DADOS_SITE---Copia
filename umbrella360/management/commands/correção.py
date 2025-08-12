from django.core.management.base import BaseCommand
from umbrella360.models import Unidade, Viagem_Base, CheckPoint, Infrações
from django.db import transaction

class Command(BaseCommand):
    help = 'Encontra e deleta unidades com ID começando com quatro zeros (0000)'

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

    def handle(self, *args, **options):
        # Buscar unidades com ID começando com quatro zeros
        unidades_problematicas = Unidade.objects.filter(id__startswith='0000')
        
        if not unidades_problematicas.exists():
            self.stdout.write(
                self.style.SUCCESS("✅ Nenhuma unidade com ID começando com '0000' foi encontrada.")
            )
            return

        self.stdout.write(f"🔍 Encontradas {unidades_problematicas.count()} unidades com ID começando com '0000':")
        self.stdout.write("-" * 80)
        
        # Listar unidades encontradas
        for unidade in unidades_problematicas:
            self.stdout.write(f"ID: {unidade.id}")
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

        # Se for dry-run, apenas mostrar o que seria deletado
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f"🔍 DRY RUN: {unidades_problematicas.count()} unidades seriam deletadas.\n"
                    "Use --confirm para executar a deleção real."
                )
            )
            return

        # Se não tiver confirmação, pedir confirmação
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  ATENÇÃO: {unidades_problematicas.count()} unidades serão DELETADAS permanentemente!\n"
                    "Isso também deletará todos os dados relacionados (viagens, checkpoints, infrações).\n"
                    "Use --confirm para confirmar a deleção ou --dry-run para apenas visualizar."
                )
            )
            return

        # Executar deleção com transaction para garantir consistência
        try:
            with transaction.atomic():
                # Contar dados relacionados antes da deleção
                total_viagens = 0
                total_checkpoints = 0
                total_infracoes = 0
                
                for unidade in unidades_problematicas:
                    total_viagens += Viagem_Base.objects.filter(unidade=unidade).count()
                    total_checkpoints += CheckPoint.objects.filter(unidade=unidade).count()
                    total_infracoes += Infrações.objects.filter(unidade=unidade).count()

                # Deletar as unidades (cascade deletará dados relacionados)
                unidades_deletadas = unidades_problematicas.count()
                unidades_problematicas.delete()

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

        # Verificar se ainda existem unidades problemáticas
        restantes = Unidade.objects.filter(id__startswith='0000').count()
        if restantes > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Ainda existem {restantes} unidades com ID começando com '0000'")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ Todas as unidades com ID problemático foram removidas.")
            )