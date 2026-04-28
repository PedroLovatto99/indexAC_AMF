from django.db import models
from django.contrib.auth.models import User


class PerfilAluno(models.Model):

    CURSOS = [
        ('ontopsicologia', 'Ontopsicologia'),
        ('administracao', 'Administração'),
        ('sistemas_informacao', 'Sistemas de Informação'),
        ('direito', 'Direito'),
        ('pedagogia', 'Pedagogia'),
        ('ciencias_contabeis', 'Ciências Contábeis'),
        ('hotelaria', 'Hotelaria'),
        ('gastronomia', 'Gastronomia'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    nome_completo = models.CharField(max_length=255)

    curso = models.CharField(max_length=150, choices=CURSOS)
    

    def __str__(self):
        return self.nome_completo


class CertificadoSalvo(models.Model):
    STATUS_CHOICES = [
        ('NOVO', 'Novo (Aguardando Processamento)'),
        ('PROCESSADO', 'Processado (Enviado à Coordenadoria)'),
        ('VALIDADO', 'Validado (Finalizado)'),
    ]

    dono = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arquivos_salvos')
    
    arquivo = models.FileField(upload_to='certificados/%Y/%m/') 
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOVO')
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Arquivo {self.id} - {self.dono.username}"