import { useRef } from "react";
import { ETAPAS, HORARIOS } from "../../../config/comoFunciona";
import { ICONES_ETAPA } from "../iconesEtapa";
import { useRevelar, revelarEmSequencia } from "../../../hooks/useRevelar";
import CabecaSecao from "./CabecaSecao";

export default function Trajeto() {
  const ref = useRef(null);

  useRevelar(ref, (gsap, q) => {
    revelarEmSequencia(gsap, q("[data-cabeca] > *"), ref.current);
    // A linha liga as estações conforme a seção sobe; cada estação acende na passagem.
    gsap.fromTo(
      q("[data-linha]"),
      { strokeDasharray: 1, strokeDashoffset: 1 },
      {
        strokeDashoffset: 0,
        ease: "none",
        scrollTrigger: { trigger: q(".trajeto__mapa")[0], start: "top 80%", end: "bottom 55%", scrub: 0.6 },
      },
    );
    revelarEmSequencia(gsap, q(".estacao"), q(".trajeto")[0], { stagger: 0.14 });
    revelarEmSequencia(gsap, q(".horarios"), q(".horarios")[0], { y: 16 });
  });

  return (
    <section className="secao" ref={ref} aria-labelledby="trajeto-titulo">
      <div className="envelope">
        <CabecaSecao
          marcador="03 · Como funciona"
          id="trajeto-titulo"
          titulo="Da coleta diária até a sua tela."
          texto="Quatro estações, todo dia. Robôs coletam as vagas nas fontes, removem repetições, guardam tudo organizado e entregam aqui com filtros que rodam no seu navegador."
        />

        <div className="trajeto__mapa">
          <svg className="trajeto__linha" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">
            <path className="trajeto__linha-base" d="M 6 0 C 30 9, 45 9, 50 5 S 75 -2, 94 4" />
            <path d="M 6 0 C 30 9, 45 9, 50 5 S 75 -2, 94 4" pathLength="1" data-linha />
          </svg>
          <ol className="trajeto">
          {ETAPAS.map((etapa, i) => {
            const Icone = ICONES_ETAPA[etapa.icone];
            return (
              <li key={etapa.titulo} className="estacao">
                <span className="estacao__astro" aria-hidden="true">
                  <Icone size={22} strokeWidth={1.5} />
                </span>
                <span className="estacao__numero voz-coordenada">Estação {String(i + 1).padStart(2, "0")}</span>
                <h3 className="estacao__titulo">{etapa.titulo}</h3>
                <p className="estacao__texto">{etapa.texto}</p>
              </li>
            );
          })}
          </ol>
        </div>

        <div className="placa horarios" data-efeito="vidro">
          <p className="horarios__titulo">Horários da coleta diária</p>
          <dl>
            {HORARIOS.map(({ plataforma, horario }) => (
              <div key={plataforma}>
                <dt>{plataforma}</dt>
                <dd className="voz-coordenada">{horario}</dd>
              </div>
            ))}
          </dl>
          <p className="horarios__nota">Horário de Brasília · via GitHub Actions</p>
        </div>
      </div>
    </section>
  );
}
