import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import { ChevronDown, Check } from "lucide-react";

/**
 * Dropdown multi-select com checkboxes.
 *
 * Por que usa Portal?
 * O painel de filtros usa `backdrop-filter`, que cria um stacking context
 * isolado: z-index alto não escapa dele. O painel suspenso é renderizado
 * direto no document.body, fora de qualquer stacking context.
 *
 * Posição calculada via getBoundingClientRect() do botão-âncora e
 * atualizada em scroll/resize para acompanhar o botão na tela.
 * Como o painel sai da árvore, a luz da área chega pela prop `luz`.
 */
export default function FiltroMultiSelect({ icone, placeholder, opcoes, selecionados, onChange, luz = "neutra" }) {
  const [aberto, setAberto] = useState(false);
  const [posicaoPainel, setPosicaoPainel] = useState({ top: 0, left: 0, width: 0 });
  const containerRef = useRef(null);
  const botaoRef = useRef(null);
  const painelRef = useRef(null);

  const atualizarPosicao = () => {
    if (!botaoRef.current) return;
    const rect = botaoRef.current.getBoundingClientRect();
    setPosicaoPainel({ top: rect.bottom + 6, left: rect.left, width: rect.width });
  };

  useEffect(() => {
    if (!aberto) return;
    atualizarPosicao();
    window.addEventListener("scroll", atualizarPosicao, true);
    window.addEventListener("resize", atualizarPosicao);
    return () => {
      window.removeEventListener("scroll", atualizarPosicao, true);
      window.removeEventListener("resize", atualizarPosicao);
    };
  }, [aberto]);

  // Fecha ao clicar fora (botão e painel contam como "dentro") e no Esc,
  // devolvendo o foco ao botão.
  useEffect(() => {
    if (!aberto) return;

    const handleClickFora = (e) => {
      const dentroBotao = containerRef.current?.contains(e.target);
      const dentroPainel = painelRef.current?.contains(e.target);
      if (!dentroBotao && !dentroPainel) setAberto(false);
    };

    const handleEsc = (e) => {
      if (e.key === "Escape") {
        setAberto(false);
        botaoRef.current?.focus();
      }
    };

    document.addEventListener("mousedown", handleClickFora);
    document.addEventListener("keydown", handleEsc);
    return () => {
      document.removeEventListener("mousedown", handleClickFora);
      document.removeEventListener("keydown", handleEsc);
    };
  }, [aberto]);

  // Setas movem o foco entre as opções do painel aberto.
  const aoTeclarPainel = (e) => {
    if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
    e.preventDefault();
    const itens = [...(painelRef.current?.querySelectorAll('[role="option"]') ?? [])];
    const atual = itens.indexOf(document.activeElement);
    const proximo = e.key === "ArrowDown" ? Math.min(itens.length - 1, atual + 1) : Math.max(0, atual - 1);
    itens[proximo]?.focus();
  };

  const toggleOpcao = (value) => {
    if (selecionados.includes(value)) onChange(selecionados.filter((v) => v !== value));
    else onChange([...selecionados, value]);
  };

  const textoBotao = (() => {
    if (selecionados.length === 0) return placeholder;
    if (selecionados.length === 1) {
      const op = opcoes.find((o) => o.value === selecionados[0]);
      return op?.label ?? selecionados[0];
    }
    return `${selecionados.length} selecionados`;
  })();

  const temSelecao = selecionados.length > 0;

  const painel =
    aberto && typeof document !== "undefined"
      ? createPortal(
          <div
            ref={painelRef}
            className={`multi-painel luz-${luz}`}
            style={{
              top: posicaoPainel.top,
              left: posicaoPainel.left,
              minWidth: Math.max(posicaoPainel.width, 200),
            }}
            role="listbox"
            aria-multiselectable="true"
            aria-label={placeholder}
            onKeyDown={aoTeclarPainel}
          >
            {opcoes.length === 0 ? (
              <div className="multi-painel__vazio">Nenhuma opção disponível</div>
            ) : (
              opcoes.map((opcao) => {
                const marcado = selecionados.includes(opcao.value);
                return (
                  <button
                    key={opcao.value}
                    type="button"
                    onClick={() => toggleOpcao(opcao.value)}
                    role="option"
                    aria-selected={marcado}
                    className={`multi-opcao ${opcao.luz ? `luz-${opcao.luz}` : ""}`}
                  >
                    <span className="multi-opcao__caixa" aria-hidden="true">
                      {marcado && <Check size={11} strokeWidth={3} />}
                    </span>
                    {opcao.luz && <span className="alternador__ponto" aria-hidden="true" />}
                    <span>{opcao.label}</span>
                  </button>
                );
              })
            )}
          </div>,
          document.body,
        )
      : null;

  return (
    <div ref={containerRef} className="relative min-w-0">
      <button
        ref={botaoRef}
        type="button"
        onClick={() => setAberto((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={aberto}
        aria-pressed={temSelecao}
        className="alternador multi"
      >
        <span className="multi__rotulo">
          {icone && <span className="multi__icone" aria-hidden="true">{icone}</span>}
          <span className="multi__texto">{textoBotao}</span>
        </span>
        <ChevronDown size={14} className="multi__seta" aria-hidden="true" />
      </button>
      {painel}
    </div>
  );
}
