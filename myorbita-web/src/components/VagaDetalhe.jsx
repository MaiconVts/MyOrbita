import { MapPin, Briefcase, Accessibility, Clock, ArrowUpRight } from "lucide-react";
import Modal from "./Modal";
import { estaAusente, formatarData, formatarLocalizacao, statusPrazo } from "../utils/vagas";

/**
 * Detalhe de uma vaga. `luz` é a luz da modalidade (tech, adv ou neutra),
 * calculada por quem abre o detalhe, para seguir a mesma regra da lista.
 */
export default function VagaDetalhe({ vaga, onClose, luz = "neutra" }) {
  const local = formatarLocalizacao(vaga.city, vaga.state);
  const prazo = estaAusente(vaga.prazo_inscricao) ? null : statusPrazo(vaga.prazo_inscricao);

  const campos = [
    { rotulo: "Empresa", valor: vaga.empresa },
    { rotulo: "Modalidade", valor: vaga.modalidade, luz },
    { rotulo: "Publicado", valor: formatarData(vaga.data_publicacao), mono: true },
    { rotulo: "Origem", valor: vaga.origem },
  ];

  return (
    <Modal titulo={vaga.titulo} onClose={onClose}>
      <dl className="detalhe__campos">
        {campos.map(({ rotulo, valor, luz: luzCampo, mono }) => {
          const ausente = estaAusente(valor);
          return (
            <div key={rotulo} className="detalhe__campo">
              <dt className="voz-rotulo">{rotulo}</dt>
              <dd
                className={[
                  ausente ? "dado-ausente" : "",
                  luzCampo ? `luz-${luzCampo}` : "",
                  mono && !ausente ? "voz-coordenada" : "",
                ].join(" ")}
              >
                {ausente ? "Não informado" : valor}
              </dd>
            </div>
          );
        })}
      </dl>

      <ul className="detalhe__selos" aria-label="Detalhes da vaga">
        {!local.ausente && (
          <li className="selo">
            <MapPin size={14} strokeWidth={1.5} aria-hidden="true" />
            {local.texto}
          </li>
        )}
        {!estaAusente(vaga.tipo_contrato) && (
          <li className="selo">
            <Briefcase size={14} strokeWidth={1.5} aria-hidden="true" />
            {vaga.tipo_contrato}
          </li>
        )}
        {vaga.pcd && (
          <li className="selo">
            <Accessibility size={14} strokeWidth={1.5} aria-hidden="true" />
            PCD
          </li>
        )}
        {prazo && (
          <li className={`selo selo--prazo-${prazo.estado}`}>
            <Clock size={14} strokeWidth={1.5} aria-hidden="true" />
            <span className="so-leitor">Prazo de inscrição: </span>
            {prazo.texto}
          </li>
        )}
      </ul>

      <a className="botao botao--rota detalhe__cta" href={vaga.link} target="_blank" rel="noopener noreferrer">
        Ver Vaga Completa
        <ArrowUpRight size={18} strokeWidth={1.75} aria-hidden="true" />
        <span className="so-leitor"> (abre em nova aba)</span>
      </a>
    </Modal>
  );
}
