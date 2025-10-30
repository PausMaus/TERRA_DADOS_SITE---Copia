from django.db import models

# Create your models here.
#model para regiões geográficas
class Regiao(models.Model):
    nome = models.CharField(max_length=100, unique=True, blank=False, null=False)
    sigla = models.CharField(max_length=2, blank=True, null=True)
    populacao = models.IntegerField(blank=True, null=True)
    area = models.FloatField(blank=True, null=True)


#model para dados google trends
class GoogleTrendsData(models.Model):
    termo = models.CharField(max_length=200, blank=False, null=False)
    data_inicial = models.DateField(blank=False, null=False)
    data_final = models.DateField(blank=False, null=False)
    interesse = models.IntegerField(blank=True, null=True)
    regiao = models.ForeignKey(Regiao, on_delete=models.CASCADE, related_name='google_trends_data')
    termos_comparados = models.TextField(blank=True, null=True)  # Armazena termos relacionados como texto simples


class Usuario(models.Model):
    username = models.CharField(max_length=150, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    senha = models.CharField(max_length=128, blank=False, null=False)
    
    def __str__(self):
        return self.username
    
    def verificar_senha(self, senha_texto):
        """Verifica se a senha fornecida está correta"""
        from django.contrib.auth.hashers import check_password
        return check_password(senha_texto, self.senha)
    
    def set_senha(self, senha_texto):
        """Define a senha do usuário (hash)"""
        from django.contrib.auth.hashers import make_password
        self.senha = make_password(senha_texto)


class YouTubeData(models.Model):
    termo = models.CharField(max_length=200, blank=False, null=False)
    data_inicial = models.DateField(blank=False, null=False)
    data_final = models.DateField(blank=False, null=False)
    total_videos = models.IntegerField(default=0)
    data_consulta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['termo', 'data_inicial', 'data_final']