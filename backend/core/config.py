from __future__ import annotations

import os
from pathlib import Path


class Settings:
    """
    Classe responsável por reunir e expor as configurações do projeto.

    Por enquanto, esta classe:
    - lê valores de variáveis de ambiente
    - define valores padrão quando necessário
    - calcula caminhos importantes do projeto

    Vantagem desta abordagem:
    - outras partes do sistema importam apenas 'settings'
    - não precisam saber de onde veio cada configuração
    """

    def __init__(self) -> None:
        """
        Inicializa todas as configurações do projeto.

        Observação:
        As variáveis de ambiente permitem alterar comportamento sem editar o código.
        Isso é útil para:
        - mudar o modelo Gaia
        - trocar endpoint
        - ajustar timeout
        - migrar entre ambientes
        """

        # ============================================================
        # Caminhos do projeto
        # ============================================================

        # Pasta backend/
        self.BACKEND_DIR = Path(__file__).resolve().parent.parent

        # Pasta raiz do projeto sentinela/
        self.BASE_DIR = self.BACKEND_DIR.parent

        # Pasta frontend/
        self.FRONTEND_DIR = self.BASE_DIR / "frontend"

        # Arquivos principais do frontend
        self.INDEX_FILE = self.FRONTEND_DIR / "index.html"
        self.CSS_FILE = self.FRONTEND_DIR / "styles.css"
        self.JS_FILE = self.FRONTEND_DIR / "app.js"

        # ============================================================
        # Configurações da aplicação
        # ============================================================

        # Nome da aplicação, útil para logs e documentação
        self.APP_NAME = os.getenv("APP_NAME", "Sentinela API")

        # Versão inicial da API
        self.APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

        # Ambiente de execução: dev, test, prod etc.
        self.APP_ENV = os.getenv("APP_ENV", "development")

        # ============================================================
        # Configurações do modelo Gaia
        # ============================================================

        # URL da API do Gaia
        # Exemplo:
        # http://localhost:11434/api/generate
        self.GAIA_API_URL = os.getenv(
            "GAIA_API_URL",
            "http://localhost:11434/api/generate"
        )

        # Nome do modelo a ser utilizado
        # Exemplo:
        # gaia:latest
        self.GAIA_MODEL_NAME = os.getenv(
            "GAIA_MODEL_NAME",
            "gaia:latest"
        )

        # Timeout da chamada ao modelo, em segundos
        # Usamos int para garantir valor numérico
        self.GAIA_TIMEOUT_SECONDS = int(
            os.getenv("GAIA_TIMEOUT_SECONDS", "120")
        )

    def as_dict(self) -> dict:
        """
        Retorna as configurações em formato de dicionário.

        Utilidade:
        - depuração
        - inspeção em testes
        - logging controlado

        Atenção:
        Em projetos reais, deve-se evitar expor informações sensíveis.
        Neste MVP acadêmico, estamos lidando apenas com configurações gerais.
        """
        return {
            "APP_NAME": self.APP_NAME,
            "APP_VERSION": self.APP_VERSION,
            "APP_ENV": self.APP_ENV,
            "BASE_DIR": str(self.BASE_DIR),
            "BACKEND_DIR": str(self.BACKEND_DIR),
            "FRONTEND_DIR": str(self.FRONTEND_DIR),
            "INDEX_FILE": str(self.INDEX_FILE),
            "CSS_FILE": str(self.CSS_FILE),
            "JS_FILE": str(self.JS_FILE),
            "GAIA_API_URL": self.GAIA_API_URL,
            "GAIA_MODEL_NAME": self.GAIA_MODEL_NAME,
            "GAIA_TIMEOUT_SECONDS": self.GAIA_TIMEOUT_SECONDS,
        }


# Instância única de configuração do projeto
# Esta será importada pelas demais camadas do backend.
settings = Settings()