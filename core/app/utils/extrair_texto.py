import fitz  # PyMuPDF
import pdfplumber
import os

class ExtratorCertificado:
    def __init__(self, caminho_pdf):
        self.caminho_pdf = caminho_pdf

    def _limpar_texto(self, texto):
        """
        Remove quebras de linha excessivas e espaços duplos para economizar 
        tokens e facilitar a vida do modelo local (Ollama).
        """
        if not texto:
            return ""
        # Substitui múltiplas quebras de linha por uma só e remove espaços extras
        linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
        return " ".join(linhas)

    def extrair_com_pymupdf(self):
        """Tentativa 1A: Extração super rápida usando PyMuPDF."""
        print("[*] Tentando extração com PyMuPDF...")
        texto_completo = ""
        try:
            # O PyMuPDF abre o arquivo através do módulo fitz
            doc = fitz.open(self.caminho_pdf)
            for pagina in doc:
                texto_completo += pagina.get_text()
            doc.close()
            return self._limpar_texto(texto_completo)
        except Exception as e:
            print(f"[!] Erro no PyMuPDF: {e}")
            return None

    def extrair_com_pdfplumber(self):
        """Tentativa 1B: Extração focada em layout usando pdfplumber."""
        print("[*] Tentando extração com pdfplumber...")
        texto_completo = ""
        try:
            with pdfplumber.open(self.caminho_pdf) as pdf:
                for pagina in pdf.pages:
                    # extract_text do pdfplumber tenta manter a ordem visual da leitura
                    texto_extraido = pagina.extract_text()
                    if texto_extraido:
                        texto_completo += texto_extraido + "\n"
            return self._limpar_texto(texto_completo)
        except Exception as e:
            print(f"[!] Erro no pdfplumber: {e}")
            return None

    def executar_pipeline(self):
        """
        Orquestra a tentativa de extração e decide se precisa do Fallback (Visão/OCR).
        """
        if not os.path.exists(self.caminho_pdf):
            return "Erro: Arquivo não encontrado."

        # 1. Tenta a extração mais leve primeiro
        texto = self.extrair_com_pymupdf()

        # Se o texto for muito curto, provavelmente é um PDF escaneado (imagem) 
        # ou tem uma codificação estranha.
        if not texto or len(texto) < 50:
            print("[!] PyMuPDF retornou pouco ou nenhum texto. Tentando pdfplumber...")
            texto = self.extrair_com_pdfplumber()

        # 2. Avalia se a Tentativa 1 (Texto) falhou completamente
        if not texto or len(texto) < 50:
            print("[!] Ambas as bibliotecas falharam. O PDF provavelmente é uma imagem.")
            print("[*] -> ACIONAR FALLBACK AQUI (Converter para imagem + LLM Vision ou OCR) <-")
            return None # Retorna None para sua view acionar o fallback

        print("[+] Extração de texto bem-sucedida!")
        return texto
