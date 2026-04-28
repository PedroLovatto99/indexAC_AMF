from django.shortcuts import render
import os
import fitz
import tempfile
from django.http import JsonResponse, FileResponse
from .utils.gerar_excel import gerar_excel_final
from .utils.ia_texto import extrair_dados_com_ia_texto
from .utils.ia_imagem import extrair_dados_com_ia_imagem
from .utils.extrair_texto import ExtratorCertificado
from .models import PerfilAluno, CertificadoSalvo
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages


def index(request):
    return render(request, "index.html")


def cadastro_aluno(request):
    if request.method == 'POST':
        nome = request.POST.get('nome_completo')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        curso = request.POST.get('curso')

        if User.objects.filter(username=email).exists():
            return render(request, 'cadastro.html', {'erro': 'Este email já está cadastrado.'})

        novo_usuario = User.objects.create_user(
            username=email, 
            email=email, 
            password=senha
        )

        PerfilAluno.objects.create(
            usuario=novo_usuario,
            nome_completo=nome,
            curso=curso
        )

        return redirect('login')
    
    return render(request, 'cadastro.html')

class Login(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True


@login_required
def dashboard_certificados(request):
    novos = CertificadoSalvo.objects.filter(dono=request.user, status='NOVO')

    verificados = CertificadoSalvo.objects.filter(
        dono=request.user, 
        status__in=['PROCESSADO', 'VALIDADO']
    )
    
    return render(request, 'dashboard.html', {
        'certificados_novos': novos,
        'certificados_validados': verificados
    })

@login_required
def upload_manual_certificado(request):
    if request.method == 'POST':
        arquivos = request.FILES.getlist('arquivos')
        
        if not arquivos:
            messages.error(request, "Nenhum arquivo foi selecionado.")
            return redirect('dashboard')

        for f in arquivos:
            CertificadoSalvo.objects.create(
                dono=request.user,
                arquivo=f,
                status='NOVO'
            )
            
        messages.success(request, f"{len(arquivos)} certificados adicionados com sucesso!")
        return redirect('dashboard')
    
    return redirect('dashboard')

@login_required
def mover_para_validado(request, cert_id):
    certificado = get_object_or_404(CertificadoSalvo, id=cert_id, dono=request.user)
    
    certificado.status = 'VALIDADO'
    certificado.save()
    
    return redirect('dashboard')


def extrair_certificado(request):
    return render(request, "extrair_certificado.html")


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
            print(f"\n--- Processando: {arquivo_pdf.name} ---")
            extrator = ExtratorCertificado(caminho_temporario)
            texto_cru = extrator.executar_pipeline()
            
            if texto_cru:
                dados_json = extrair_dados_com_ia_texto(texto_cru)
            else:
                print("[!] Sem texto. Acionando minicpm-v (Visão)...")
                doc = fitz.open(caminho_temporario)
                pagina = doc.load_page(0)
                pix = pagina.get_pixmap()
                
                caminho_imagem_temp = temp_pdf.name + ".png"
                pix.save(caminho_imagem_temp)
                doc.close()
                
                dados_json = extrair_dados_com_ia_imagem(caminho_imagem_temp)
                
            if dados_json:
                if request.user.is_authenticated:
                    CertificadoSalvo.objects.create(
                        dono=request.user,
                        arquivo=arquivo_pdf,
                        status='PROCESSADO'
                    )

                certificados_lidos = request.session.get('certificados', [])
                certificados_lidos.append(dados_json)
                request.session['certificados'] = certificados_lidos
                request.session.modified = True 
                
                print(f"[+] Sucesso! Já temos {len(certificados_lidos)} certificados na memória.")
                return JsonResponse({'status': 'sucesso', 'dados': dados_json})
            else:
                print(f"[-] A IA falhou ao extrair dados de {arquivo_pdf.name}")
                return JsonResponse({'erro': 'IA não conseguiu interpretar o arquivo.'}, status=500)

        finally:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
            if caminho_imagem_temp and os.path.exists(caminho_imagem_temp):
                os.remove(caminho_imagem_temp)
                
    return JsonResponse({'erro': 'Método inválido'}, status=405)


def gerar_planilha(request):
    if request.method == 'GET':
        nome = request.GET.get('nome', '')
        curso_cru = request.GET.get('curso', '')

        tradutor_cursos = {
        'ontopsicologia': 'Ontopsicologia',
        'administracao': 'Administração',
        'sistemas_informacao': 'Sistemas de Informação',
        'direito': 'Direito',
        'pedagogia': 'Pedagogia',
        'ciencias_contabeis': 'Ciências Contábeis',
        'hotelaria': 'Hotelaria',
        'gastronomia': 'Gastronomia',
    }


        curso_bonito = tradutor_cursos.get(curso_cru, curso_cru)
        
        dados_ia = request.session.get('certificados', [])
        
        if not dados_ia:
            return JsonResponse({'erro': 'Nenhum certificado foi processado.'}, status=400)

        caminho_excel_pronto = gerar_excel_final(dados_ia, nome, curso_bonito)
        
        request.session['certificados'] = []
        
        return FileResponse(
            open(caminho_excel_pronto, 'rb'), 
            as_attachment=True, 
            filename="Horas Complementares.xlsx"
        )
    
def limpar_sessao(request):
    if request.method == 'POST':
        request.session['certificados'] = [] 
        request.session.modified = True
        return JsonResponse({'status': 'sucesso', 'mensagem': 'Sessão limpa'})
    return JsonResponse({'erro': 'Método inválido'}, status=405)