from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="home"),
    path("/extrair", extrair_certificado, name="extracao_arquivo"),
    path('processar-arquivo/', processar_arquivo, name='processar_arquivo'),
    path('gerar-planilha/', gerar_planilha, name='gerar_planilha'),
    path('limpar-sessao/', limpar_sessao, name='limpar_sessao'),
]
