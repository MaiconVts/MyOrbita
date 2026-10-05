import { Cog } from "lucide-react";
import Modal from "../Modal";
import { ETAPAS, HORARIOS } from "../../config/comoFunciona";
import { ICONES_ETAPA } from "../carta/iconesEtapa";

export default function ComoFunciona({ onClose }) {
  return (
    <Modal titulo="Como Funciona" icone={Cog} onClose={onClose}>
      <ol className="modal-etapas">
        {ETAPAS.map(({ titulo, icone, texto }) => {
          const Icone = ICONES_ETAPA[icone];
          return (
            <li key={titulo} className="modal-etapa">
              <Icone className="modal-etapa__icone" size={20} strokeWidth={1.5} aria-hidden="true" />
              <div>
                <h3 className="modal-passo__titulo">{titulo}</h3>
                <p className="modal-passo__texto">{texto}</p>
              </div>
            </li>
          );
        })}
      </ol>
      <section className="modal-secao">
        <h3 className="modal-secao__titulo voz-rotulo">Horários de Atualização (BRT)</h3>
        <dl className="modal-horarios">
          {HORARIOS.map(({ plataforma, horario }) => (
            <div key={plataforma}>
              <dt>{plataforma}</dt>
              <dd className="voz-coordenada">{horario}</dd>
            </div>
          ))}
        </dl>
      </section>
    </Modal>
  );
}
