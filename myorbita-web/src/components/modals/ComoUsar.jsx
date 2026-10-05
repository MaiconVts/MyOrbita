import { Map } from "lucide-react";
import Modal from "../Modal";

function Passo({ numero, titulo, children }) {
  return (
    <li className="modal-passo">
      <span className="modal-passo__numero voz-coordenada" aria-hidden="true">
        {numero}
      </span>
      <div>
        <h3 className="modal-passo__titulo">{titulo}</h3>
        <div className="modal-passo__texto">{children}</div>
      </div>
    </li>
  );
}

export default function ComoUsar({ onClose }) {
  return (
    <Modal titulo="Como Usar" icone={Map} onClose={onClose}>
      <ol className="modal-passos">
        <Passo numero="01" titulo="Escolha sua área">
          Na página inicial, selecione <strong className="luz-tech">Vagas Dev</strong> para
          Tecnologia & Desenvolvimento ou <strong className="luz-adv">Vagas Jurídico</strong> para
          Direito & Advocacia.
        </Passo>
        <Passo numero="02" titulo="Filtre as vagas">
          Use os filtros disponíveis para refinar sua busca:
          <ul className="modal-lista">
            <li>Busca textual por título, empresa ou localização</li>
            <li>Modalidade: Remoto, Híbrido ou Presencial</li>
            <li>Nível: Estágio, Júnior, Pleno ou Sênior</li>
            <li>Estado, Tipo de Contrato, PCD e Plataforma de origem</li>
          </ul>
        </Passo>
        <Passo numero="03" titulo="Explore uma vaga">
          Clique em qualquer card para abrir os detalhes completos da vaga —
          empresa, modalidade, localização, contrato, prazo de inscrição e mais.
        </Passo>
        <Passo numero="04" titulo="Candidate-se">
          Dentro do painel de detalhes, clique em <strong className="luz-adv">Ver Vaga Completa</strong>{" "}
          para ser redirecionado ao site original da vaga.
        </Passo>
        <Passo numero="05" titulo="Atualize os dados">
          As vagas são atualizadas automaticamente todos os dias às ~4h (horário de Brasília).
          Para forçar uma atualização manual, clique no botão <strong>Atualizar</strong> na barra de filtros.
        </Passo>
      </ol>
    </Modal>
  );
}
