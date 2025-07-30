from django.db import models

# Create your models here.
#modelo basico para itens de academia virtual, tanto equipamentos quanto treinos e professores.
class Area(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Área")
    descricao = models.TextField(verbose_name="Descrição da Área", blank=True, null=True)
    imagem = models.ImageField(upload_to='academia_virtual/', verbose_name="Imagem da Área", blank=True, null=True)

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class ItemAcademia(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Item")
    descricao = models.TextField(verbose_name="Descrição do Item", blank=True, null=True)
    imagem = models.ImageField(upload_to='academia_virtual/', verbose_name="Imagem do Item", blank=True, null=True)


    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ['nome']

    def __str__(self):
        return self.nome
    

class Equipamento(ItemAcademia):
    tipo = models.CharField(max_length=50, verbose_name="Tipo de Equipamento", blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name="Área Associada", blank=True, null=True)

    class Meta:
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"

    def __str__(self):
        return f"{self.nome} ({self.tipo})"
    
class Professor(ItemAcademia):
    especialidade = models.CharField(max_length=100, verbose_name="Especialidade do Professor", blank=True, null=True)

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"

    def __str__(self):
        return f"{self.nome} - {self.especialidade}" if self.especialidade else self.nome


class Exercicio(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Exercício")
    descricao = models.TextField(verbose_name="Descrição do Exercício", blank=True, null=True)
    imagem = models.ImageField(upload_to='academia_virtual/exercicios/', verbose_name="Imagem do Exercício", blank=True, null=True)
    duracao = models.IntegerField(verbose_name="Duração do Exercício (em minutos)", blank=True, null=True)
    repeticoes = models.IntegerField(verbose_name="Número de Repetições", blank=True, null=True)
    series = models.IntegerField(verbose_name="Número de Séries", blank=True, null=True)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, verbose_name="Equipamento Associado", blank=True, null=True)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, verbose_name="Professor Associado", blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name="Área Associada", blank=True, null=True)
    dificuldade = models.CharField(max_length=50, verbose_name="Dificuldade do Exercício", blank=True, null=True)

    class Meta:
        verbose_name = "Exercício"
        verbose_name_plural = "Exercícios"

    def __str__(self):
        return f"{self.nome} ({self.dificuldade})" if self.dificuldade else self.nome
    

class Treino(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Treino")
    descricao = models.TextField(verbose_name="Descrição do Treino", blank=True, null=True)
    exercicios = models.ManyToManyField(Exercicio, verbose_name="Exercícios do Treino", blank=True)
    dificuldade = models.CharField(max_length=50, verbose_name="Dificuldade do Treino", blank=True, null=True)

    class Meta:
        verbose_name = "Treino"
        verbose_name_plural = "Treinos"

    def __str__(self):
        return self.nome
