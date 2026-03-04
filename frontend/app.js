/**
 * Responsabilidade única: lógica do formulário e comunicação com a API.
 * - Coleta os dados do formulário
 * - Monta o payload no formato esperado pelo backend (sections + metadata)
 * - Mostra preview e envia via fetch
 *
 * Esse arquivo é intencionalmente simples para aprendizado.
 */

/**
 * Monta o payload a ser enviado ao backend.
 * Mantemos esse contrato estável para facilitar testes e integração.
 */
function buildPayloadFromForm() {
  return {
    sections: {
      queixa_principal: document.getElementById("chiefComplaint").value.trim(),
      anamnese: document.getElementById("anamnesis").value.trim(),
      evolucao: document.getElementById("evolution").value.trim(),
      observacoes: document.getElementById("observations").value.trim(),
      antecedentes: document.getElementById("background").value.trim(),
    },
    metadata: {
      age_group: document.getElementById("ageGroup").value || null,
      visit_type: document.getElementById("visitType").value || null,
      source: "frontend-form-v1"
    }
  };
}

/**
 * Atualiza o preview do JSON (apoio didático).
 */
function renderJsonPreview(obj) {
  document.getElementById("jsonPreview").textContent = JSON.stringify(obj, null, 2);
}

/**
 * Atualiza status na tela para feedback.
 */
function setStatus(msg) {
  document.getElementById("status").textContent = msg;
}

/**
 * Tenta enviar o payload ao backend.
 * Por padrão, usa o mesmo host/porta (ideal quando FastAPI servir os arquivos).
 */
async function sendToApi(payload) {
  const response = await fetch("/analyze_prontuario", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    // Lemos texto para facilitar depuração (didático)
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text}`);
  }

  return await response.json();
}

// --- Wire-up de eventos (código executado ao carregar a página) ---

document.getElementById("btnGenerate").addEventListener("click", () => {
  const payload = buildPayloadFromForm();
  renderJsonPreview(payload);
  setStatus("JSON atualizado (não enviado).");
});

document.getElementById("btnSend").addEventListener("click", async () => {
  const payload = buildPayloadFromForm();
  renderJsonPreview(payload);
  setStatus("Enviando para a API...");

  try {
    const result = await sendToApi(payload);
    setStatus("Sucesso! Resposta recebida da API.");
    renderJsonPreview(result);
  } catch (err) {
    setStatus("Falha ao conectar/enviar. A API já está rodando? " + err.message);
  }
});