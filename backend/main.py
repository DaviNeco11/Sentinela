"""
Sentinela - Ponto de entrada da aplicação FastAPI

Objetivo deste arquivo:
- Criar a instância principal da aplicação FastAPI
- Configurar informações básicas da API
- Registrar as rotas definidas em backend/api/routes.py

Observação acadêmica:
Este projeto é desenvolvido para fins de estudo e aprendizado.
Por isso, mantemos este arquivo simples e enxuto, para deixar claro
o papel de cada camada dentro da arquitetura.

Princípios SOLID aplicados:
- S (Single Responsibility): este arquivo cuida apenas da inicialização da aplicação
- O (Open/Closed): novas configurações e middlewares podem ser adicionados sem alterar a lógica das rotas
- D (Dependency Inversion): a aplicação depende de módulos bem definidos,
  em vez de concentrar lógica de negócio aqui
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.api.routes import router
from backend.core.config import settings


def create_app() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI.

    Responsabilidades desta função:
    - instanciar o objeto principal da API
    - definir metadados da aplicação
    - registrar as rotas do sistema

    Vantagem de usar uma fábrica de aplicação:
    - facilita testes automatizados
    - melhora organização
    - permite futura configuração por ambiente
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "API acadêmica do projeto Sentinela para análise textual "
            "de prontuários simulados com apoio de modelo de linguagem."
        ),
    )

    # Inclui todas as rotas definidas na camada HTTP.
    # Como estamos em um MVP simples, usamos o router principal diretamente.
    app.include_router(router)

    return app


# Instância principal da aplicação.
# Esta variável é utilizada pelo uvicorn no comando:
# python -m uvicorn backend.main:app --reload
app = create_app()