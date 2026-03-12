from __future__ import annotations

from typing import Any, Dict, List

from backend.schemas.prontuario import (
    AnalysisResult,
    EvidenceSnippet,
    ProntuarioInput,
)
from backend.services.gaia_service import GaiaService


class AnalysisService:
    """
    Serviço responsável por executar o fluxo principal de análise.

    Esta classe orquestra o processo completo:
    1. recebe o prontuário
    2. gera um texto único e organizado
    3. monta o prompt para o modelo
    4. consulta o Gaia
    5. normaliza a resposta
    6. devolve um AnalysisResult padronizado

    Vantagem desta camada:
    - a API não precisa conhecer detalhes de prompt ou parsing
    - o serviço Gaia não precisa conhecer regras de negócio
    """

    def __init__(self, gaia_service: GaiaService | None = None) -> None:
        """
        Inicializa o serviço de análise.

        Parâmetros:
        - gaia_service: permite injeção de dependência para testes ou futuras trocas

        Se não for fornecido, o serviço cria uma instância padrão de GaiaService.
        """
        self.gaia_service = gaia_service or GaiaService()

    async def analyze_prontuario(self, payload: ProntuarioInput) -> AnalysisResult:
        """
        Executa o fluxo completo de análise do prontuário.

        Etapas:
        - construir o texto a partir do payload
        - montar o prompt
        - consultar o Gaia
        - normalizar a resposta

        Parâmetros:
        - payload: prontuário validado recebido pela API

        Retorno:
        - AnalysisResult padronizado
        """
        prontuario_text = self._build_text_from_payload(payload)
        prompt = self._build_gaia_prompt(prontuario_text)
        model_output = await self.gaia_service.generate(prompt)
        result = self._normalize_analysis_result(model_output)
        return result

    def _build_text_from_payload(self, payload: ProntuarioInput) -> str:
        """
        Constrói um texto único e organizado a partir do payload.

        Estratégia:
        - se houver 'text', usa o texto diretamente
        - se houver 'sections', concatena em ordem lógica
        - ignora campos vazios

        Isso melhora a leitura do modelo e torna o prompt mais consistente.
        """
        # Caso 1: o usuário enviou um texto livre completo
        if payload.text and payload.text.strip():
            return payload.text.strip()

        # Caso 2: o usuário enviou o prontuário por seções
        parts: List[str] = []

        if payload.sections:
            # Ordem lógica das seções principais do prontuário
            ordered_keys = [
                "queixa_principal",
                "anamnese",
                "evolucao",
                "observacoes",
                "antecedentes",
            ]

            # Primeiro percorremos as chaves conhecidas, para manter consistência
            for key in ordered_keys:
                value = payload.sections.get(key)
                if value and value.strip():
                    section_title = key.replace("_", " ").title()
                    parts.append(f"{section_title}: {value.strip()}")

            # Depois adicionamos chaves extras, caso existam
            for key, value in payload.sections.items():
                if key not in ordered_keys and value and value.strip():
                    section_title = key.replace("_", " ").title()
                    parts.append(f"{section_title}: {value.strip()}")

        # Retorna um texto único, separado por quebras de linha
        return "\n".join(parts).strip()

    def _build_gaia_prompt(self, prontuario_text: str) -> str:
        """
        Monta o prompt a ser enviado ao modelo Gaia.

        Objetivo do prompt:
        - focar em possíveis indícios de violência
        - deixar claro que não se trata de diagnóstico
        - pedir saída em JSON
        - reduzir respostas vagas ou excessivamente livres

        A qualidade do prompt é central para a qualidade do MVP.
        """
        return f"""
Você é um assistente acadêmico de apoio à análise textual de prontuários simulados.

Sua tarefa é analisar o texto abaixo e identificar POSSÍVEIS indícios de violência.
Não faça diagnóstico. Não trate a saída como certeza. Apenas aponte sinais textuais sugestivos.

Categorias possíveis:
- violencia_fisica
- violencia_psicologica
- violencia_sexual
- negligencia
- violencia_domestica
- outros_indicios

Retorne SOMENTE um JSON válido, sem comentários extras, no seguinte formato:

{{
  "labels": ["violencia_domestica", "violencia_fisica"],
  "risk_score": 0.78,
  "severity": "alto",
  "summary": "Resumo curto dos principais indícios encontrados.",
  "evidence_snippets": [
    {{
      "label": "violencia_fisica",
      "snippet": "trecho curto do texto que sustenta o indício",
      "explanation": "explicação breve"
    }}
  ]
}}

Regras importantes:
- Se não houver indícios claros, retorne labels vazio, risk_score baixo e severity "baixo".
- Baseie-se somente no texto fornecido.
- Não invente informações.
- Use risk_score entre 0 e 1.
- Use severity apenas como: "baixo", "moderado" ou "alto".

Texto do prontuário:
\"\"\"
{prontuario_text}
\"\"\"
""".strip()

    def _normalize_analysis_result(self, model_output: Dict[str, Any]) -> AnalysisResult:
        """
        Normaliza a saída do modelo Gaia para o formato AnalysisResult.

        Problema que esta função resolve:
        Modelos de linguagem podem devolver:
        - tipos inesperados
        - campos ausentes
        - valores fora do padrão esperado

        Esta função protege a API e o frontend, convertendo tudo para um formato consistente.
        """
        # ------------------------------------------------------------
        # Normalização de labels
        # ------------------------------------------------------------
        labels = model_output.get("labels", [])
        if not isinstance(labels, list):
            labels = []

        # Garantimos que os itens de labels sejam strings
        normalized_labels = []
        for item in labels:
            if isinstance(item, str) and item.strip():
                normalized_labels.append(item.strip())

        # ------------------------------------------------------------
        # Normalização de risk_score
        # ------------------------------------------------------------
        risk_score = model_output.get("risk_score", 0.0)
        try:
            risk_score = float(risk_score)
        except (TypeError, ValueError):
            risk_score = 0.0

        # Mantém o valor entre 0 e 1
        risk_score = max(0.0, min(1.0, risk_score))

        # ------------------------------------------------------------
        # Normalização de severity
        # ------------------------------------------------------------
        severity = str(model_output.get("severity", "baixo")).strip().lower()
        if severity not in {"baixo", "moderado", "alto"}:
            severity = "baixo"

        # ------------------------------------------------------------
        # Normalização de summary
        # ------------------------------------------------------------
        summary = str(model_output.get("summary", "")).strip()

        # ------------------------------------------------------------
        # Normalização de evidence_snippets
        # ------------------------------------------------------------
        raw_evidence = model_output.get("evidence_snippets", [])
        normalized_evidence: List[EvidenceSnippet] = []

        if isinstance(raw_evidence, list):
            for item in raw_evidence:
                if not isinstance(item, dict):
                    continue

                label = str(item.get("label", "")).strip()
                snippet = str(item.get("snippet", "")).strip()
                explanation = str(item.get("explanation", "")).strip()

                # Só adicionamos a evidência se houver pelo menos algum conteúdo útil
                if label or snippet or explanation:
                    normalized_evidence.append(
                        EvidenceSnippet(
                            label=label or "outros_indicios",
                            snippet=snippet,
                            explanation=explanation,
                        )
                    )

        # ------------------------------------------------------------
        # Retorno final padronizado
        # ------------------------------------------------------------
        return AnalysisResult(
            labels=normalized_labels,
            risk_score=risk_score,
            severity=severity,
            summary=summary,
            evidence_snippets=normalized_evidence,
            model_version="gaia-mvp-v1",
        )