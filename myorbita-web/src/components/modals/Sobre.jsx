import { Orbit } from "lucide-react";
import Modal from "../Modal";
import { Secao } from "./partes";

const STACK = [
  ["Backend", "Python 3.11 — Scrapers Gupy (API) e LinkedIn (HTML)"],
  ["Banco de Dados", "Firebase Realtime Database"],
  ["Automação", "GitHub Actions — execução diária"],
  ["Frontend", "React 19 + Vite + TypeScript + Tailwind CSS"],
  ["Animações", "Framer Motion"],
];

export default function Sobre({ onClose }) {
  return (
    <Modal titulo="Sobre o MyOrbita" icone={Orbit} onClose={onClose}>
      <p className="modal-lede">
        Agregador inteligente de vagas profissionais desenvolvido como projeto solo
        de portfólio técnico. Coleta, padroniza e exibe vagas de tecnologia e direito
        em uma interface unificada, atualizada diariamente.
      </p>
      <Secao titulo="Autor">
        <strong>Maicon Vitor Theodoro da Silva</strong>
        <br />
        Desenvolvedor FullStack — Vespasiano, MG
        <br />
        <a className="modal-link" href="https://github.com/MaiconVts/MyOrbita" target="_blank" rel="noopener noreferrer">
          github.com/MaiconVts/MyOrbita
          <span className="so-leitor"> (abre em nova aba)</span>
        </a>
      </Secao>
      <Secao titulo="Stack Técnica">
        <dl className="modal-stack">
          {STACK.map(([rotulo, valor]) => (
            <div key={rotulo}>
              <dt>{rotulo}:</dt> <dd>{valor}</dd>
            </div>
          ))}
        </dl>
      </Secao>
      <Secao titulo="Fontes de Dados">
        As vagas são coletadas automaticamente todos os dias das plataformas{" "}
        <span className="luz-tech">Gupy</span> e <span className="luz-linkedin">LinkedIn</span>.
      </Secao>
    </Modal>
  );
}
