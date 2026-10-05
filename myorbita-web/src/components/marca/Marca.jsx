import { useId } from "react";
import { useReduzMovimento } from "../../hooks/useReduzMovimento";

/*
 * Marca MyOrbita: "My" leve + "Orbita" pesado em Unbounded, com um anel
 * orbital inclinado em volta do O. A metade de trás do anel passa atrás da
 * letra e a da frente por cima; o satélite troca de camada no meio da volta,
 * então ele some de fato atrás do O. Geometria igual à do banner do README
 * (tools/banner/gen_banner.py): anel 1,62 × raio do O, achatado em 0,42, −16°.
 */
const R_O = 42; // raio aproximado do O no viewBox (-100..100)
const RX = R_O * 1.62;
const RY = R_O * 0.42;
const INCLINACAO = -16;
// SMIL não lê variáveis CSS; espelha --dur-satelite de tokens.css.
const DUR_SATELITE = "9s";

const TRAS = `M${-RX} 0A${RX} ${RY} 0 0 1 ${RX} 0`;
const FRENTE = `M${RX} 0A${RX} ${RY} 0 0 1 ${-RX} 0`;
// Começa em (+RX, 0) e desce pela frente na primeira metade da volta.
const VOLTA = `M${RX} 0A${RX} ${RY} 0 1 1 ${-RX} 0A${RX} ${RY} 0 1 1 ${RX} 0`;

function Satelite({ id, camada, animado }) {
  if (!animado) {
    // Parado na frente, à direita, como no banner estático.
    return camada === "frente" ? (
      <g transform={`translate(${RX * 0.62} ${RY * 0.78})`}>
        <circle r="9" fill={`url(#${id}-sat)`} />
        <circle r="2.8" className="marca__satelite-nucleo" />
      </g>
    ) : null;
  }
  return (
    <g opacity={camada === "frente" ? 1 : 0}>
      <animate
        attributeName="opacity"
        values={camada === "frente" ? "1;0" : "0;1"}
        keyTimes="0;0.5"
        calcMode="discrete"
        dur={DUR_SATELITE}
        begin="0s"
        repeatCount="indefinite"
      />
      <animateMotion dur={DUR_SATELITE} repeatCount="indefinite" path={VOLTA} />
      <circle r="9" fill={`url(#${id}-sat)`} />
      <circle r="2.8" className="marca__satelite-nucleo" />
    </g>
  );
}

function Anel({ id, camada, animado }) {
  return (
    <svg
      className={`marca__anel marca__anel--${camada}`}
      viewBox="-100 -100 200 200"
      aria-hidden="true"
      focusable="false"
    >
      {camada === "tras" && (
        <defs>
          <linearGradient id={`${id}-anel`} gradientUnits="userSpaceOnUse" x1={-RX} x2={RX}>
            <stop offset="0" className="marca__anel-borda" />
            <stop offset="0.5" className="marca__anel-meio" />
            <stop offset="1" className="marca__anel-fim" />
          </linearGradient>
          <radialGradient id={`${id}-sat`}>
            <stop offset="0" className="marca__sat-0" />
            <stop offset="0.3" className="marca__sat-1" />
            <stop offset="1" className="marca__sat-2" />
          </radialGradient>
        </defs>
      )}
      <g transform={`rotate(${INCLINACAO})`}>
        <path
          className="marca__traco"
          d={camada === "tras" ? TRAS : FRENTE}
          pathLength="1"
          stroke={`url(#${id}-anel)`}
        />
        <Satelite id={id} camada={camada} animado={animado} />
      </g>
    </svg>
  );
}

/**
 * @param {"header"|"hero"|"rodape"} variante tamanho e coreografia de entrada
 */
export default function Marca({ variante = "header", className = "" }) {
  const id = useId().replace(/:/g, "");
  const reduz = useReduzMovimento();
  const animado = !reduz;

  return (
    <span className={`marca marca--${variante} ${className}`} role="img" aria-label="MyOrbita">
      <span className="marca__my" aria-hidden="true">My</span>
      <span className="marca__orbita" aria-hidden="true">
        <span className="marca__o">
          <Anel id={id} camada="tras" animado={animado} />
          <span className="marca__o-letra">O</span>
          <Anel id={id} camada="frente" animado={animado} />
        </span>
        rbita
      </span>
    </span>
  );
}
