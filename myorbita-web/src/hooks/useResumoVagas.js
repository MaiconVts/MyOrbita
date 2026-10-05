import { useMemo } from "react";
import { useCacheVagas } from "./useCacheVagas";
import { AREAS, MODALIDADES } from "../config/areas";
import { publicadaNasUltimas24h } from "../utils/vagas";

function tempo(vaga) {
  const t = vaga.data_publicacao ? new Date(vaga.data_publicacao).getTime() : NaN;
  return isNaN(t) ? 0 : t;
}

function resumir(vagas) {
  const porModalidade = Object.fromEntries(MODALIDADES.map((m) => [m, 0]));
  let semModalidade = 0;
  let recentes = 0;
  for (const vaga of vagas) {
    if (vaga.modalidade in porModalidade) porModalidade[vaga.modalidade] += 1;
    else semModalidade += 1;
    if (publicadaNasUltimas24h(vaga)) recentes += 1;
  }
  return { total: vagas.length, recentes, porModalidade, semModalidade };
}

/*
 * Números reais das duas áreas para a Home: total, publicadas nas últimas
 * 24 h, distribuição por modalidade e as vagas mais recentes das duas juntas.
 * Usa o mesmo cache local das listas, então abrir uma lista depois é imediato.
 */
export function useResumoVagas(quantasRecentes = 6) {
  const dev = useCacheVagas(AREAS.dev.rotasFirebase);
  const adv = useCacheVagas(AREAS.adv.rotasFirebase);

  return useMemo(() => {
    const carregando = dev.carregando || adv.carregando;
    const recentes = [
      ...dev.vagas.map((vaga) => ({ vaga, area: AREAS.dev })),
      ...adv.vagas.map((vaga) => ({ vaga, area: AREAS.adv })),
    ]
      .sort((a, b) => tempo(b.vaga) - tempo(a.vaga))
      .slice(0, quantasRecentes);

    const datas = [dev.atualizadoEm, adv.atualizadoEm].filter(Boolean);

    return {
      carregando,
      erro: dev.erro || adv.erro,
      areas: { dev: resumir(dev.vagas), adv: resumir(adv.vagas) },
      recentes,
      // A coleta mais antiga entre as duas é a que vale como "atualizado".
      atualizadoEm: datas.length ? Math.min(...datas) : null,
    };
  }, [dev, adv, quantasRecentes]);
}
