import { useRef } from "react";
import { Plus } from "lucide-react";
import { useRevelar, revelarEmSequencia } from "../../../hooks/useRevelar";
import CabecaSecao from "./CabecaSecao";
import { PERGUNTAS } from "./perguntas";

export default function Faq() {
  const ref = useRef(null);

  useRevelar(ref, (gsap, q) => {
    revelarEmSequencia(gsap, q("[data-cabeca] > *"), ref.current);
    revelarEmSequencia(gsap, q(".faq details"), q(".faq__lista")[0], { y: 16 });
  });

  return (
    <section className="secao" ref={ref} aria-labelledby="faq-titulo">
      <div className="envelope faq">
        <CabecaSecao id="faq-titulo" titulo="Antes de decolar." />
        <div className="faq__lista">
          {PERGUNTAS.map(({ pergunta, resposta }) => (
            <details key={pergunta} name="faq">
              <summary>
                {pergunta}
                <Plus className="faq__sinal" size={20} strokeWidth={1.75} aria-hidden="true" />
              </summary>
              <p className="faq__resposta">{resposta}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
