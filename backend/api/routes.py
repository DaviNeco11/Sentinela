"""
Sentinela - Rotas da API

Objetivo deste arquivo:
- Definir os endpoints HTTP do backend
- Entregar os arquivos do frontend
- Receber dados enviados pelo formulário
- Acionar o serviço de análise
- Retornar a resposta para o cliente

Observação acadêmica:
Este projeto é desenvolvido para fins de estudo e aprendizado.
Aqui separamos a camada HTTP da lógica de negócio para manter o código
mais organizado, legível e fácil de evoluir.

Princípios SOLID aplicados:
- S (Single Responsibility): este arquivo cuida apenas da camada de rotas
- O (Open/Closed): novas rotas podem ser adicionadas sem alterar a lógica dos serviços
- D (Dependency Inversion): as rotas dependem do serviço de análise,
  e não da implementação detalhada do modelo Gaia
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.core.config import settings
from backend.schemas.prontuario import AnalysisResult, ProntuarioInput
from backend.services.analysis_service import AnalysisService


# ============================================================
# Instâncias principais da camada de rotas
# ============================================================

# APIRouter permite organizar endpoints separadamente do main.py.
router = APIRouter()

# Instância do serviço principal de análise.
# Neste MVP, usamos uma instância simples e direta.
analysis_service = AnalysisService()


# ============================================================
# Rotas utilitárias
# ============================================================

@router.get("/health")
def healthcheck() -> dict:
    """
    Endpoint de verificação de saúde da aplicação.

    Finalidade:
    - confirmar se a API está ativa
    - servir como teste rápido de funcionamento
    - ajudar em depuração e monitoramento

    Retorno:
    - dicionário simples com status da aplicação
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


# ============================================================
# Rotas do frontend
# ============================================================

@router.get("/")
def serve_index() -> FileResponse:
    """
    Entrega o arquivo principal do frontend.

    Essa rota permite que o navegador abra a interface HTML
    diretamente a partir do backend.

    Se o arquivo não existir, retornamos erro 404.
    """
    if not settings.INDEX_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Arquivo frontend/index.html não encontrado."
        )

    return FileResponse(settings.INDEX_FILE)


@router.get("/styles.css")
def serve_css() -> FileResponse:
    """
    Entrega o arquivo de estilos do frontend.

    Mantemos uma rota explícita para facilitar entendimento do fluxo.
    """
    if not settings.CSS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Arquivo frontend/styles.css não encontrado."
        )

    return FileResponse(settings.CSS_FILE, media_type="text/css")


@router.get("/app.js")
def serve_js() -> FileResponse:
    """
    Entrega o arquivo JavaScript do frontend.

    Esse arquivo contém a lógica do formulário e o envio do prontuário
    para a rota de análise.
    """
    if not settings.JS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Arquivo frontend/app.js não encontrado."
        )

    return FileResponse(settings.JS_FILE, media_type="application/javascript")


# ============================================================
# Rota principal de análise
# ============================================================

@router.post("/analyze_prontuario", response_model=AnalysisResult)
async def analyze_prontuario(payload: ProntuarioInput) -> AnalysisResult:
    """
    Endpoint principal do MVP do Sentinela.

    Fluxo desta rota:
    1. Recebe o payload enviado pelo frontend
    2. Valida automaticamente os dados com Pydantic
    3. Chama o AnalysisService
    4. Retorna a resposta padronizada ao cliente

    Parâmetros:
    - payload: prontuário validado no formato ProntuarioInput

    Retorno:
    - objeto AnalysisResult

    Tratamento de erro:
    - exceções de integração e análise são convertidas em erro HTTP 502,
      indicando falha ao processar a requisição com serviço externo/modelo
    """
    try:
        result = await analysis_service.analyze_prontuario(payload)
        return result

    except ValueError as exc:
        # Erros de validação de negócio ou conteúdo inadequado
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    except RuntimeError as exc:
        # Erros esperados da integração com Gaia ou parsing da resposta
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        # Fallback para erros inesperados
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar o prontuário: {exc}"
        ) from exc