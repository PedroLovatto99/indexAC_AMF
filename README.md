# IndexAC AMF - Sistema de Atividades Complementares com Inteligência Artificial

IndexAC AMF é uma plataforma desenvolvida para facilitar a vida do acadêmico da Antonio Meneghetti Faculdade, possibilitando a gestão de certificados de atividades complementares e a extração de informações desses certificados com inteligência artificial e adicionando-as em uma planilha de forma totalmente automatizada.

## ✨ Funcionalidades Principais

- **Guia de Atividades Complementares:** Interface interativa para os alunos se informarem sobre os requisitos e atividades aceitas.
- **Integração com IA Local (Ollama):** Uso de modelos avançados de texto e visão para analisar informações acadêmicas.
- **Banco de Dados Relacional:** Utiliza o PostgreSQL para garantir a integridade dos dados acadêmicos e do sistema de autenticação.
- **Ambiente 100% Conteinerizado:** Tudo (Django, PostgreSQL e Ollama) roda através do Docker Compose, sem precisar instalar dependências de sistema (além do próprio Docker).
- **Setup Automatizado de IA:** O ambiente já baixa e prepara os modelos necessários automaticamente na primeira inicialização.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python e Django 
- **Banco de Dados:** PostgreSQL
- **Inteligência Artificial:** Ollama (modelo LLaMA 3.1 e modelo MiniCPM-V)
- **Infraestrutura:** Docker
- **Interface:** HTML, CSS, JavaScript (Templates Django)

---

## 🧠 Arquitetura e Processamento de IA

O sistema utiliza um pipeline inteligente para garantir a extração precisa de dados dos certificados, lidando tanto com PDFs em formato de texto nativo quanto com PDFs baseados em imagens escaneadas. O fluxo de análise funciona da seguinte forma:

1. **Extração de Texto (Fluxo Principal):**
   - Inicialmente, o sistema tenta extrair o conteúdo textual do arquivo PDF utilizando as bibliotecas Python **PyMuPDF** e **pdfplumber**.
   - Se a extração for bem-sucedida, esse texto é enviado para o modelo **LLaMA 3.1** (executado via Ollama).
   - O modelo LLaMA 3.1 é o encarregado de interpretar o texto bruto extraído, organizando e identificando as informações exigidas do certificado (como nome do participante, carga horária, tema, etc.).

2. **Processamento Visual (Fallback de Segurança):**
   - Caso as bibliotecas não consigam extrair o texto (cenário comum quando o certificado é uma imagem escaneada ou um PDF sem camada de texto), o sistema ativa seu processo de *fallback*.
   - O documento PDF é convertido em uma imagem.
   - Em seguida, o modelo **MiniCPM-V** (modelo de visão computacional, também via Ollama) é acionado. Ele processa a imagem do certificado como uma foto e utiliza OCR avançado para extrair as informações de forma visual, garantindo a completude dos dados sem falhas para o usuário.

---

## 🚀 Como Iniciar o Projeto (Passo a Passo)

### 1. Pré-requisitos
Antes de começar, certifique-se de que sua máquina atende aos seguintes requisitos:
- [Docker](https://docs.docker.com/get-docker/) instalado.

### 2. Executando o Projeto

**2.1 Clone o repositório**
```bash
git clone https://github.com/PedroLovatto99/indexAC_AMF
``` 

**2.2 Entre na pasta**
```bash
cd indexAC_AMF/core
``` 

**2.3 Execute o comando:**

```bash
docker-compose up --build -d
```
*(Pode demorar um pouco, pois por conta dos modelos do Llama o conteiner irá ficar pesado)*

### 3. Acessando a Aplicação
Quando o terminal exibir mensagens informando que o servidor do Django iniciou, você poderá acessar o sistema através do navegador no endereço:

**http://localhost:8000**
