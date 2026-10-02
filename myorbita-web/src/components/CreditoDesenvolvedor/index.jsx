import mtIcon from "./mt-icon.svg";

// Crédito do desenvolvedor no rodapé: ícone MT, "Desenvolvido por" e o nome como link para o portfólio.
// A cor vem de quem usa (className) e a cor do hover também (linkClassName), para servir em qualquer projeto.
export default function CreditoDesenvolvedor({ className = "", linkClassName = "" }) {
  return (
    <p className={`text-xs ${className}`}>
      <a
        href="https://maicontheodoro-dev.vercel.app"
        target="_blank"
        rel="noopener"
        className={`group inline-flex items-center gap-2 rounded-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-current ${linkClassName}`}
      >
        <img src={mtIcon} alt="" width="20" height="20" className="shrink-0" />
        <span>
          Desenvolvido por{" "}
          <span className="font-medium underline underline-offset-4 group-hover:decoration-2">maicontheodoro-dev</span>
          <span className="sr-only"> (abre em nova aba)</span>
        </span>
      </a>
    </p>
  );
}
