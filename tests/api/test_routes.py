"""
Testes unitários das rotas da API do projeto Sentinela.

Objetivo deste arquivo:
- Validar o comportamento HTTP básico da aplicação
- Garantir que as rotas principais respondam corretamente
- Testar a integração entre a camada web e o serviço de análise
- Evitar dependência do modelo Gaia real durante os testes

Observação acadêmica:
Este teste usa um serviço de análise falso (fake) para isolar
a camada HTTP. Assim, validamos as rotas sem depender de rede,
modelo externo ou comportamento imprevisível de LLM.
"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas.prontuario import AnalysisResult, EvidenceSnippet
from backend.api import routes


class FakeAnalysisService:
    """
    Serviço falso de análise usado apenas nos testes.

    Responsabilidade:
    - simular uma resposta estável da camada de análise
    - permitir que o teste da rota seja determinístico
    - evitar dependência do Gaia real

    Este fake implementa o mesmo método esperado pela rota:
    - analyze_prontuario(payload)
    """

    async def analyze_prontuario(self, payload):
        """
        Retorna uma resposta simulada e padronizada.

        O conteúdo imita o formato real do AnalysisResult.
        """
        return AnalysisResult(
            labels=["violencia_domestica"],
            risk_score=0.77,
            severity="alto",
            summary="Há indícios relevantes no prontuário.",
            evidence_snippets=[
                EvidenceSnippet(
                    label="violencia_domestica",
                    snippet="Paciente relata agressões do companheiro.",
                    explanation="Há menção direta a agressões no ambiente doméstico.",
                )
            ],
            model_version="fake-analysis-service-v1",
        )


class FakeAnalysisServiceWithRuntimeError:
    """
    Serviço falso que simula falha de integração/processamento.

    Útil para testar se a rota converte RuntimeError em HTTP 502.
    """

    async def analyze_prontuario(self, payload):
        raise RuntimeError("Falha simulada ao consultar o serviço externo.")


# Cliente de teste do FastAPI
client = TestClient(app)


def test_healthcheck_returns_ok():
    """
    Verifica se a rota /health responde corretamente.

    Resultado esperado:
    - status code 200
    - corpo com informações básicas da aplicação
    """
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data
    assert "version" in data
    assert "environment" in data


def test_index_route_returns_html_file():
    """
    Verifica se a rota principal '/' responde com sucesso.

    Como o backend serve o frontend, esperamos:
    - status code 200
    - conteúdo HTML
    """
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_analyze_prontuario_returns_analysis_result(monkeypatch):
    """
    Verifica se a rota /analyze_prontuario responde corretamente
    quando recebe um payload válido.

    Estratégia:
    - substituímos o analysis_service real pelo fake
    - enviamos um payload válido
    - validamos o retorno da rota
    """

    # Substitui o serviço real pelo fake apenas durante este teste
    monkeypatch.setattr(routes, "analysis_service", FakeAnalysisService())

    payload = {
        "sections": {
            "queixa_principal": "Paciente relata medo de voltar para casa.",
            "anamnese": "Refere agressões do companheiro."
        },
        "metadata": {
            "age_group": "adulto",
            "visit_type": "urgencia"
        }
    }

    response = client.post("/analyze_prontuario", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["labels"] == ["violencia_domestica"]
    assert data["risk_score"] == 0.77
    assert data["severity"] == "alto"
    assert data["model_version"] == "fake-analysis-service-v1"
    assert len(data["evidence_snippets"]) == 1


def test_analyze_prontuario_rejects_invalid_payload():
    """
    Verifica se a rota /analyze_prontuario rejeita payload inválido.

    Cenário:
    - payload vazio
    - o schema ProntuarioInput deve falhar na validação

    Resultado esperado:
    - status code 422
    """
    payload = {}

    response = client.post("/analyze_prontuario", json=payload)

    assert response.status_code == 422


def test_analyze_prontuario_returns_502_on_runtime_error(monkeypatch):
    """
    Verifica se a rota converte RuntimeError em HTTP 502.

    Isso é importante porque a camada de rotas foi projetada
    para tratar falhas esperadas de integração/processamento
    como erro de gateway/serviço externo.
    """
    monkeypatch.setattr(routes, "analysis_service", FakeAnalysisServiceWithRuntimeError())

    payload = {
        "text": "Paciente relata agressões frequentes no ambiente doméstico."
    }

    response = client.post("/analyze_prontuario", json=payload)

    assert response.status_code == 502

    data = response.json()
    assert "detail" in data
    assert "Falha simulada" in data["detail"]