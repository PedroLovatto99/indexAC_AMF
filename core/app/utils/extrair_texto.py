import fitz 
import pdfplumber
import os
from .ia_imagem import extrair_dados_com_ia_imagem

class ExtratorCertificado:
    def __init__(self, caminho_pdf):
        self.caminho_pdf = caminho_pdf

    def _limpar_texto(self, texto):
        if not texto:
            return ""
        linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
        return " ".join(linhas)

    def extrair_com_pymupdf(self):
        print("[*] Tentando extração com PyMuPDF...")
        texto_completo = ""
        try:
            doc = fitz.open(self.caminho_pdf)
            for pagina in doc:
                texto_completo += pagina.get_text()
            doc.close()
            return self._limpar_texto(texto_completo)
        except Exception as e:
            print(f"[!] Erro no PyMuPDF: {e}")
            return None

    def extrair_com_pdfplumber(self):
        print("[*] Tentando extração com pdfplumber...")
        texto_completo = ""
        try:
            with pdfplumber.open(self.caminho_pdf) as pdf:
                for pagina in pdf.pages:
                    texto_extraido = pagina.extract_text()
                    if texto_extraido:
                        texto_completo += texto_extraido + "\n"
            return self._limpar_texto(texto_completo)
        except Exception as e:
            print(f"[!] Erro no pdfplumber: {e}")
            return None

    def executar_pipeline(self):
            if not os.path.exists(self.caminho_pdf):
                return None

            texto = self.extrair_com_pymupdf()

            if not texto or len(texto) < 50:
                texto = self.extrair_com_pdfplumber()

            if not texto or len(texto) < 50:
                return None 

            return texto
