import ollama
import json
import re
import os

def extrair_dados_com_ia_imagem(caminho_imagem):

    prompt_sistema = """
        Você é um sistema de extração de dados focado e direto para certificados acadêmicos, declarações e contratos de estágio.
        Analise o documento e extraia as informações estritamente para o formato JSON abaixo.
        
        REGRA MÁXIMA SOBRE DATAS:
        1. DATAS ALVO: 
        - Se for Certificado: procure a data próxima a "ocorrido no dia", "realizado em" ou "período de".
        - Se for Estágio: procure por "Data de Admissão" e "Afastamento", OU por frases textuais como "período de [data] a [data]".
        2. DATA DE EMISSÃO: Aparece isolada no final/rodapé. É ESTRITAMENTE PROIBIDO usar a data do rodapé como início ou fim do evento.

        REGRAS DE EXTRAÇÃO:
        - "tipo_documento": Escreva apenas "certificado", "monitoria" ou "estagio".
        - "papel": Se o texto disser "Comissão Organizadora", escreva "organizador". Caso contrário, escreva "participante". (Deixe vazio "" para estágio/monitoria).
        - "nome_alvo": Ignore completamente o topo do documento. Vá direto para o final da página, localize o número do CNPJ ou a assinatura. O nome que você deve extrair é EXATAMENTE a Razão Social que está escrita imediatamente ACIMA do CNPJ.
        - "horas": Extraia o número de horas se estiver explícito no texto. Se não mencionar, deixe vazio "". Converta minutos para horas.
        - "data_inicio": Data de início do evento ou estágio. Formato DD/MM/AAAA.
        - "data_fim": Data de término. Se ocorreu em apenas UM DIA, repita a data_inicio aqui.
        - "semestre": Se houver período letivo explícito (ex: 2024/2), coloque aqui. Senão, "".

        FORMATO EXATO DA RESPOSTA:
        {
            "tipo_documento": "",
            "papel": "",
            "nome_alvo": "",
            "horas": "",
            "data_inicio": "",
            "data_fim": "",
            "semestre": ""
        }
        """

    try:
        host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        client = ollama.Client(host=host)
        resposta = client.chat(
            model='minicpm-v',
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