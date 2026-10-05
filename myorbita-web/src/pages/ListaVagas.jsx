import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  MapPin,
  GraduationCap,
  Briefcase,
  Accessibility,
  X,
  SlidersHorizontal,
  Layers,
  RefreshCw,
  AlertCircle,
  CalendarClock,
  ArrowRight,
  ArrowDownUp,
} from "lucide-react";
import PageTransition from "../components/PageTransition";
import FiltroMultiSelect from "../components/FiltroMultiSelect";
import { useFiltrosVagas } from "../hooks/useFiltrosVagas";
import { useCacheVagas } from "../hooks/useCacheVagas";
import { rolarAte } from "../hooks/useRolagemSuave";
import { OPCOES_NIVEL, MODALIDADES, luzDaModalidade } from "../config/areas";
import { SITE } from "../config/site";
import {
  estaAusente,
  formatarData,
  statusPrazo,
  formatarTempoRelativo,
  formatarLocalizacao,
  agruparPorDia,
  publicadaNasUltimas24h,
} from "../utils/vagas";

const VagaDetalhe = lazy(() => import("../components/VagaDetalhe"));

const LUZ_ORIGEM = { LinkedIn: "linkedin" };
const ORDENACOES = new Set(["recente", "antiga"]);

// Filtros na URL: a busca pode ser compartilhada e sobrevive ao recarregar.
const PARAMS_LISTA = {
  modalidade: "modalidade",
  nivel: "nivel",
  estado: "estado",
  contrato: "contrato",
  origem: "origem",
};

function lerFiltrosDaUrl(params) {
  const lista = (chave) => params.get(chave)?.split(",").filter(Boolean) ?? [];
  const ordem = params.get("ordem");
  return {
    busca: params.get("q") ?? "",
    ordenacao: ORDENACOES.has(ordem) ? ordem : "recente",
    modalidade: lista("modalidade"),
    nivel: lista("nivel"),
    estado: lista("estado"),
    contrato: lista("contrato"),
    origem: lista("origem"),
    pcd: params.get("pcd") === "1",
  };
}

/*
 * "Nova" marca o que entrou desde a última visita a esta área. Na primeira
 * visita, vale o recorte das últimas 24 h. Sem armazenamento, só o recorte.
 */
function useUltimaVisita(chave) {
  const [anterior] = useState(() => {
    try {
      const salvo = Number(localStorage.getItem(`myorbita:visita:${chave}`));
      return Number.isFinite(salvo) && salvo > 0 ? salvo : null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(`myorbita:visita:${chave}`, String(Date.now()));
    } catch {
      /* armazenamento indisponível: segue sem lembrar a visita */
    }
  }, [chave]);

  return (vaga) => {
    if (!anterior) return publicadaNasUltimas24h(vaga);
    const t = new Date(vaga.data_publicacao).getTime();
    return !isNaN(t) && t > anterior;
  };
}

function textoPrazo(prazo) {
  if (prazo.estado === "aberta") return `até ${prazo.texto}`;
  return prazo.texto;
}

function CartaoVaga({ vaga, area, nova, onAbrir }) {
  const modalidadeAusente = estaAusente(vaga.modalidade);
  const contratoAusente = estaAusente(vaga.tipo_contrato);
  const localizacao = formatarLocalizacao(vaga.city, vaga.state);
  const prazo = vaga.prazo_inscricao && !estaAusente(vaga.prazo_inscricao) ? statusPrazo(vaga.prazo_inscricao) : null;

  return (
    <article className={`placa vaga${nova ? " vaga--nova" : ""}`}>
      <div className="vaga__topo">
        {nova && <span className="selo selo--nova">Nova</span>}
        {modalidadeAusente ? (
          <span className="selo selo--ausente" title="Modalidade não informada na vaga original">
            <AlertCircle size={12} aria-hidden="true" />
            Modalidade não informada
          </span>
        ) : (
          <span className={`selo luz-${luzDaModalidade(area, vaga.modalidade)}`}>{vaga.modalidade}</span>
        )}
        {vaga.origem && <span className={`selo luz-${LUZ_ORIGEM[vaga.origem] ?? "neutra"}`}>{vaga.origem}</span>}
      </div>

      <h3 className="vaga__titulo">
        <button type="button" className="vaga__abrir" onClick={onAbrir} aria-haspopup="dialog">
          {vaga.titulo}
        </button>
      </h3>
      <p className="vaga__empresa">{vaga.empresa}</p>

      <ul className="vaga__dados">
        <li
          className={localizacao.ausente ? "dado-ausente" : undefined}
          title={localizacao.ausente ? "Localização não informada na vaga original" : undefined}
        >
          {localizacao.ausente ? <AlertCircle size={14} aria-hidden="true" /> : <MapPin size={14} aria-hidden="true" />}
          {localizacao.texto}
        </li>
        <li
          className={contratoAusente ? "dado-ausente" : undefined}
          title={contratoAusente ? "Tipo de contrato não informado na vaga original" : undefined}
        >
          {contratoAusente ? <AlertCircle size={14} aria-hidden="true" /> : <Briefcase size={14} aria-hidden="true" />}
          {contratoAusente ? "Contrato não informado" : vaga.tipo_contrato}
        </li>
        {vaga.pcd && (
          <li>
            <Accessibility size={14} aria-hidden="true" />
            PCD
          </li>
        )}
      </ul>

      <div className="vaga__rodape">
        <span>
          <span className="so-leitor">Publicada em </span>
          {formatarData(vaga.data_publicacao)}
        </span>
        {prazo && (
          <span className={`selo selo--prazo-${prazo.estado}`}>
            <CalendarClock size={12} aria-hidden="true" />
            <span className="so-leitor">Inscrições: </span>
            {textoPrazo(prazo)}
          </span>
        )}
        <span className="vaga__ver" aria-hidden="true">
          Ver detalhes <ArrowRight size={13} />
        </span>
      </div>
    </article>
  );
}

function CartaoEsqueleto() {
  return (
    <li aria-hidden="true">
      <div className="placa vaga vaga--esqueleto">
        <span className="esqueleto" />
        <span className="esqueleto" />
        <span className="esqueleto" />
        <span className="esqueleto" />
      </div>
    </li>
  );
}

function OrbitaVazia() {
  return (
    <svg className="vazio__orbita" viewBox="-60 -60 120 120" aria-hidden="true">
      <circle className="vazio__trilha" r="52" />
      <ellipse rx="40" ry="16" transform="rotate(-24)" />
      <g className="vazio__giro">
        <circle cx="52" cy="0" r="4" fill="currentColor" />
      </g>
      <circle r="9" fill="currentColor" opacity="0.85" />
    </svg>
  );
}

export default function ListaVagas({ area }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [inicial] = useState(() => lerFiltrosDaUrl(searchParams));
  const [vagaSelecionada, setVagaSelecionada] = useState(null);
  const resultadosRef = useRef(null);
  const ehNova = useUltimaVisita(area.chave);

  const { vagas: vagasRaw, carregando, atualizando, atualizadoEm, recarregar, erro } = useCacheVagas(area.rotasFirebase);

  const {
    busca, setBusca,
    ordenacao, setOrdenacao,
    filtrosModalidade, setFiltrosModalidade,
    filtrosNivel, setFiltrosNivel,
    filtrosEstado, setFiltrosEstado,
    filtrosContrato, setFiltrosContrato,
    filtrosOrigem, setFiltrosOrigem,
    filtroPcd, setFiltroPcd,
    estadosDisponiveis,
    contratosDisponiveis,
    origensDisponiveis,
    paginaAtual, setPaginaAtual,
    vagasFiltradas, vagasPagina, totalPaginas, paginasVisiveis,
    filtrosAtivos, totalFiltrosAtivos, limparFiltros,
  } = useFiltrosVagas(vagasRaw, inicial);

  // No celular, plataforma, nível, estado, contrato e PCD ficam recolhidos para a lista aparecer antes.
  const [maisFiltros, setMaisFiltros] = useState(false);
  const extrasAtivos =
    [filtrosOrigem, filtrosNivel, filtrosEstado, filtrosContrato].filter((l) => l.length > 0).length +
    (filtroPcd ? 1 : 0);

  // Estado dos filtros → URL, sem empilhar histórico a cada tecla.
  useEffect(() => {
    const params = new URLSearchParams();
    if (busca.trim()) params.set("q", busca.trim());
    if (ordenacao !== "recente") params.set("ordem", ordenacao);
    const listas = {
      modalidade: filtrosModalidade,
      nivel: filtrosNivel,
      estado: filtrosEstado,
      contrato: filtrosContrato,
      origem: filtrosOrigem,
    };
    for (const [chave, valores] of Object.entries(listas)) {
      if (valores.length) params.set(PARAMS_LISTA[chave], valores.join(","));
    }
    if (filtroPcd) params.set("pcd", "1");
    setSearchParams(params, { replace: true });
  }, [busca, ordenacao, filtrosModalidade, filtrosNivel, filtrosEstado, filtrosContrato, filtrosOrigem, filtroPcd, setSearchParams]);

  const opcoesModalidade = useMemo(
    () => MODALIDADES.map((m) => ({ value: m, label: m, luz: luzDaModalidade(area, m) })),
    [area],
  );
  const opcoesEstado = estadosDisponiveis.map((uf) => ({ value: uf, label: uf }));
  const opcoesContrato = contratosDisponiveis.map((tipo) => ({ value: tipo, label: tipo }));
  const faixas = useMemo(() => agruparPorDia(vagasPagina), [vagasPagina]);

  const toggleOrigem = (origem) => {
    if (filtrosOrigem.includes(origem)) setFiltrosOrigem(filtrosOrigem.filter((o) => o !== origem));
    else setFiltrosOrigem([...filtrosOrigem, origem]);
  };

  const irParaPagina = (p) => {
    setPaginaAtual(p);
    rolarAte(resultadosRef.current);
  };

  const total = vagasFiltradas.length;
  const canonica = `${SITE.url}${area.caminho}`;

  return (
    <PageTransition>
      <title>{area.seo.titulo}</title>
      <meta name="description" content={area.seo.descricao} />
      <link rel="canonical" href={canonica} />
      <meta property="og:title" content={area.seo.titulo} />
      <meta property="og:description" content={area.seo.descricao} />
      <meta property="og:url" content={canonica} />

      <div className={`envelope lista luz-${area.luz}`}>
        <header className="lista__cabeca">
          <span className="lista__luz" aria-hidden="true" data-efeito="glow" />
          <div>
            <h1 className="lista__titulo subir" style={{ "--ordem": 0 }}>
              {area.titulo}
            </h1>
            <p className="lista__sub voz-coordenada subir" style={{ "--ordem": 1 }}>
              {area.subtitulo}
            </p>
            <p className="lista__contador subir" style={{ "--ordem": 2 }}>
              {carregando ? (
                "Carregando vagas..."
              ) : (
                <>
                  <strong>{total.toLocaleString("pt-BR")}</strong> vagas disponíveis agora
                </>
              )}
            </p>
          </div>
          <svg className="lista__orbita" viewBox="-60 -60 120 120" aria-hidden="true" data-efeito="parallax">
            <ellipse rx="54" ry="22" transform="rotate(-20)" opacity="0.35" />
            <ellipse rx="34" ry="13" transform="rotate(-20)" opacity="0.6" />
            <g className="lista__orbita-giro">
              <circle cx="54" cy="0" r="3.5" fill="currentColor" />
            </g>
            <circle r="10" fill="currentColor" />
          </svg>
        </header>

        <section className="placa filtros" aria-labelledby="filtros-titulo" data-efeito="vidro">
          <div className="filtros__topo">
            <h2 className="filtros__titulo" id="filtros-titulo">
              <SlidersHorizontal size={16} strokeWidth={1.75} aria-hidden="true" />
              Filtros
              {totalFiltrosAtivos > 0 && (
                <span className="filtros__ativos">
                  {totalFiltrosAtivos} {totalFiltrosAtivos === 1 ? "ativo" : "ativos"}
                </span>
              )}
            </h2>
            {!carregando && (
              <div className="filtros__meta">
                {atualizadoEm && <span>Atualizado {formatarTempoRelativo(atualizadoEm)}</span>}
                <button
                  type="button"
                  className="botao-texto"
                  onClick={recarregar}
                  disabled={atualizando}
                  title="Buscar vagas atualizadas no Firebase"
                >
                  <RefreshCw size={14} className={atualizando ? "giro" : undefined} aria-hidden="true" />
                  Atualizar
                </button>
                {totalFiltrosAtivos > 0 && (
                  <button type="button" className="botao-texto" onClick={limparFiltros}>
                    <X size={14} aria-hidden="true" />
                    Limpar filtros
                  </button>
                )}
              </div>
            )}
          </div>

          <div className="filtros__linha">
            <label className="campo">
              <span className="so-leitor">Buscar por cargo, empresa ou palavra-chave</span>
              <Search size={16} className="campo__icone" aria-hidden="true" />
              <input
                type="search"
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                placeholder={area.placeholderBusca}
                autoComplete="off"
              />
            </label>
            <FiltroMultiSelect
              icone={<Layers size={15} />}
              placeholder="Modalidade"
              opcoes={opcoesModalidade}
              selecionados={filtrosModalidade}
              onChange={setFiltrosModalidade}
              luz={area.luz}
            />
            <label className="campo">
              <span className="so-leitor">Ordenar por data</span>
              <ArrowDownUp size={16} className="campo__icone" aria-hidden="true" />
              <select value={ordenacao} onChange={(e) => setOrdenacao(e.target.value)}>
                <option value="recente">Mais recentes</option>
                <option value="antiga">Mais antigas</option>
              </select>
              <ChevronDown size={14} className="campo__seta" aria-hidden="true" />
            </label>
          </div>

          <button
            type="button"
            className="botao-texto filtros__mais"
            aria-expanded={maisFiltros}
            aria-controls="filtros-extra"
            onClick={() => setMaisFiltros(!maisFiltros)}
          >
            <ChevronDown size={14} className="filtros__mais-seta" aria-hidden="true" />
            {maisFiltros ? "Menos filtros" : "Mais filtros"}
            {extrasAtivos > 0 && <span className="filtros__ativos">{extrasAtivos}</span>}
          </button>

          <div className="filtros__extra" id="filtros-extra" data-aberto={maisFiltros || undefined}>
            {origensDisponiveis.length > 0 && (
              <div className="filtros__origens" role="group" aria-labelledby="filtro-plataforma">
                <span className="voz-rotulo" id="filtro-plataforma">
                  Plataforma
                </span>
                {origensDisponiveis.map((origem) => {
                  const ativo = filtrosOrigem.includes(origem);
                  return (
                    <button
                      key={origem}
                      type="button"
                      className={`alternador luz-${LUZ_ORIGEM[origem] ?? "neutra"}`}
                      aria-pressed={ativo}
                      onClick={() => toggleOrigem(origem)}
                      title={ativo ? `Remover filtro do ${origem}` : `Adicionar vagas do ${origem}`}
                    >
                      <span className="alternador__ponto" aria-hidden="true" />
                      {origem}
                    </button>
                  );
                })}
                <span className="filtros__dica">
                  {filtrosOrigem.length > 0
                    ? `${filtrosOrigem.length} ${filtrosOrigem.length === 1 ? "selecionada" : "selecionadas"}`
                    : "Nenhum filtro = todas as plataformas"}
                </span>
              </div>
            )}

            <div className="filtros__grade">
              <FiltroMultiSelect
                icone={<GraduationCap size={15} />}
                placeholder="Qualquer Nível"
                opcoes={OPCOES_NIVEL}
                selecionados={filtrosNivel}
                onChange={setFiltrosNivel}
                luz={area.luz}
              />
              <FiltroMultiSelect
                icone={<MapPin size={14} />}
                placeholder="Qualquer Estado"
                opcoes={opcoesEstado}
                selecionados={filtrosEstado}
                onChange={setFiltrosEstado}
                luz={area.luz}
              />
              <FiltroMultiSelect
                icone={<Briefcase size={14} />}
                placeholder="Qualquer Contrato"
                opcoes={opcoesContrato}
                selecionados={filtrosContrato}
                onChange={setFiltrosContrato}
                luz={area.luz}
              />
              <button
                type="button"
                className={`alternador luz-${area.luz}`}
                aria-pressed={filtroPcd}
                onClick={() => setFiltroPcd(!filtroPcd)}
              >
                <Accessibility size={14} aria-hidden="true" />
                PCD
              </button>
            </div>
          </div>

          {totalFiltrosAtivos > 0 && (
            <div className="filtros__chips" aria-label="Filtros ativos" role="group">
              {filtrosAtivos.map((filtro, i) => (
                <button
                  key={`${filtro.nome}-${i}`}
                  type="button"
                  className="chip"
                  onClick={filtro.limpar}
                  title="Clique para remover este filtro"
                >
                  {filtro.nome}
                  <X size={12} aria-hidden="true" />
                </button>
              ))}
            </div>
          )}
        </section>

        <p className="so-leitor" aria-live="polite">
          {carregando ? "" : `${total} ${total === 1 ? "vaga encontrada" : "vagas encontradas"}`}
        </p>

        <div ref={resultadosRef} aria-busy={carregando}>
          {carregando && (
            <ul className="grade-vagas" aria-label="Carregando vagas">
              {Array.from({ length: 6 }, (_, i) => (
                <CartaoEsqueleto key={i} />
              ))}
            </ul>
          )}

          {!carregando && total === 0 && (
            <div className="vazio">
              <OrbitaVazia />
              <h2 className="vazio__titulo">
                {erro && !vagasRaw.length ? "Não foi possível carregar as vagas" : "Nenhuma vaga atende aos filtros"}
              </h2>
              {totalFiltrosAtivos > 0 ? (
                <>
                  <p className="vazio__texto">
                    Você tem {totalFiltrosAtivos} {totalFiltrosAtivos === 1 ? "filtro ativo" : "filtros ativos"}. Tente
                    remover {totalFiltrosAtivos === 1 ? "ele" : "alguns"} para ver mais resultados.
                  </p>
                  <div className="vazio__chips">
                    {filtrosAtivos.map((filtro, i) => (
                      <button key={`${filtro.nome}-${i}`} type="button" className="chip" onClick={filtro.limpar}>
                        Remover: <strong>{filtro.nome}</strong>
                        <X size={12} aria-hidden="true" />
                      </button>
                    ))}
                  </div>
                  <button type="button" className="botao botao--rota" onClick={limparFiltros}>
                    Limpar todos os filtros
                  </button>
                </>
              ) : erro && !vagasRaw.length ? (
                <>
                  <p className="vazio__texto">A conexão com a base de vagas falhou. Tente de novo em instantes.</p>
                  <button type="button" className="botao botao--rota" onClick={recarregar}>
                    <RefreshCw size={14} aria-hidden="true" />
                    Tentar de novo
                  </button>
                </>
              ) : (
                <p className="vazio__texto">As vagas ainda estão sendo coletadas. Tente novamente em alguns minutos.</p>
              )}
            </div>
          )}

          {!carregando &&
            faixas.map((faixa) => (
              <section key={faixa.chave} className="faixa" aria-labelledby={`faixa-${faixa.chave}`}>
                <div className="faixa__cabeca">
                  <h2 className="faixa__rotulo" id={`faixa-${faixa.chave}`}>
                    {faixa.rotulo}
                    <span>
                      {faixa.vagas.length} {faixa.vagas.length === 1 ? "vaga" : "vagas"}
                    </span>
                  </h2>
                </div>
                <ul className="grade-vagas">
                  {faixa.vagas.map((vaga) => (
                    <li key={vaga.id ?? vaga.link}>
                      <CartaoVaga
                        vaga={vaga}
                        area={area}
                        nova={ehNova(vaga)}
                        onAbrir={() => setVagaSelecionada(vaga)}
                      />
                    </li>
                  ))}
                </ul>
              </section>
            ))}
        </div>

        {!carregando && totalPaginas > 1 && (
          <nav className="paginacao" aria-label="Páginas de resultados">
            <button
              type="button"
              className="paginacao__botao"
              onClick={() => irParaPagina(Math.max(1, paginaAtual - 1))}
              disabled={paginaAtual === 1}
              aria-label="Página anterior"
            >
              <ChevronLeft size={18} aria-hidden="true" />
            </button>
            {paginasVisiveis().map((p) => (
              <button
                key={p}
                type="button"
                className="paginacao__botao"
                onClick={() => irParaPagina(p)}
                aria-current={paginaAtual === p ? "page" : undefined}
                aria-label={`Página ${p}`}
              >
                {p}
              </button>
            ))}
            <button
              type="button"
              className="paginacao__botao"
              onClick={() => irParaPagina(Math.min(totalPaginas, paginaAtual + 1))}
              disabled={paginaAtual === totalPaginas}
              aria-label="Próxima página"
            >
              <ChevronRight size={18} aria-hidden="true" />
            </button>
          </nav>
        )}

        {!carregando && (
          <div className="lista__rodape">
            <p className="voz-margem">Atualizado via Gupy + LinkedIn</p>
            <p className="lista__total">
              <span className="painel__pulso" aria-hidden="true" />
              {total} {total === 1 ? "vaga encontrada" : "vagas encontradas"}
            </p>
          </div>
        )}
      </div>

      {vagaSelecionada && (
        <Suspense fallback={null}>
          <VagaDetalhe
            vaga={vagaSelecionada}
            luz={luzDaModalidade(area, vagaSelecionada.modalidade)}
            onClose={() => setVagaSelecionada(null)}
          />
        </Suspense>
      )}
    </PageTransition>
  );
}
