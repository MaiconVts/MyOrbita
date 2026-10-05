import { useRef } from "react";
import { Link } from "react-router-dom";
import { m, useMotionValue, useSpring } from "framer-motion";
import { ArrowRight } from "lucide-react";
import Marca from "../../marca/Marca";
import { AREAS } from "../../../config/areas";
import { HORARIOS } from "../../../config/comoFunciona";
import { formatarTempoRelativo } from "../../../utils/vagas";
import { useReduzMovimento } from "../../../hooks/useReduzMovimento";
import { useRevelar } from "../../../hooks/useRevelar";

const MotionLink = m.create(Link);

// Atração do botão pelo cursor; só com mouse e sem movimento reduzido.
function BotaoMagnetico({ to, className, children }) {
  const reduz = useReduzMovimento();
  const x = useSpring(useMotionValue(0), { stiffness: 260, damping: 20, mass: 0.6 });
  const y = useSpring(useMotionValue(0), { stiffness: 260, damping: 20, mass: 0.6 });

  const mover = (e) => {
    if (reduz || !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
    const r = e.currentTarget.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * 0.22);
    y.set((e.clientY - (r.top + r.height / 2)) * 0.3);
  };
  const soltar = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <MotionLink to={to} className={className} style={{ x, y }} onPointerMove={mover} onPointerLeave={soltar}>
      {children}
    </MotionLink>
  );
}

function Numero({ valor, carregando }) {
  if (carregando) return <span className="esqueleto" style={{ width: "3ch" }} aria-hidden="true" />;
  return <span data-contar={valor}>{valor.toLocaleString("pt-BR")}</span>;
}

function PainelDeBordo({ resumo }) {
  const { carregando, areas, atualizadoEm } = resumo;
  const recentes = areas.dev.recentes + areas.adv.recentes;

  return (
    <aside className="placa painel" aria-label="Painel de bordo: vagas de hoje" data-efeito="vidro">
      <div className="painel__topo">
        <span className="voz-rotulo">Painel de bordo</span>
        <span className="painel__estado" aria-live="polite">
          <span className="painel__pulso" data-anima aria-hidden="true" />
          {carregando ? "Sincronizando…" : atualizadoEm ? `Atualizado ${formatarTempoRelativo(atualizadoEm)}` : "Ao vivo"}
        </span>
      </div>

      <ul className="painel__areas">
        {[AREAS.dev, AREAS.adv].map((area) => (
          <li key={area.chave} className={`painel__area luz-${area.luz}`}>
            <Link to={area.caminho}>
              <span className="painel__ponto" aria-hidden="true" />
              <span className="painel__nome">
                {area.nome}
                <small>{area.subtitulo}</small>
              </span>
              <span className="painel__numero voz-coordenada">
                <Numero valor={areas[area.chave].total} carregando={carregando} />
                <span className="so-leitor"> vagas</span>
              </span>
            </Link>
          </li>
        ))}
      </ul>

      <p className="painel__recentes">
        {carregando ? (
          <span className="esqueleto" style={{ width: "14ch" }} aria-hidden="true" />
        ) : (
          <>
            <strong className="voz-coordenada">+{recentes.toLocaleString("pt-BR")}</strong>
            publicadas nas últimas 24 h
          </>
        )}
      </p>

      <dl className="painel__coleta">
        {HORARIOS.map(({ plataforma, horario }) => (
          <div key={plataforma}>
            <dt>{plataforma}</dt>
            <dd className="voz-coordenada">{horario}</dd>
          </div>
        ))}
      </dl>
      <p className="painel__rodape voz-margem">Fonte: Gupy · LinkedIn · Atualizado diariamente</p>
    </aside>
  );
}

export default function Hero({ resumo }) {
  const ref = useRef(null);

  // Parallax em camadas: a luz desce devagar, o painel um pouco mais rápido
  // que o texto, para a carta ganhar profundidade ao rolar.
  useRevelar(ref, (gsap, q) => {
    const rolagem = { trigger: ref.current, start: "top top", end: "bottom top", scrub: true };
    gsap.to(q(".hero__luz"), { yPercent: 18, ease: "none", scrollTrigger: rolagem });
    gsap.to(q("[data-parallax='painel']"), { y: -60, ease: "none", scrollTrigger: { ...rolagem } });
    gsap.to(q("[data-parallax='texto']"), { y: 40, opacity: 0.35, ease: "none", scrollTrigger: { ...rolagem } });
  });

  return (
    <section className="hero" ref={ref} aria-labelledby="hero-titulo">
      <div className="hero__luz" aria-hidden="true" data-efeito="glow">
        <span className="hero__luz-tech" />
        <span className="hero__luz-roxa" />
      </div>

      <div className="envelope hero__grade">
        <div className="hero__texto" data-parallax="texto" data-efeito="parallax">
          <h1 className="hero__h1" id="hero-titulo">
            <Marca variante="hero" />
            <span className="hero__titulo subir" style={{ "--ordem": 2 }}>
              Vagas remotas em tecnologia e direito — atualizadas diariamente.
            </span>
          </h1>
          <p className="hero__lede subir" style={{ "--ordem": 3 }}>
            Todo dia, o MyOrbita coleta as vagas da Gupy e do LinkedIn e coloca tudo num só lugar,
            com filtros por modalidade, nível, estado e contrato. A candidatura acontece na página original.
          </p>
          <div className="hero__acoes subir" style={{ "--ordem": 4 }}>
            <BotaoMagnetico to="/vagas-dev" className="botao botao--tech botao--grande">
              Ver vagas Dev <ArrowRight size={18} strokeWidth={1.75} aria-hidden="true" />
            </BotaoMagnetico>
            <BotaoMagnetico to="/vagas-adv" className="botao botao--rota botao--grande">
              Ver vagas Jurídico <ArrowRight size={18} strokeWidth={1.75} aria-hidden="true" />
            </BotaoMagnetico>
          </div>
        </div>

        <div className="subir" style={{ "--ordem": 5 }}>
          <div data-parallax="painel">
            <PainelDeBordo resumo={resumo} />
          </div>
        </div>
      </div>

      <a href="#rotas" className="hero__rolar" aria-label="Rolar até as áreas">
        <span className="voz-rotulo">Rolar</span>
        <span className="hero__rolar-trilho" data-anima aria-hidden="true" />
      </a>
    </section>
  );
}
