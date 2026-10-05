import { lazy, Suspense, useState } from "react";
import { Link } from "react-router-dom";
import { Coffee } from "lucide-react";
import { SITE } from "../config/site";
import Marca from "./marca/Marca";
import mtIcon from "./CreditoDesenvolvedor/mt-icon.svg";

// Modais só baixam quando alguém abre um deles.
const MODAIS = {
  "como-usar": lazy(() => import("./modals/ComoUsar")),
  "como-funciona": lazy(() => import("./modals/ComoFunciona")),
  sobre: lazy(() => import("./modals/Sobre")),
  termos: lazy(() => import("./modals/TermosDeUso")),
  privacidade: lazy(() => import("./modals/PoliticaPrivacidade")),
};

const NAVEGAR = [
  { to: "/", label: "Início" },
  { to: "/vagas-dev", label: "Vagas Dev" },
  { to: "/vagas-adv", label: "Vagas Jurídico" },
];

const PROJETO = [
  { id: "como-usar", label: "Como usar" },
  { id: "como-funciona", label: "Como funciona" },
  { id: "sobre", label: "Sobre" },
];

const LEGAL = [
  { id: "termos", label: "Termos de Uso" },
  { id: "privacidade", label: "Privacidade" },
];

function Coluna({ titulo, children }) {
  return (
    <div className="rodape__coluna">
      <h2 className="voz-rotulo">{titulo}</h2>
      <ul>{children}</ul>
    </div>
  );
}

export default function Rodape() {
  const [modalAberto, setModalAberto] = useState(null);
  const ModalAtual = modalAberto ? MODAIS[modalAberto] : null;

  const botoes = (itens) =>
    itens.map(({ id, label }) => (
      <li key={id}>
        <button type="button" className="rodape__item" onClick={() => setModalAberto(id)} aria-haspopup="dialog">
          {label}
        </button>
      </li>
    ));

  return (
    <footer className="rodape">
      <div className="envelope">
        <div className="rodape__grade">
          <div className="rodape__marca">
            <Link to="/" aria-label="MyOrbita, início">
              <Marca variante="rodape" />
            </Link>
            <p className="rodape__frase">
              Encontre vagas remotas em tecnologia e direito — atualizadas diariamente.
            </p>
            <p className="voz-coordenada">Fonte: Gupy · LinkedIn</p>
          </div>

          <Coluna titulo="Navegar">
            {NAVEGAR.map(({ to, label }) => (
              <li key={to}>
                <Link to={to} className="rodape__item">
                  {label}
                </Link>
              </li>
            ))}
          </Coluna>
          <Coluna titulo="Projeto">{botoes(PROJETO)}</Coluna>
          <Coluna titulo="Legal">{botoes(LEGAL)}</Coluna>
        </div>

        <div className="rodape__base">
          <span>© {new Date().getFullYear()} MyOrbita</span>
          {SITE.apoio && (
            <a className="credito" href={SITE.apoio} target="_blank" rel="noopener">
              <Coffee aria-hidden="true" strokeWidth={1.75} className="credito__icone" />
              <span>
                Apoie o projeto com um café
                <span className="so-leitor"> (abre em nova aba)</span>
              </span>
            </a>
          )}
          <a className="credito" href="https://maicontheodoro-dev.vercel.app" target="_blank" rel="noopener">
            <img src={mtIcon} alt="" width="20" height="20" />
            <span>
              Desenvolvido por <span className="credito__nome">maicontheodoro-dev</span>
              <span className="so-leitor"> (abre em nova aba)</span>
            </span>
          </a>
        </div>
      </div>

      {ModalAtual && (
        <Suspense fallback={null}>
          <ModalAtual onClose={() => setModalAberto(null)} />
        </Suspense>
      )}
    </footer>
  );
}
