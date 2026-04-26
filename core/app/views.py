from django.shortcuts import render
import os
import tempfile
from django.http import JsonResponse, FileResponse
from .utils.gerar_excel import gerar_excel_final
from .utils.ia_config import extrair_dados_com_ia
from .utils.extrair_texto import ExtratorCertificado


def index(request):
    return render(request, "index.html")

def processar_arquivo(request):
    """Recebe UM certificado, extrai o texto, passa na IA e salva o JSON na sessão."""
    if request.method == 'POST':
        arquivo_pdf = request.FILES.get('certificado')
        
        if not arquivo_pdf:
            return JsonResponse({'erro': 'Nenhum arquivo enviado'}, status=400)

        # 1. Salva o PDF temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            for chunk in arquivo_pdf.chunks():
                temp_pdf.write(chunk)
            caminho_temporario = temp_pdf.name

        try:
            # 2. Extrai o texto real do PDF
            extrator = ExtratorCertificado(caminho_temporario)
            texto_cru = extrator.executar_pipeline()
            
            # Se a extração falhou (ex: PDF é uma imagem e o fallback ainda não existe)
            if not texto_cru:
                return JsonResponse({'erro': 'Não foi possível ler o texto deste PDF (provavelmente é uma imagem scaneada).'}, status=422)

            # 3. Envia o texto real para o Ollama
            dados_json = extrair_dados_com_ia(texto_cru)

            if dados_json:
                # 4. Salva o resultado na sessão
                certificados_lidos = request.session.get('certificados', [])
                certificados_lidos.append(dados_json)
                request.session['certificados'] = certificados_lidos
                request.session.modified = True 
                
                # Devolve o sucesso para o JavaScript avançar a barrinha
                return JsonResponse({'status': 'sucesso', 'dados': dados_json})
            else:
                return JsonResponse({'erro': 'A IA não conseguiu interpretar este certificado.'}, status=500)

        finally:
            # 5. Limpeza do HD
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
                
    return JsonResponse({'erro': 'Método inválido'}, status=405)

def gerar_planilha(request):
    if request.method == 'GET':
        nome_aluno = request.GET.get('nome', 'Aluno')
        curso_aluno = request.GET.get('curso', 'Curso Não Informado')
        
        dados_ia = request.session.get('certificados', [])
        
        if not dados_ia:
            return JsonResponse({'erro': 'Nenhum certificado foi processado.'}, status=400)

        caminho_excel_pronto = gerar_excel_final(dados_ia, nome_aluno, curso_aluno)
        
        request.session['certificados'] = []
        
        return FileResponse(
            open(caminho_excel_pronto, 'rb'), 
            as_attachment=True, 
            filename="Horas Complementares.xlsx"
        )