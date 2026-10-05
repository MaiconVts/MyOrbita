import { useEffect } from 'react';
import { m } from 'framer-motion';
import { useTransitionStore } from '../stores/transitionStore';
import { useReduzMovimento } from '../hooks/useReduzMovimento';
import { DUR, EASE_SAIDA } from '../constants/motion';

export default function PageTransition({ children }) {
  const { startTransition, completeTransition } = useTransitionStore();
  const reduz = useReduzMovimento();

  // Dispara warp na entrada de cada página
  useEffect(() => {
    startTransition();
    const timer = setTimeout(completeTransition, 600);
    return () => clearTimeout(timer);
  }, [startTransition, completeTransition]);

  // Conteúdo visível já no primeiro frame (pré-render): só a saída esmaece.
  return (
    <m.div
      className="transicao-pagina"
      initial={false}
      animate={{ opacity: 1 }}
      exit={reduz ? { opacity: 1 } : { opacity: 0 }}
      transition={{ duration: DUR.media, ease: EASE_SAIDA }}
    >
      {children}
    </m.div>
  );
}
