"""
Sentinela - Schemas de prontuário e resposta da análise

Objetivo deste arquivo:
- Definir os modelos de dados utilizados pela API
- Validar a estrutura do prontuário recebido
- Padronizar a resposta da análise
- Melhorar legibilidade e segurança do código

Observação acadêmica:
Este projeto é desenvolvido para fins de estudo e aprendizado.
Aqui utilizamos Pydantic para modelar e validar dados,
o que é muito comum em APIs Python modernas.

Princípios SOLID aplicados:
- S (Single Responsibility): este arquivo cuida apenas dos contratos de dados
- O (Open/Closed): novos campos podem ser adicionados sem alterar a lógica principal
- I (Interface Segregation): cada classe representa uma estrutura específica e enxuta
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class ProntuarioInput(BaseModel):
    """
    Modelo de entrada do prontuário.

    Este schema representa o payload recebido pelo backend.
    O frontend pode enviar o prontuário de duas formas:

    1) text:
       Um texto único contendo todo o prontuário

    2) sections:
       Um dicionário com seções separadas do prontuário,
       como queixa principal, anamnese, evolução etc.

    metadata:
       Informações complementares, como faixa etária e tipo de atendimento

    Observação:
    O sistema exige que pelo menos 'text' ou 'sections' seja informado.
    """

    text: Optional[str] = Field(
        default=None,
        description="Texto completo do prontuário, quando enviado em formato livre."
    )

    sections: Optional[Dict[str, str]] = Field(
        default=None,
        description="Prontuário organizado por seções, como anamnese e evolução."
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadados complementares do prontuário, sem dados pessoais identificáveis."
    )

    @model_validator(mode="after")
    def validate_content(self) -> "ProntuarioInput":
        """
        Validador de negócio do schema.

        Responsabilidade:
        Garantir que o payload tenha conteúdo útil para análise.

        Regra:
        - deve existir 'text' preenchido
          OU
        - deve existir ao menos uma seção preenchida em 'sections'

        Isso evita que a API receba objetos vazios.
        """
        has_text = bool(self.text and self.text.strip())

        has_sections = False
        if self.sections:
            # Verifica se existe ao menos um valor de seção não vazio
            has_sections = any(
                bool(value and value.strip())
                for value in self.sections.values()
            )

        if not has_text and not has_sections:
            raise ValueError(
                "É necessário informar 'text' ou ao menos uma seção preenchida em 'sections'."
            )

        return self


class EvidenceSnippet(BaseModel):
    """
    Modelo que representa uma evidência textual identificada na análise.

    Cada evidência contém:
    - label: categoria do possível indício
    - snippet: trecho do texto relacionado ao indício
    - explanation: breve explicação do porquê esse trecho foi considerado relevante

    Exemplo:
    {
      "label": "violencia_domestica",
      "snippet": "relata agressões frequentes do companheiro",
      "explanation": "há menção explícita a agressões no ambiente doméstico"
    }
    """

    label: str = Field(
        ...,
        description="Categoria do indício identificado."
    )

    snippet: str = Field(
        ...,
        description="Trecho textual que sustenta o possível indício."
    )

    explanation: str = Field(
        ...,
        description="Explicação curta sobre a relevância do trecho."
    )


class AnalysisResult(BaseModel):
    """
    Modelo de saída da análise realizada pelo backend.

    Este schema padroniza o retorno para o frontend.

    Campos:
    - labels: lista de categorias encontradas
    - risk_score: escore numérico entre 0 e 1
    - severity: classificação qualitativa do risco
    - summary: resumo textual da análise
    - evidence_snippets: evidências encontradas
    - model_version: identifica o modelo/estratégia usada

    Observação:
    Mesmo quando não houver indícios, a resposta deve seguir esta estrutura.
    """

    labels: List[str] = Field(
        default_factory=list,
        description="Lista de categorias de possíveis indícios identificados."
    )

    risk_score: float = Field(
        default=0.0,
        description="Escore de risco entre 0 e 1."
    )

    severity: str = Field(
        default="baixo",
        description="Classificação qualitativa do risco: baixo, moderado ou alto."
    )

    summary: str = Field(
        default="",
        description="Resumo geral da análise."
    )

    evidence_snippets: List[EvidenceSnippet] = Field(
        default_factory=list,
        description="Lista de evidências textuais relacionadas aos indícios."
    )

    model_version: str = Field(
        default="unknown",
        description="Identificação da versão do modelo ou pipeline utilizado."
    )

    @model_validator(mode="after")
    def validate_result(self) -> "AnalysisResult":
        """
        Validador para manter consistência mínima na resposta.

        Regras aplicadas:
        - risk_score deve ficar entre 0 e 1
        - severity deve ser 'baixo', 'moderado' ou 'alto'

        Caso valores inválidos cheguem aqui, o schema rejeita o objeto.
        """
        if not (0.0 <= self.risk_score <= 1.0):
            raise ValueError("risk_score deve estar entre 0 e 1.")

        if self.severity not in {"baixo", "moderado", "alto"}:
            raise ValueError("severity deve ser 'baixo', 'moderado' ou 'alto'.")

        return self