from django.core.management.base import BaseCommand
from lab_01.models import Usuario

class Command(BaseCommand):
    help = 'Cria um novo usuário do Laboratorium'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nome de usuário')
        parser.add_argument('email', type=str, help='Email do usuário')
        parser.add_argument('senha', type=str, help='Senha do usuário')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        senha = kwargs['senha']
        
        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'Usuário "{username}" já existe!'))
            return
        
        usuario = Usuario(username=username, email=email)
        usuario.set_senha(senha)
        usuario.save()
        
        self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" criado com sucesso!'))
