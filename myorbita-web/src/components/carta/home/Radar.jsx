import { useRef } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { AREAS, luzDaModalidade } from "../../../config/areas";
import { faixaDoDia } from "../../../utils/vagas";
import { useRevelar, revelarEmSequencia } from "../../../hooks/useRevelar";
import CabecaSecao from "./CabecaSecao";

// "Publicadas hoje" vira "Hoje"; datas antigas ficam curtas ("2 de out.").
function quando(iso) {
  const { rotulo } = faixaDoDia(iso);
  if (rotulo === "Publicadas hoje") return "Hoje";
  if (rotulo === "Publicadas ontem") return "Ontem";
  const d = iso ? new Date(iso) : null;
  if (!d || isNaN(d.getTime())) return "Sem data";
  return d.toLocaleDateString("pt-BR", { day: "numeric", month: "short" });
}

function LinhaEsqueleto() {
  return (
    <li className="radar__item" aria-hidden="true">
      <div className="radar__linha">
        <span className="esqueleto" style={{ width: "4ch" }} />
        <span className="radar__corpo">
          <span className="esqueleto" style={{ width: "70%" }} />
          <span className="esqueleto" style={{ width: "35%", marginTop: "0.5em" }} />
        </span>
        <span className="esqueleto" style={{ width: "8ch" }} />
        <span />
      </div>
    </li>
  );
}

export default function Radar({ resumo, onAbrir }) {
  const ref = useRef(null);
  const { carregando, recentes, erro } = resumo;

  useRevelar(
    ref,
    (gsap, q) => {
      revelarEmSequencia(gsap, q("[data-cabeca] > *"), ref.current);
      if (!carregando) revelarEmSequencia(gsap, q(".radar__item"), q(".radar")[0], { y: 16, x: -12 });
    },
    [carregando],
  );

  return (
    <section className="secao" ref={ref} aria-labelledby="radar-titulo">
      <div className="envelope">
        <CabecaSecao
          id="radar-titulo"
          titulo="As últimas vagas que entraram na carta."
          texto="As publicações mais recentes das duas áreas, em ordem de chegada. Abra uma para ver os detalhes e seguir para a candidatura na página original."
        />

        <div className="placa radar" data-efeito="vidro">
          {erro && !recentes.length ? (
            <p className="radar__vazio">Não foi possível carregar as vagas agora. Tente de novo em instantes.</p>
          ) : (
            <ul className="radar__lista" aria-busy={carregando}>
              {carregando
                ? Array.from({ length: 6 }, (_, i) => <LinhaEsqueleto key={i} />)
                : recentes.map(({ vaga, area }) => {
                    const luz = luzDaModalidade(area, vaga.modalidade);
                    return (
                      <li key={`${area.chave}-${vaga.link ?? vaga.titulo}`} className={`radar__item luz-${area.luz}`}>
                        <button
                          type="button"
                          className="radar__linha"
                          onClick={() => onAbrir({ vaga, luz })}
                          aria-haspopup="dialog"
                        >
                          <span className="radar__quando voz-coordenada">{quando(vaga.data_publicacao)}</span>
                          <span className="radar__corpo">
                            <span className="radar__titulo">{vaga.titulo}</span>
                            <span className="radar__empresa">
                              {vaga.empresa}
                              {vaga.modalidade ? ` · ${vaga.modalidade}` : ""}
                            </span>
                          </span>
                          <span className="radar__area">{area.nome}</span>
                          <ArrowUpRight className="radar__seta" size={18} strokeWidth={1.75} aria-hidden="true" />
                        </button>
                      </li>
                    );
                  })}
            </ul>
          )}

          <div className="radar__rodape">
            <span className="voz-margem">Fonte: Gupy · LinkedIn</span>
            <span className="radar__links">
              <Link to={AREAS.dev.caminho} className="botao">
                Todas as vagas Dev
              </Link>
              <Link to={AREAS.adv.caminho} className="botao">
                Todas as vagas Jurídico
              </Link>
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
