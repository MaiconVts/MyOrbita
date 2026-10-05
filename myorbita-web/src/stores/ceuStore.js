import { create } from 'zustand';

// Pausa do céu animado (WCAG 2.2.2). Lembrada por visitante; o atributo
// data-ceu no <html> congela também as animações em CSS da carta.
const CHAVE = 'myorbita:ceu-pausado';

function lerPreferencia() {
  try {
    return localStorage.getItem(CHAVE) === '1';
  } catch {
    return false;
  }
}

const temDocumento = typeof document !== 'undefined';

function aplicar(pausado) {
  if (!temDocumento) return;
  document.documentElement.dataset.ceu = pausado ? 'pausado' : 'vivo';
  try {
    localStorage.setItem(CHAVE, pausado ? '1' : '0');
  } catch {
    // armazenamento indisponível: a pausa vale só nesta visita
  }
}

const inicial = temDocumento ? lerPreferencia() : false;
if (temDocumento) document.documentElement.dataset.ceu = inicial ? 'pausado' : 'vivo';

export const useCeuStore = create((set, get) => ({
  pausado: inicial,
  alternar: () => {
    const pausado = !get().pausado;
    aplicar(pausado);
    set({ pausado });
  },
}));
