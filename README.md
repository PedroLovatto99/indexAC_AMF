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
docker-compose up --build
```
*(Pode demorar um pouco, pois por conta dos modelos do Llama o conteiner irá ficar pesado)*

### 3. Acessando a Aplicação
Quando o terminal exibir mensagens informando que o servidor do Django iniciou, você poderá acessar o sistema através do navegador no endereço:

**http://localhost:8000**
