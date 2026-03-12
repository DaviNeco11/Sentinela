"""
Sentinela - Serviço de integração com o modelo Gaia

Objetivo deste arquivo:
- Centralizar a comunicação com o modelo de linguagem Gaia
- Enviar prompts para o modelo
- Receber e interpretar a resposta
- Extrair o JSON retornado pelo modelo
- Tratar erros de integração de forma controlada

Observação acadêmica:
Este projeto é desenvolvido para fins de estudo e aprendizado.
O modelo Gaia é utilizado aqui como apoio experimental para identificação
de possíveis indícios textuais, sem qualquer finalidade diagnóstica.

Princípios SOLID aplicados:
- S (Single Responsibility): este arquivo cuida apenas da integração com o Gaia
- O (Open/Closed): a integração pode ser expandida sem alterar outras camadas
- D (Dependency Inversion): a camada de análise dependerá deste serviço,
  em vez de lidar diretamente com HTTP e detalhes da API externa
"""

from __future__ import annotations

import json
from typing import Any, Dict

import httpx

from backend.core.config import settings


class GaiaService:
    """
    Serviço responsável por consultar o modelo Gaia.

    Esta classe encapsula:
    - a URL do modelo
    - o nome do modelo
    - o timeout
    - o formato da requisição HTTP
    - o tratamento da resposta

    Vantagem:
    Se amanhã o Gaia mudar de endpoint ou formato, a alteração ficará
    concentrada neste arquivo, sem impactar as demais camadas.
    """

    def __init__(self) -> None:
        """
        Inicializa o serviço usando as configurações centrais do projeto.
        """
        self.api_url = settings.GAIA_API_URL
        self.model_name = settings.GAIA_MODEL_NAME
        self.timeout_seconds = settings.GAIA_TIMEOUT_SECONDS

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Envia um prompt ao modelo Gaia e retorna a resposta já convertida em dicionário.

        Fluxo:
        1. Monta o payload HTTP
        2. Envia POST para a API do Gaia
        3. Valida o status HTTP
        4. Lê o campo textual da resposta
        5. Extrai o JSON produzido pelo modelo
        6. Retorna o conteúdo parseado
        """
        request_payload = self._build_request_payload(prompt)
        raw_response_text = await self._send_request(request_payload)
        parsed_response = self._extract_json_from_response(raw_response_text)
        return parsed_response

    def _build_request_payload(self, prompt: str) -> Dict[str, Any]:
        """
        Monta o corpo da requisição HTTP para o Gaia.

        Neste MVP, assumimos um formato semelhante a:
        {
          "model": "gaia:latest",
          "prompt": "...",
          "stream": false
        }
        """
        return {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }

    async def _send_request(self, payload: Dict[str, Any]) -> str:
        """
        Envia a requisição HTTP para o Gaia e retorna o texto bruto da resposta.

        Esta função:
        - abre um cliente HTTP assíncrono
        - envia a requisição POST
        - valida o status HTTP
        - extrai o campo textual esperado da resposta
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(self.api_url, json=payload)
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Erro de conexão ao acessar o Gaia em '{self.api_url}': {exc}"
            ) from exc

        if response.status_code != 200:
            raise RuntimeError(
                "Falha ao consultar o Gaia. "
                f"Status HTTP: {response.status_code}. "
                f"Resposta: {response.text}"
            )

        try:
            response_data = response.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "A API do Gaia respondeu, mas o corpo HTTP não é um JSON válido."
            ) from exc

        # Muitos servidores de LLM devolvem a saída textual no campo "response"
        raw_text = response_data.get("response")

        if not raw_text or not isinstance(raw_text, str):
            raise RuntimeError(
                "A resposta do Gaia não contém um campo textual 'response' válido."
            )

        return raw_text

    def _extract_json_from_response(self, raw_text: str) -> Dict[str, Any]:
        """
        Extrai um JSON válido do texto retornado pelo modelo.

        Estratégia:
        1. tenta converter a resposta inteira em JSON
        2. se falhar, busca o trecho entre o primeiro '{' e o último '}'
        3. tenta converter esse trecho em JSON
        """
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                return parsed
            raise RuntimeError("O JSON retornado pelo Gaia não é um objeto válido.")
        except json.JSONDecodeError:
            pass

        start = raw_text.find("{")
        end = raw_text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise RuntimeError(
                "Não foi possível localizar um bloco JSON válido na resposta do Gaia."
            )

        candidate_json = raw_text[start:end + 1]

        try:
            parsed = json.loads(candidate_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Foi localizado um possível bloco JSON, mas ele não pôde ser convertido."
            ) from exc

        if not isinstance(parsed, dict):
            raise RuntimeError("O conteúdo extraído do Gaia não é um objeto JSON válido.")

        return parsed