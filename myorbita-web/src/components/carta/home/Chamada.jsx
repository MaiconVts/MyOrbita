import { useRef } from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { AREAS } from "../../../config/areas";
import { useRevelar, revelarEmSequencia } from "../../../hooks/useRevelar";

export default function Chamada({ total, carregando }) {
  const ref = useRef(null);

  useRevelar(ref, (gsap, q) => {
    revelarEmSequencia(gsap, q(".chamada > :not(.chamada__luz)"), ref.current);
    gsap.from(q(".chamada__luz"), {
      scale: 0.6,
      opacity: 0,
      ease: "none",
      scrollTrigger: { trigger: ref.current, start: "top bottom", end: "center center", scrub: true },
    });
  });

  return (
    <section className="secao" ref={ref} aria-labelledby="chamada-titulo">
      <div className="envelope">
        <div className="placa chamada" data-efeito="vidro">
          <span className="chamada__luz" aria-hidden="true" data-efeito="glow" />
          <p className="voz-coordenada secao__marcador">Próxima parada</p>
          <h2 className="chamada__titulo" id="chamada-titulo">
            {carregando || !total
              ? "Escolha a sua rota e comece a buscar."
              : `${total.toLocaleString("pt-BR")} vagas esperando a sua busca.`}
          </h2>
          <div className="chamada__acoes">
            <Link to={AREAS.dev.caminho} className="botao botao--tech botao--grande">
              Ver vagas Dev <ArrowRight size={18} strokeWidth={1.75} aria-hidden="true" />
            </Link>
            <Link to={AREAS.adv.caminho} className="botao botao--rota botao--grande">
              Ver vagas Jurídico <ArrowRight size={18} strokeWidth={1.75} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
