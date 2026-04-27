import ollama
import json
import re

def extrair_dados_com_ia_imagem(caminho_imagem):

    prompt_sistema = """
    Você é um sistema de extração de dados focado e direto.
    Analise o documento e extraia as informações estritamente para o JSON abaixo.
    IGNORE completamente logs de assinatura (Clicksign, DocuSign) e datas de emissão do documento.

    REGRAS DE EXTRAÇÃO:
    - "tipo_documento": Avalie o texto e escreva apenas "certificado", "monitoria" ou "estagio".
    - "nome_alvo": 
      * Se certificado, o nome do evento. 
      * Se monitoria, o nome da disciplina. 
      * Se estagio/rescisão, procure por "Razão Social" ou "Empregador" e extraia apenas o nome da empresa.
       * Se estagio/rescisão, extraia APENAS o nome curto da empresa (geralmente 1 a 3 palavras, ex: "FOIL"). É ESTRITAMENTE PROIBIDO incluir textos legais, frases de aviso, endereços ou jargões de contrato (ex: ignore frases como "A assistência no ato...").
    - "horas": Apenas o número da carga horária. Deixe vazio "" se for estágio.
    - "data_inicio": Data de início do evento ou Data de Admissão. Formato DD/MM/AAAA. É PROIBIDO usar a data de emissão/assinatura do documento (ex: "Restinga Seca, 10 de Fevereiro de 2026" ou similares na parte inferior do documento devem ser ignorados).
    - "data_fim": Data de término do evento ou Data de Afastamento/Demissão. Formato DD/MM/AAAA. (Se ocorreu em um único dia, repita a data inicial). - É PROIBIDO usar a data de emissão/assinatura do documento (ex: "Restinga Seca, 10 de Fevereiro de 2026" ou similares na parte inferior do documento devem ser ignorados).
    - "semestre": Se houver período letivo explícito (ex: 2024/2), coloque aqui. Senão, "".

    FORMATO EXATO DA RESPOSTA:
    {
        "tipo_documento": "",
        "nome_alvo": "",
        "horas": "",
        "data_inicio": "",
        "data_fim": "",
        "semestre": ""
    }
    """

    try:
        resposta = ollama.chat(
            model='llava',
            messages=[
                {
                    'role': 'user',
                    'content': prompt_sistema,
                    'images': [caminho_imagem]
                }
            ],
            options={'temperature': 0.0} 
        )

        resultado = resposta['message']['content'].strip()

        print("\n--- JSON CRU DA IA (VISÃO) ---")
        print(resultado)
        print("------------------------------\n")

        match = re.search(r'\{.*\}', resultado, re.DOTALL)
        
        if match:
            dados_brutos = json.loads(match.group(0))
            
            evento_final = ""
            data_final = ""
            
            tipo = dados_brutos.get('tipo_documento', '').lower()
            nome = dados_brutos.get('nome_alvo', '')
            inicio = dados_brutos.get('data_inicio', '')
            fim = dados_brutos.get('data_fim', '')
            semestre = dados_brutos.get('semestre', '')
            horas = dados_brutos.get('horas', '')

            categorias_estagio = ['estagio', 'estágio', 'rescisao', 'rescisão', 'contrato', 'trabalho']
            
            if tipo in categorias_estagio:
                evento_final = f"Estágio na {nome}" if nome else "Contrato de Estágio"
            elif tipo == 'monitoria':
                evento_final = f"Monitoria em {nome}" if nome else "Monitoria"
            else:
                evento_final = nome

            if semestre:
                data_final = semestre
            elif inicio and fim and inicio != fim:
                data_final = f"{inicio} até {fim}"
            elif inicio:
                data_final = inicio
            elif fim:
                data_final = fim

            return {
                'evento': evento_final,
                'horas': horas,
                'data': data_final
            }
            
        else:
            print("[!] Erro: Nenhum bloco JSON encontrado pelo LLaVA.")
            return None

    except json.JSONDecodeError:
        print("[!] Erro: Formato JSON inválido no LLaVA.")
        return None
    except Exception as e:
        print(f"[!] Erro de comunicação com o LLaVA: {e}")
        return None