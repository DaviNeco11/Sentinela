"""
Testes unitários do AnalysisService do projeto Sentinela.

Objetivo deste arquivo:
- Validar a lógica principal de análise do prontuário
- Garantir que o texto do prontuário seja montado corretamente
- Testar a normalização da resposta do modelo
- Testar o fluxo completo do serviço usando um GaiaService falso (mock)

Observação acadêmica:
Para manter os testes unitários isolados e determinísticos,
não chamamos o modelo Gaia real. Em vez disso, utilizamos um
FakeGaiaService que retorna respostas simuladas.
"""

import pytest

from backend.schemas.prontuario import ProntuarioInput
from backend.services.analysis_service import AnalysisService


class FakeGaiaService:
    """
    Implementação falsa do GaiaService.

    Esta classe simula a resposta do modelo Gaia para permitir
    testes determinísticos do AnalysisService.

    Ela segue o mesmo contrato da função generate().
    """

    async def generate(self, prompt: str):
        """
        Retorna uma resposta simulada do modelo.

        O conteúdo retornado imita o JSON esperado pelo AnalysisService.
        """
        return {
            "labels": ["violencia_domestica"],
            "risk_score": 0.72,
            "severity": "alto",
            "summary": "Há indícios de violência doméstica no texto.",
            "evidence_snippets": [
                {
                    "label": "violencia_domestica",
                    "snippet": "Paciente relata agressões do companheiro.",
                    "explanation": "Menção direta a agressões no ambiente doméstico."
                }
            ]
        }


@pytest.mark.asyncio
async def test_analysis_service_with_text():
    """
    Testa o fluxo completo de análise usando texto livre.

    Cenário:
    - o prontuário é enviado no campo 'text'
    - o GaiaService é substituído por FakeGaiaService

    Resultado esperado:
    - a resposta deve conter labels e evidências simuladas
    """

    payload = ProntuarioInput(
        text="Paciente relata agressões frequentes do companheiro."
    )

    service = AnalysisService(gaia_service=FakeGaiaService())

    result = await service.analyze_prontuario(payload)

    assert result.labels == ["violencia_domestica"]
    assert result.risk_score == 0.72
    assert result.severity == "alto"
    assert len(result.evidence_snippets) == 1


@pytest.mark.asyncio
async def test_analysis_service_with_sections():
    """
    Testa o fluxo de análise quando o prontuário vem em seções.

    Cenário:
    - o payload possui 'sections'
    - o texto precisa ser montado internamente pelo serviço
    """

    payload = ProntuarioInput(
        sections={
            "queixa_principal": "Paciente relata medo de voltar para casa.",
            "anamnese": "Refere agressões físicas recentes."
        }
    )

    service = AnalysisService(gaia_service=FakeGaiaService())

    result = await service.analyze_prontuario(payload)

    assert result.labels == ["violencia_domestica"]
    assert result.severity == "alto"


def test_build_text_from_sections():
    """
    Testa diretamente a função interna de construção de texto.

    Cenário:
    - o prontuário possui várias seções
    - o serviço deve gerar um texto concatenado
    """

    payload = ProntuarioInput(
        sections={
            "queixa_principal": "Paciente com ansiedade.",
            "anamnese": "Relata conflitos familiares.",
            "observacoes": "Paciente aparenta medo."
        }
    )

    service = AnalysisService(gaia_service=FakeGaiaService())

    text = service._build_text_from_payload(payload)

    assert "Queixa Principal" in text
    assert "Anamnese" in text
    assert "Observacoes" in text


def test_normalize_analysis_result_handles_invalid_values():
    """
    Testa a normalização quando o modelo retorna valores inesperados.

    Cenário:
    - labels inválidas
    - risk_score fora do intervalo
    - severity inválida

    Resultado esperado:
    - o método deve corrigir ou aplicar valores padrão
    """

    service = AnalysisService(gaia_service=FakeGaiaService())

    raw_model_output = {
        "labels": "violencia_domestica",
        "risk_score": 5,
        "severity": "critico",
        "summary": "Texto qualquer",
        "evidence_snippets": []
    }

    result = service._normalize_analysis_result(raw_model_output)

    assert result.labels == []
    assert result.risk_score == 1.0
    assert result.severity == "baixo"


def test_prompt_contains_prontuario_text():
    """
    Testa se o prompt construído contém o texto do prontuário.

    Isso é importante porque o modelo precisa receber o conteúdo
    para realizar a análise.
    """

    service = AnalysisService(gaia_service=FakeGaiaService())

    prontuario_text = "Paciente relata agressão."

    prompt = service._build_gaia_prompt(prontuario_text)

    assert "Paciente relata agressão." in prompt
    assert "Retorne SOMENTE um JSON válido" in prompt