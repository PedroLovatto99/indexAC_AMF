from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="teste"),
    path('processar-arquivo/', processar_arquivo, name='processar_arquivo'),
    
    # A rota final que o JS chama para baixar o Excel
    path('gerar-planilha/', gerar_planilha, name='gerar_planilha'),
]
