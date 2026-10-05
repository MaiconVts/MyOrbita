import { useEffect, useId, useRef } from "react";
import { X } from "lucide-react";

/**
 * Casca única dos modais, sobre <dialog> nativo: foco preso, Esc e fundo
 * inerte vêm do navegador. Clique fora do painel também fecha.
 */
export default function Modal({ titulo, icone: Icone, onClose, largura = "padrao", children }) {
  const ref = useRef(null);
  const tituloId = useId();

  useEffect(() => {
    const dialogo = ref.current;
    if (dialogo && !dialogo.open) dialogo.showModal();
    const anterior = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = anterior;
    };
  }, []);

  const aoCancelar = (e) => {
    e.preventDefault();
    onClose();
  };

  const aoClicar = (e) => {
    if (e.target === ref.current) onClose();
  };

  return (
    <dialog
      ref={ref}
      className={`modal modal--${largura}`}
      aria-labelledby={tituloId}
      onCancel={aoCancelar}
      onClick={aoClicar}
    >
      <div className="modal__painel">
        <header className="modal__cabeca">
          {Icone && <Icone className="modal__icone" size={20} strokeWidth={1.5} aria-hidden="true" />}
          <h2 id={tituloId} className="modal__titulo voz-gravada">
            {titulo}
          </h2>
          <button type="button" className="modal__fechar" onClick={onClose} aria-label="Fechar">
            <X size={20} strokeWidth={1.5} aria-hidden="true" />
          </button>
        </header>
        <div className="modal__corpo">{children}</div>
      </div>
    </dialog>
  );
}
