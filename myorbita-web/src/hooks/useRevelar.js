import { useLayoutEffect, useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReduzMovimento } from "./useReduzMovimento";
import { DUR, EASE_GSAP, ESCALONAMENTO } from "../constants/motion";

gsap.registerPlugin(ScrollTrigger);

const useEfeitoDeLayout = typeof window === "undefined" ? useEffect : useLayoutEffect;

/*
 * Coreografia de rolagem de uma seção, escopada no ref. `montar(gsap, alvo)`
 * recebe o gsap e o seletor do escopo; tudo é desfeito ao desmontar.
 * Com movimento reduzido não roda nada: o conteúdo já está visível no HTML.
 * `deps` refaz a coreografia quando os dados chegam (ex.: contagens).
 */
export function useRevelar(ref, montar, deps = []) {
  const reduz = useReduzMovimento();
  useEfeitoDeLayout(() => {
    if (reduz || !ref.current) return;
    const ctx = gsap.context((self) => montar(gsap, self.selector), ref);
    ScrollTrigger.refresh();
    return () => ctx.revert();
  }, [reduz, ...deps]);
}

/** Entrada padrão: sobe e acende em sequência quando entra na tela. */
export function revelarEmSequencia(gsap, alvos, gatilho, extra = {}) {
  return gsap.from(alvos, {
    opacity: 0,
    y: 28,
    duration: DUR.lenta,
    ease: EASE_GSAP,
    stagger: ESCALONAMENTO,
    scrollTrigger: { trigger: gatilho, start: "top 82%", once: true },
    ...extra,
  });
}
