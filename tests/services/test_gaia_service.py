"""
Testes unitários do GaiaService do projeto Sentinela.

Objetivo deste arquivo:
- Validar a lógica interna do serviço de integração com o Gaia
- Garantir que o payload da requisição seja montado corretamente
- Verificar se a extração de JSON funciona mesmo com respostas imperfeitas
- Confirmar que erros esperados são tratados adequadamente

Observação acadêmica:
Este teste NÃO acessa o modelo Gaia real.
Ele testa apenas a lógica local do serviço, o que caracteriza
um teste unitário verdadeiro e mais confiável.
"""

import pytest

from backend.services.gaia_service import GaiaService


def test_build_request_payload():
    """
    Verifica se o payload enviado ao modelo Gaia
    é montado no formato esperado.

    Resultado esperado:
    - deve conter model, prompt e stream
    - stream deve ser False no MVP atual
    """
    service = GaiaService()

    prompt = "Analise este prontuário."
    payload = service._build_request_payload(prompt)

    assert isinstance(payload, dict)
    assert payload["model"] == service.model_name
    assert payload["prompt"] == prompt
    assert payload["stream"] is False


def test_extract_json_from_valid_response():
    """
    Verifica se o serviço consegue extrair JSON
    quando a resposta já vem como JSON puro e válido.
    """
    service = GaiaService()

    raw_text = """
    {
      "labels": ["violencia_domestica"],
      "risk_score": 0.81,
      "severity": "alto",
      "summary": "Há indícios relevantes no texto.",
      "evidence_snippets": [
        {
          "label": "violencia_domestica",
          "snippet": "Relata agressões do companheiro.",
          "explanation": "Menção direta a agressões no ambiente doméstico."
        }
      ]
    }
    """

    result = service._extract_json_from_response(raw_text)

    assert isinstance(result, dict)
    assert result["labels"] == ["violencia_domestica"]
    assert result["risk_score"] == 0.81
    assert result["severity"] == "alto"


def test_extract_json_from_response_with_extra_text():
    """
    Verifica se o serviço consegue localizar e extrair o JSON
    quando o modelo devolve texto extra antes e depois do bloco JSON.

    Esse teste é importante porque LLMs nem sempre obedecem
    perfeitamente ao formato solicitado.
    """
    service = GaiaService()

    raw_text = """
    Aqui está o resultado da análise:

    {
      "labels": ["violencia_psicologica"],
      "risk_score": 0.56,
      "severity": "moderado",
      "summary": "Há sinais sugestivos de violência psicológica.",
      "evidence_snippets": [
        {
          "label": "violencia_psicologica",
          "snippet": "Paciente relata ameaças e humilhações recorrentes.",
          "explanation": "Há menção textual a intimidação e humilhação."
        }
      ]
    }

    Fim da resposta.
    """

    result = service._extract_json_from_response(raw_text)

    assert isinstance(result, dict)
    assert result["labels"] == ["violencia_psicologica"]
    assert result["severity"] == "moderado"


def test_extract_json_raises_error_when_no_json_exists():
    """
    Verifica se o serviço lança erro quando não existe
    nenhum bloco JSON identificável na resposta.
    """
    service = GaiaService()

    raw_text = "Resposta sem estrutura JSON alguma."

    with pytest.raises(RuntimeError) as exc_info:
        service._extract_json_from_response(raw_text)

    assert "Não foi possível localizar um bloco JSON válido" in str(exc_info.value)


def test_extract_json_raises_error_when_json_is_invalid():
    """
    Verifica se o serviço lança erro quando existe algo parecido com JSON,
    mas o conteúdo não pode ser convertido corretamente.

    Exemplo:
    - chaves sem aspas
    - sintaxe inválida
    """
    service = GaiaService()

    raw_text = """
    Texto antes.

    {
      labels: [violencia_domestica],
      risk_score: 0.8
    }

    Texto depois.
    """

    with pytest.raises(RuntimeError) as exc_info:
        service._extract_json_from_response(raw_text)

    assert "não pôde ser convertido" in str(exc_info.value).lower()


def test_extract_json_raises_error_when_json_is_not_object():
    """
    Verifica se o serviço rejeita JSON válido que não seja um objeto.

    Exemplo:
    - lista JSON
    - número
    - string

    O serviço espera especificamente um dicionário JSON,
    pois o restante do backend trabalha com esse formato.
    """
    service = GaiaService()

    raw_text = """
    [
      {
        "label": "violencia_domestica"
      }
    ]
    """

    with pytest.raises(RuntimeError) as exc_info:
        service._extract_json_from_response(raw_text)

    assert "não é um objeto válido" in str(exc_info.value).lower()