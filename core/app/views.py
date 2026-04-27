from django.shortcuts import render
import os
import tempfile
from django.http import JsonResponse, FileResponse
from .utils.gerar_excel import gerar_excel_final
from .utils.ia_texto import extrair_dados_com_ia_texto
from .utils.extrair_texto import ExtratorCertificado
import fitz


def index(request):
    return render(request, "index.html")

def processar_arquivo(request):
    if request.method == 'POST':
        arquivo_pdf = request.FILES.get('certificado')
        
        if not arquivo_pdf:
            return JsonResponse({'erro': 'Nenhum arquivo enviado'}, status=400)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            for chunk in arquivo_pdf.chunks():
                temp_pdf.write(chunk)
            caminho_temporario = temp_pdf.name

        caminho_imagem_temp = None
        dados_json = None

        try:
            extrator = ExtratorCertificado(caminho_temporario)
            texto_cru = extrator.executar_pipeline()
            
            if texto_cru:
                dados_json = extrair_dados_com_ia_texto(texto_cru)
                
            else:
                doc = fitz.open(caminho_temporario)
                pagina = doc.load_page(0)
                pix = pagina.get_pixmap(dpi=150)
                
                caminho_imagem_temp = caminho_temporario.replace(".pdf", ".png")
                pix.save(caminho_imagem_temp)
                doc.close()

                dados_json = extrair_dados_com_ia_texto(caminho_imagem_temp)

            if dados_json:
                certificados_lidos = request.session.get('certificados', [])
                certificados_lidos.append(dados_json)
                request.session['certificados'] = certificados_lidos
                request.session.modified = True 
                
                return JsonResponse({'status': 'sucesso', 'dados': dados_json})
            else:
                return JsonResponse({'erro': 'Nenhuma das IAs conseguiu interpretar o arquivo.'}, status=500)

        finally:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
            if caminho_imagem_temp and os.path.exists(caminho_imagem_temp):
                os.remove(caminho_imagem_temp)
                
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