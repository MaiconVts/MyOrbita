import { useRef } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { AREAS, MODALIDADES } from "../../../config/areas";
import { DUR, EASE_GSAP } from "../../../constants/motion";
import { useRevelar, revelarEmSequencia } from "../../../hooks/useRevelar";
import CabecaSecao from "./CabecaSecao";

// Remoto acende a luz da área; híbrido e presencial ficam em tons de apoio.
const COR_SEGMENTO = {
  Remoto: "var(--luz)",
  Híbrido: "color-mix(in oklch, var(--luz) 45%, var(--color-tinta-fraca))",
  Presencial: "var(--color-tinta-fraca)",
};

function Orbita() {
  return (
    <svg className="rota__orbita" viewBox="-100 -100 200 200" aria-hidden="true" data-efeito="grade">
      <g className="rota__orbita-giro">
        <circle className="rota__trilha rota__trilha--fraca" r="92" />
        <circle className="rota__trilha rota__trilha--fraca" r="64" />
        <ellipse className="rota__trilha rota__trilha--fraca" rx="96" ry="38" transform="rotate(-24)" />
        <path
          className="rota__trilha rota__trilha--forte"
          d="M -64 0 A 64 64 0 1 1 45.25 45.25"
          pathLength="1"
          data-trilha
        />
        <circle className="rota__planeta-halo" cx="45.25" cy="45.25" r="9" />
        <circle className="rota__planeta" cx="45.25" cy="45.25" r="3.5" />
        <circle className="rota__planeta" r="14" opacity="0.9" />
        <circle className="rota__planeta-halo" r="26" />
      </g>
    </svg>
  );
}

function Rota({ area, dados, carregando }) {
  const total = dados.total;
  const comModalidade = MODALIDADES.reduce((s, m) => s + dados.porModalidade[m], 0);

  return (
    <Link to={area.caminho} className={`placa rota rota--${area.chave} luz-${area.luz}`} data-rota>
      <span className="rota__luz" aria-hidden="true" data-efeito="glow" />
      <Orbita />

      <div>
        <p className="voz-rotulo">{area.titulo}</p>
        <h3 className="rota__nome">{area.nome}</h3>
        <p className="rota__sub">{area.subtitulo}</p>
      </div>

      <div className="rota__contagem">
        <span className="rota__numero voz-coordenada">
          {carregando ? (
            <span className="esqueleto" style={{ width: "2.5ch", height: "0.8em" }} aria-hidden="true" />
          ) : (
            <span data-contar={total}>{total.toLocaleString("pt-BR")}</span>
          )}
        </span>
        <span className="rota__legenda">
          {carregando ? "Contando vagas…" : `vagas abertas · +${dados.recentes.toLocaleString("pt-BR")} nas últimas 24 h`}
        </span>
      </div>

      <div className="rota__distribuicao">
        <div className="rota__barra" aria-hidden="true">
          {!carregando &&
            comModalidade > 0 &&
            MODALIDADES.map((m) =>
              dados.porModalidade[m] > 0 ? (
                <span
                  key={m}
                  data-segmento
                  style={{ flex: dados.porModalidade[m], "--seg": COR_SEGMENTO[m] }}
                />
              ) : null,
            )}
        </div>
        <ul className="rota__modalidades">
          {MODALIDADES.map((m) => (
            <li key={m} style={{ "--seg": COR_SEGMENTO[m] }}>
              {m} <b>{carregando ? "–" : dados.porModalidade[m].toLocaleString("pt-BR")}</b>
            </li>
          ))}
        </ul>
      </div>

      <span className="rota__ir">
        Abrir {area.titulo} <ArrowUpRight size={18} strokeWidth={1.75} aria-hidden="true" />
      </span>
    </Link>
  );
}

export default function Rotas({ resumo }) {
  const ref = useRef(null);
  const { carregando, areas } = resumo;

  useRevelar(
    ref,
    (gsap, q) => {
      revelarEmSequencia(gsap, q("[data-rota]"), ref.current, { y: 48 });

      // A órbita forte se desenha conforme a seção atravessa a tela.
      gsap.fromTo(
        q("[data-trilha]"),
        { strokeDasharray: 1, strokeDashoffset: 1 },
        {
          strokeDashoffset: 0.08,
          ease: "none",
          scrollTrigger: { trigger: ref.current, start: "top 85%", end: "center 40%", scrub: 0.6 },
        },
      );

      if (carregando) return;

      // Contagem sobe uma vez, ao entrar na tela.
      q("[data-contar]").forEach((el) => {
        const alvo = Number(el.dataset.contar);
        const estado = { v: 0 };
        gsap.to(estado, {
          v: alvo,
          duration: DUR.lenta * 2.2,
          ease: EASE_GSAP,
          scrollTrigger: { trigger: el, start: "top 90%", once: true },
          onUpdate: () => (el.textContent = Math.round(estado.v).toLocaleString("pt-BR")),
        });
      });

      gsap.from(q("[data-segmento]"), {
        scaleX: 0,
        duration: DUR.lenta * 1.4,
        ease: EASE_GSAP,
        stagger: 0.12,
        scrollTrigger: { trigger: ref.current, start: "top 70%", once: true },
      });
    },
    [carregando],
  );

  return (
    <section className="secao" id="rotas" ref={ref} aria-labelledby="rotas-titulo">
      <div className="envelope">
        <CabecaSecao
          id="rotas-titulo"
          titulo="Duas áreas, um mapa só."
          texto="Tecnologia e direito, cada uma com a sua luz. Os números abaixo vêm da coleta de hoje e mostram quantas vagas estão no ar e como se dividem entre remoto, híbrido e presencial."
        />
        <div className="rotas">
          <Rota area={AREAS.dev} dados={areas.dev} carregando={carregando} />
          <Rota area={AREAS.adv} dados={areas.adv} carregando={carregando} />
        </div>
      </div>
    </section>
  );
}
