import { useSyncExternalStore } from "react";

// Preferência do sistema por menos movimento, reativa a mudanças em tempo real.
const consulta = "(prefers-reduced-motion: reduce)";

function assinar(aviso) {
  const mq = window.matchMedia(consulta);
  mq.addEventListener("change", aviso);
  return () => mq.removeEventListener("change", aviso);
}

export function useReduzMovimento() {
  return useSyncExternalStore(
    assinar,
    () => window.matchMedia(consulta).matches,
    () => false,
  );
}
