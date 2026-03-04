# Sentinela

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-Academic-lightgrey)
![Purpose](https://img.shields.io/badge/purpose-academic%20research-blueviolet)

---

## Visão Geral

O **Sentinela** é um projeto acadêmico destinado ao estudo e à experimentação de técnicas de **Processamento de Linguagem Natural (Natural Language Processing – NLP)** e **Inteligência Artificial aplicada à análise de textos clínicos**.

O sistema tem como objetivo analisar textos estruturados provenientes de **prontuários eletrônicos simulados** e identificar **possíveis indicativos linguísticos associados a situações de violência**, a partir de métodos computacionais.

A proposta do projeto é construir um ambiente experimental que permita avaliar abordagens baseadas em:

- **Regras linguísticas**
- **Análise estatística de texto**
- **Modelos de aprendizado de máquina**
- **Modelos de linguagem**

O sistema **não tem finalidade diagnóstica ou clínica**, sendo desenvolvido exclusivamente como **instrumento de pesquisa e aprendizado**.

---

## Objetivo do Projeto

### Objetivo Geral

Desenvolver um protótipo computacional capaz de analisar registros textuais estruturados de prontuários eletrônicos e identificar **padrões linguísticos potencialmente associados a indicadores de violência**.

### Objetivos Específicos

- Construir um pipeline de processamento textual aplicado a registros clínicos.
- Estruturar mecanismos de **detecção baseada em padrões e regras linguísticas**.
- Explorar o uso de **modelos de linguagem natural e aprendizado supervisionado**.
- Desenvolver uma arquitetura modular que permita evolução incremental do sistema.
- Criar um ambiente experimental para estudos em **IA aplicada à saúde digital**.

---

## Finalidade Acadêmica

Este projeto é desenvolvido **exclusivamente para fins acadêmicos e educacionais**.

O sistema:

- **não substitui avaliação profissional**
- **não deve ser utilizado em ambientes clínicos reais**
- **não possui validação clínica**
- **não deve ser utilizado para tomada de decisões médicas, jurídicas ou institucionais**

Todos os dados utilizados no desenvolvimento devem ser **anonimizados ou simulados**, evitando qualquer utilização de dados pessoais identificáveis.

---

## Arquitetura do Projeto

O sistema está organizado em duas camadas principais:


sentinela/
│
├── frontend/ # Interface de coleta de prontuário
│
└── backend/ # API e pipeline de análise textual


---

### Frontend

Responsável pela interface de entrada de dados.

Funções principais:

- coleta estruturada de dados do prontuário
- organização das informações em formato JSON
- envio das informações para a API de análise

Tecnologias utilizadas:

- HTML
- CSS
- JavaScript

---

### Backend

Responsável pelo processamento e análise do conteúdo textual.

Funções principais:

- recebimento do prontuário estruturado
- pré-processamento do texto
- identificação de padrões linguísticos
- aplicação de modelos de análise
- retorno dos resultados estruturados

Tecnologias utilizadas:

- Python
- FastAPI
- Pydantic
- bibliotecas de NLP

---

## Tecnologias Utilizadas

### Backend

- **Python**
- **FastAPI**
- **Pydantic**
- **spaCy**
- **Transformers / HuggingFace**
- **PyTest**

### Frontend

- HTML5
- CSS3
- JavaScript

### Infraestrutura

- Git / GitHub
- Docker (planejado para futuras versões)

---

## Pipeline Conceitual de Processamento

O sistema seguirá um fluxo conceitual semelhante ao seguinte:


Prontuário (texto)
↓
Normalização do texto
↓
Segmentação por seções
↓
Detecção baseada em regras
↓
Classificação por modelo de linguagem
↓
Extração de evidências textuais
↓
Geração de relatório estruturado


---

## Princípios de Desenvolvimento

O desenvolvimento do sistema segue boas práticas de engenharia de software com foco em:

- **arquitetura modular**
- **separação de responsabilidades**
- **código testável**
- **documentação clara**

Sempre que possível, serão aplicados os princípios **SOLID**, visando melhorar:

- manutenção
- extensibilidade
- clareza do código

---

## Considerações Éticas

Projetos envolvendo análise de dados relacionados à saúde exigem cuidados éticos importantes.

Portanto:

- O projeto **não utiliza dados clínicos reais identificáveis**.
- Qualquer dado utilizado deve ser **anonimizado ou sintético**.
- O sistema **não realiza diagnóstico clínico**.
- Os resultados são **apenas indicativos computacionais experimentais**.

---

## Status do Projeto

🚧 Em desenvolvimento acadêmico.

As etapas iniciais incluem:

- estruturação do repositório
- desenvolvimento da interface de coleta de dados
- implementação da API
- construção do pipeline inicial de análise textual

---

## Licença

Este projeto é disponibilizado para **fins educacionais e de pesquisa acadêmica**.

A utilização em ambientes clínicos reais **não é recomendada sem validação científica adequada**.

---

## Autor

Projeto desenvolvido no contexto de estudos acadêmicos em:

- Inteligência Artificial
- Processamento de Linguagem Natural
- Análise de Dados em Saúde Digital