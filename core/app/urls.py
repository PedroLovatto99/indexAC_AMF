from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", index, name="home"),
    path("/extrair", extrair_certificado, name="extracao_arquivo"),
    path('processar-arquivo/', processar_arquivo, name='processar_arquivo'),
    path('gerar-planilha/', gerar_planilha, name='gerar_planilha'),
    path('limpar-sessao/', limpar_sessao, name='limpar_sessao'),
    path('cadastro/', cadastro_aluno, name='cadastro'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('meus-certificados/', dashboard_certificados, name='dashboard'),
]
