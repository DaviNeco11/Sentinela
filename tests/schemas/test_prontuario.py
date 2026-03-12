"""
Testes unitários dos schemas de prontuário do projeto Sentinela.

Objetivo deste arquivo:
- Validar o comportamento dos modelos Pydantic
- Garantir que entradas e saídas sigam o contrato esperado
- Verificar se as regras mínimas de validação estão funcionando

Observação acadêmica:
Estes testes ajudam a garantir que a base do sistema esteja consistente.
Como os schemas são usados por várias camadas, erros aqui podem afetar
todo o fluxo da aplicação.

Bibliotecas usadas:
- pytest: framework de testes
- pydantic: validações lançam exceções quando os dados são inválidos
"""

import pytest
from pydantic import ValidationError

from backend.schemas.prontuario import (
    AnalysisResult,
    EvidenceSnippet,
    ProntuarioInput,
)


def test_prontuario_input_accepts_text():
    """
    Verifica se o schema aceita um prontuário enviado como texto livre.

    Cenário:
    - o campo 'text' contém conteúdo válido
    - o campo 'sections' não é necessário nesse caso

    Resultado esperado:
    - o objeto deve ser criado com sucesso
    """
    payload = ProntuarioInput(
        text="Paciente relata medo de voltar para casa."
    )

    assert payload.text == "Paciente relata medo de voltar para casa."
    assert payload.sections is None


def test_prontuario_input_accepts_sections():
    """
    Verifica se o schema aceita um prontuário enviado por seções.

    Cenário:
    - 'sections' possui ao menos uma chave preenchida

    Resultado esperado:
    - o objeto deve ser criado com sucesso
    """
    payload = ProntuarioInput(
        sections={
            "queixa_principal": "Paciente refere tristeza constante.",
            "anamnese": "Relata discussões frequentes no ambiente doméstico.",
        }
    )

    assert payload.sections is not None
    assert payload.sections["queixa_principal"] == "Paciente refere tristeza constante."


def test_prontuario_input_accepts_text_and_sections():
    """
    Verifica se o schema aceita tanto 'text' quanto 'sections' simultaneamente.

    Isso não é proibido pelo contrato atual.
    Em alguns cenários acadêmicos, pode ser útil ter as duas formas de entrada.
    """
    payload = ProntuarioInput(
        text="Texto consolidado do prontuário.",
        sections={
            "observacoes": "Observação complementar."
        }
    )

    assert payload.text == "Texto consolidado do prontuário."
    assert payload.sections["observacoes"] == "Observação complementar."


def test_prontuario_input_rejects_empty_payload():
    """
    Verifica se o schema rejeita payload sem conteúdo útil.

    Cenário:
    - não há 'text'
    - não há 'sections'

    Resultado esperado:
    - deve ocorrer erro de validação
    """
    with pytest.raises(ValidationError) as exc_info:
        ProntuarioInput()

    # Verificamos parte da mensagem para garantir que o motivo está correto
    assert "É necessário informar 'text' ou ao menos uma seção preenchida" in str(exc_info.value)


def test_prontuario_input_rejects_blank_text():
    """
    Verifica se o schema rejeita texto em branco.

    Cenário:
    - 'text' contém apenas espaços
    - não há sections válidas

    Resultado esperado:
    - deve ocorrer erro de validação
    """
    with pytest.raises(ValidationError):
        ProntuarioInput(text="   ")


def test_prontuario_input_rejects_empty_sections_values():
    """
    Verifica se o schema rejeita sections presentes, mas sem conteúdo útil.

    Cenário:
    - as chaves existem
    - os valores estão vazios ou com espaços

    Resultado esperado:
    - deve ocorrer erro de validação
    """
    with pytest.raises(ValidationError):
        ProntuarioInput(
            sections={
                "queixa_principal": "   ",
                "anamnese": "",
            }
        )


def test_evidence_snippet_valid_creation():
    """
    Verifica se uma evidência válida pode ser criada corretamente.

    Isso é importante porque a resposta final da análise depende desse objeto.
    """
    evidence = EvidenceSnippet(
        label="violencia_domestica",
        snippet="Relata agressões frequentes do companheiro.",
        explanation="Há menção explícita a agressões no ambiente doméstico.",
    )

    assert evidence.label == "violencia_domestica"
    assert "agressões frequentes" in evidence.snippet


def test_analysis_result_valid_creation():
    """
    Verifica se o schema de saída aceita uma resposta válida.

    Cenário:
    - risk_score dentro do intervalo 0..1
    - severity válida
    - evidências em formato correto

    Resultado esperado:
    - o objeto deve ser criado sem erros
    """
    result = AnalysisResult(
        labels=["violencia_domestica", "violencia_fisica"],
        risk_score=0.82,
        severity="alto",
        summary="Foram encontrados indícios relevantes no texto.",
        evidence_snippets=[
            EvidenceSnippet(
                label="violencia_fisica",
                snippet="Refere agressão física recente.",
                explanation="Há menção direta a agressão física.",
            )
        ],
        model_version="gaia-mvp-v1",
    )

    assert len(result.labels) == 2
    assert result.risk_score == 0.82
    assert result.severity == "alto"
    assert len(result.evidence_snippets) == 1


def test_analysis_result_rejects_risk_score_below_zero():
    """
    Verifica se o schema rejeita risk_score menor que zero.

    Resultado esperado:
    - erro de validação
    """
    with pytest.raises(ValidationError) as exc_info:
        AnalysisResult(
            risk_score=-0.1,
            severity="baixo",
        )

    assert "risk_score deve estar entre 0 e 1" in str(exc_info.value)


def test_analysis_result_rejects_risk_score_above_one():
    """
    Verifica se o schema rejeita risk_score maior que 1.

    Resultado esperado:
    - erro de validação
    """
    with pytest.raises(ValidationError) as exc_info:
        AnalysisResult(
            risk_score=1.5,
            severity="moderado",
        )

    assert "risk_score deve estar entre 0 e 1" in str(exc_info.value)


def test_analysis_result_rejects_invalid_severity():
    """
    Verifica se o schema rejeita severity fora dos valores permitidos.

    Valores permitidos:
    - baixo
    - moderado
    - alto
    """
    with pytest.raises(ValidationError) as exc_info:
        AnalysisResult(
            risk_score=0.4,
            severity="critico",
        )

    assert "severity deve ser 'baixo', 'moderado' ou 'alto'" in str(exc_info.value)


def test_analysis_result_defaults_are_applied():
    """
    Verifica se os valores padrão do schema são aplicados corretamente.

    Esse teste é útil para garantir previsibilidade da resposta
    quando campos opcionais não forem informados.
    """
    result = AnalysisResult()

    assert result.labels == []
    assert result.risk_score == 0.0
    assert result.severity == "baixo"
    assert result.summary == ""
    assert result.evidence_snippets == []
    assert result.model_version == "unknown"