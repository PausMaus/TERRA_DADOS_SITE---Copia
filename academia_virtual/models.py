from django.db import models

# Create your models here.
#modelo basico para itens de academia virtual, tanto equipamentos quanto treinos e professores.
class ItemAcademia(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Item")
    descricao = models.TextField(verbose_name="Descrição do Item", blank=True, null=True)
    imagem = models.ImageField(upload_to='academia_virtual/', verbose_name="Imagem do Item", blank=True, null=True)


    class Meta:
        verbose_name = "Item de Academia"
        verbose_name_plural = "Itens de Academia"
        ordering = ['nome']

    def __str__(self):
        return self.nome