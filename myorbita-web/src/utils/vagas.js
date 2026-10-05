// Helpers de apresentação de vagas, compartilhados por Home, lista e detalhe.

const VALORES_AUSENTES = new Set(["", "Não informado"]);

export const estaAusente = (valor) => {
  if (!valor) return true;
  return VALORES_AUSENTES.has(String(valor).trim());
};

const DIA_MS = 1000 * 60 * 60 * 24;

export function formatarData(iso) {
  if (!iso) return "—";
  const data = new Date(iso);
  if (isNaN(data.getTime())) return iso;
  return data.toLocaleDateString("pt-BR");
}

/** Situação do prazo de inscrição: { estado: "expirada" | "proxima" | "aberta", texto } */
export function statusPrazo(prazoIso) {
  if (!prazoIso) return null;
  const prazo = new Date(prazoIso);
  if (isNaN(prazo.getTime())) return null;
  const dias = Math.ceil((prazo.getTime() - Date.now()) / DIA_MS);
  if (dias < 0) return { estado: "expirada", texto: "Expirada" };
  if (dias <= 7) {
    const s = dias !== 1 ? "s" : "";
    return { estado: "proxima", texto: `${dias} dia${s} restante${s}` };
  }
  return { estado: "aberta", texto: formatarData(prazoIso) };
}

export function formatarTempoRelativo(timestamp) {
  if (!timestamp) return "";
  const diffMin = Math.floor((Date.now() - timestamp) / 60000);
  if (diffMin < 1) return "agora mesmo";
  if (diffMin < 60) return `há ${diffMin} min`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `há ${diffH} h`;
  return `há ${Math.floor(diffH / 24)} d`;
}

/** Sempre retorna { texto, ausente }; quem chama decide a renderização. */
export function formatarLocalizacao(city, state) {
  const cityValido = !estaAusente(city);
  const stateValido = !estaAusente(state);
  if (!cityValido && !stateValido) return { texto: "Local não informado", ausente: true };
  if (cityValido && stateValido) return { texto: `${city}, ${state}`, ausente: false };
  return { texto: cityValido ? city : state, ausente: false };
}

function inicioDoDia(data) {
  const d = new Date(data);
  d.setHours(0, 0, 0, 0);
  return d.getTime();
}

/** Chave e rótulo da faixa diária de uma vaga, pela data de publicação. */
export function faixaDoDia(iso) {
  if (!iso) return { chave: "sem-data", rotulo: "Sem data de publicação" };
  const data = new Date(iso);
  if (isNaN(data.getTime())) return { chave: "sem-data", rotulo: "Sem data de publicação" };
  const dias = Math.round((inicioDoDia(Date.now()) - inicioDoDia(data)) / DIA_MS);
  const chave = String(inicioDoDia(data));
  if (dias <= 0) return { chave, rotulo: "Publicadas hoje" };
  if (dias === 1) return { chave, rotulo: "Publicadas ontem" };
  return {
    chave,
    rotulo: `Publicadas em ${data.toLocaleDateString("pt-BR", { day: "numeric", month: "long" })}`,
  };
}

/** Agrupa uma lista já ordenada em faixas contíguas por dia de publicação. */
export function agruparPorDia(vagas) {
  const faixas = [];
  for (const vaga of vagas) {
    const { chave, rotulo } = faixaDoDia(vaga.data_publicacao);
    const ultima = faixas[faixas.length - 1];
    if (ultima && ultima.chave === chave) ultima.vagas.push(vaga);
    else faixas.push({ chave, rotulo, vagas: [vaga] });
  }
  return faixas;
}

export function publicadaNasUltimas24h(vaga) {
  if (!vaga.data_publicacao) return false;
  const t = new Date(vaga.data_publicacao).getTime();
  return !isNaN(t) && Date.now() - t <= DIA_MS;
}
