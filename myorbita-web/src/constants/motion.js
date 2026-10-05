// Espelho em JS dos tokens de motion de src/styles/tokens.css.
// framer-motion recebe segundos e arrays de bezier; mude os dois juntos.

export const EASE_SAIDA = [0.16, 1, 0.3, 1];
export const EASE_PADRAO = [0.65, 0, 0.35, 1];

export const DUR = {
  instante: 0.12,
  rapida: 0.2,
  media: 0.36,
  lenta: 0.72,
  rota: 1.1,
};

// Intervalo entre itens de uma entrada coreografada
export const ESCALONAMENTO = 0.08;

// Mesma curva de EASE_SAIDA no vocabulário do GSAP (expo.out ≈ 0.16,1,0.3,1).
export const EASE_GSAP = "expo.out";
