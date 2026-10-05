import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import Lenis from "lenis";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReduzMovimento } from "./useReduzMovimento";

gsap.registerPlugin(ScrollTrigger);

let lenisAtivo = null;

/*
 * Rolagem suave com Lenis, no mesmo relógio do GSAP para que os
 * ScrollTriggers leiam a posição já suavizada. Desligada com movimento
 * reduzido. Na troca de rota, volta ao topo sem animar.
 */
export function useRolagemSuave() {
  const reduz = useReduzMovimento();
  const { pathname } = useLocation();

  useEffect(() => {
    if (reduz) return;
    const lenis = new Lenis({ autoRaf: false, lerp: 0.11 });
    const quadro = (t) => lenis.raf(t * 1000);
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add(quadro);
    gsap.ticker.lagSmoothing(0);
    lenisAtivo = lenis;
    return () => {
      gsap.ticker.remove(quadro);
      lenis.destroy();
      lenisAtivo = null;
    };
  }, [reduz]);

  useEffect(() => {
    if (lenisAtivo) lenisAtivo.scrollTo(0, { immediate: true, force: true });
    else window.scrollTo(0, 0);
  }, [pathname]);
}

/** Rola até o elemento descontando o cabeçalho fixo; usa o Lenis quando ativo. */
export function rolarAte(elemento, folga = 16) {
  if (!elemento) return;
  const cabecalho = document.querySelector(".cabecalho")?.offsetHeight ?? 0;
  const y = elemento.getBoundingClientRect().top + window.scrollY - cabecalho - folga;
  if (lenisAtivo) lenisAtivo.scrollTo(y);
  else window.scrollTo({ top: y });
}
