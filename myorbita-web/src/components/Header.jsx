import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { m } from "framer-motion";
import { Menu, X, Pause, Play } from "lucide-react";
import Marca from "./marca/Marca";
import { useCeuStore } from "../stores/ceuStore";
import { useReduzMovimento } from "../hooks/useReduzMovimento";
import { DUR, EASE_SAIDA } from "../constants/motion";

const links = [
  { to: "/", label: "Início" },
  { to: "/vagas-dev", label: "Vagas Dev" },
  { to: "/vagas-adv", label: "Vagas Jurídico" },
];

// Barra transparente no topo da página; vira vidro assim que a página rola.
function useRolou(limite = 12) {
  const [rolou, setRolou] = useState(false);
  useEffect(() => {
    const medir = () => setRolou(window.scrollY > limite);
    medir();
    window.addEventListener("scroll", medir, { passive: true });
    return () => window.removeEventListener("scroll", medir);
  }, [limite]);
  return rolou;
}

export default function Header() {
  const { pathname } = useLocation();
  const [menuAberto, setMenuAberto] = useState(false);
  const rolou = useRolou();
  const reduz = useReduzMovimento();
  const { pausado, alternar } = useCeuStore();

  // A gaveta fecha ao trocar de rota e no Esc.
  const [rotaDoMenu, setRotaDoMenu] = useState(pathname);
  if (rotaDoMenu !== pathname) {
    setRotaDoMenu(pathname);
    setMenuAberto(false);
  }
  useEffect(() => {
    if (!menuAberto) return;
    const aoTeclar = (e) => e.key === "Escape" && setMenuAberto(false);
    document.addEventListener("keydown", aoTeclar);
    return () => document.removeEventListener("keydown", aoTeclar);
  }, [menuAberto]);

  const transicaoIndicador = reduz
    ? { duration: 0 }
    : { type: "spring", stiffness: 420, damping: 36, mass: 0.8 };

  return (
    <header
      className="cabecalho"
      data-rolou={rolou ? "true" : "false"}
      data-menu={menuAberto ? "aberto" : "fechado"}
    >
      <div className="envelope cabecalho__envelope">
        <Link to="/" className="cabecalho__marca" aria-label="MyOrbita, início">
          <Marca variante="header" />
        </Link>

        <div className="cabecalho__lado">
          <nav className="cabecalho__nav" aria-label="Principal">
            {links.map(({ to, label }) => {
              const ativo = pathname === to;
              return (
                <Link
                  key={to}
                  to={to}
                  className="cabecalho__link"
                  aria-current={ativo ? "page" : undefined}
                >
                  {label}
                  {ativo && (
                    <m.span
                      layoutId="cabecalho-indicador"
                      className="cabecalho__indicador"
                      transition={transicaoIndicador}
                      aria-hidden="true"
                    />
                  )}
                </Link>
              );
            })}
          </nav>

          <button
            type="button"
            className="cabecalho__icone"
            onClick={alternar}
            aria-pressed={pausado}
            aria-label={pausado ? "Animar o céu" : "Pausar o céu"}
            title={pausado ? "Animar o céu" : "Pausar o céu"}
          >
            {pausado ? <Play size={16} strokeWidth={1.75} /> : <Pause size={16} strokeWidth={1.75} />}
          </button>

          <button
            type="button"
            className="cabecalho__icone cabecalho__menu-botao"
            onClick={() => setMenuAberto((v) => !v)}
            aria-expanded={menuAberto}
            aria-controls="gaveta-navegacao"
            aria-label={menuAberto ? "Fechar menu" : "Abrir menu"}
          >
            {menuAberto ? <X size={18} strokeWidth={1.75} /> : <Menu size={18} strokeWidth={1.75} />}
          </button>
        </div>
      </div>

      {menuAberto && (
        <m.nav
          id="gaveta-navegacao"
          className="cabecalho__gaveta"
          aria-label="Principal"
          initial={reduz ? false : { opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: DUR.rapida, ease: EASE_SAIDA }}
        >
          <ul>
            {links.map(({ to, label }) => (
              <li key={to}>
                <Link to={to} aria-current={pathname === to ? "page" : undefined}>
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </m.nav>
      )}
    </header>
  );
}
