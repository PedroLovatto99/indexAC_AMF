import ollama
import json
import re

def extrair_dados_com_ia_texto(texto_pdf):
    
    prompt_sistema = """
        Você é um sistema de extração de dados focado e direto para certificados acadêmicos.
        Analise o documento e extraia as informações estritamente para o formato JSON abaixo.
        
        REGRA MÁXIMA SOBRE DATAS: Datas no final do documento acompanhadas do nome da cidade (ex: "Restinga Seca, 23 de setembro de 2025") são as DATAS DE EMISSÃO. É ESTRITAMENTE PROIBIDO colocar essa data em qualquer campo do JSON.

        REGRAS DE EXTRAÇÃO:
        - "tipo_documento": Escreva apenas "certificado", "monitoria" ou "estagio".
        - "papel": Se o texto disser expressamente "Comissão Organizadora", escreva "organizador". Caso contrário, escreva "participante". (Deixe vazio "" para estágio/monitoria).
        - "nome_alvo": Extraia apenas o nome curto do evento, disciplina ou empresa. É PROIBIDO adicionar prefixos como "Comissão" ou o nome da faculdade.
        - "horas": Apenas o número da carga horária. Se estiver em minutos, converta para horas (ex: 120 vira 2). Deixe "" para estágio.
        - "data_inicio": A data exata em que o EVENTO começou. Formato DD/MM/AAAA.
        - "data_fim": A data em que o EVENTO terminou. Se o evento ocorreu em apenas UM DIA, repita exatamente o mesmo valor da data_inicio aqui. JAMAIS use a data da cidade para preencher este campo.
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
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': prompt_sistema},
                {'role': 'user', 'content': texto_pdf}
            ],
            options={'temperature': 0.0} 
        )

        resultado = resposta['message']['content'].strip()
        match = re.search(r'\{.*\}', resultado, re.DOTALL)
        
        if match:
            dados_brutos = json.loads(match.group(0))
            
            # 1. Captura de variáveis brutas
            tipo = dados_brutos.get('tipo_documento', '').lower()
            papel = dados_brutos.get('papel', '').lower()
            nome = dados_brutos.get('nome_alvo', '')
            inicio = dados_brutos.get('data_inicio', '')
            fim = dados_brutos.get('data_fim', '')
            semestre = dados_brutos.get('semestre', '')
            horas = dados_brutos.get('horas', '')

            evento_final = ""
            data_final = ""

            # 2. Montagem Inteligente do Nome (Lógica Python)
            categorias_estagio = ['estagio', 'estágio', 'rescisao', 'rescisão', 'contrato', 'trabalho']

            if tipo in categorias_estagio:
                evento_final = f"Estágio na {nome}" if nome else "Contrato de Estágio"
            elif tipo == 'monitoria':
                evento_final = f"Monitoria em {nome}" if nome else "Monitoria"
            else:
                # Trata a diferenciação de Comissão Organizadora
                if papel == 'organizador':
                    evento_final = f"Comissão Organizadora do(a) {nome}"
                else:
                    evento_final = nome

            # 3. Montagem da Data
            if semestre:
                data_final = semestre
            elif inicio and fim and inicio != fim:
                data_final = f"{inicio} até {fim}" 
            elif inicio:
                data_final = inicio
            elif fim:
                data_final = fim

            # Retorno limpo para a View e a Planilha
            return {
                'evento': evento_final,
                'horas': horas,
                'data': data_final
            }
            
        return None

    except Exception as e:
        print(f"[!] Erro no processamento Python/IA: {e}")
        return None