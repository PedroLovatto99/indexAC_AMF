import ollama
import json
import re

def extrair_dados_com_ia_imagem(caminho_imagem):

    prompt_sistema = """
        Você é um sistema de extração de dados focado e direto para certificados acadêmicos e contratos de trabalho/estágio.
        Analise o documento e extraia as informações estritamente para o formato JSON abaixo.
        
        REGRA MÁXIMA SOBRE DATAS:
        1. DATAS ALVO: 
        - Se for Certificado: procure a data próxima a palavras como "ocorrido no dia", "realizado em" ou "período de".
        - Se for Estágio/Rescisão: procure explicitamente pelos campos "Data de Admissão" (para o início) e "Data de Afastamento" ou "Aviso Prévio" (para o fim).
        2. DATA DE EMISSÃO: Aparece isolada no final/rodapé (ex: "Restinga Seca, 23 de setembro") ou em logs do Clicksign. É ESTRITAMENTE PROIBIDO usar esta data.

        REGRAS DE EXTRAÇÃO:
        - "tipo_documento": Escreva apenas "certificado", "monitoria" ou "estagio".
        - "papel": Se o texto disser "Comissão Organizadora", escreva "organizador". Caso contrário, escreva "participante". (Deixe vazio "" para estágio/monitoria).
        - "nome_alvo": Extraia apenas o nome curto do evento, disciplina ou empresa (ex: "FOIL"). É PROIBIDO adicionar prefixos ou o nome da faculdade.
        - "horas": Apenas o número da carga horária. Se estiver em minutos, converta para horas (ex: 120 vira 2). Deixe vazio "" para estágio.
        - "data_inicio": Data de início do evento ou Data de Admissão. Formato DD/MM/AAAA. (Obrigatório converter meses por extenso para números, ex: "07 de novembro" vira "07/11").
        - "data_fim": Data de término do evento ou Data de Afastamento. Se o evento ocorreu em apenas UM DIA, repita exatamente a data_inicio aqui.
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