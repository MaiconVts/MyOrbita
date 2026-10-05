import { ScrollText } from "lucide-react";
import Modal from "../Modal";
import { Secao, Atualizacao, Email } from "./partes";

export default function TermosDeUso({ onClose }) {
  return (
    <Modal titulo="Termos de Uso" icone={ScrollText} onClose={onClose}>
      <p className="modal-aviso">
        <strong>Ao utilizar o MyOrbita</strong>, você declara que leu, compreendeu e concorda
        integralmente com estes Termos de Uso. Caso não concorde, interrompa o uso da plataforma.
      </p>
      <Secao titulo="1. Sobre o MyOrbita">
        O MyOrbita é uma plataforma de uso pessoal e portfólio técnico que agrega vagas de
        emprego publicamente disponíveis nas plataformas Gupy e LinkedIn, exibindo-as de forma
        consolidada e organizada por área profissional.
      </Secao>
      <Secao titulo="2. Uso da Plataforma">
        A plataforma é disponibilizada gratuitamente para consulta de vagas. É vedado o uso
        comercial, revenda ou reprodução do sistema sem autorização expressa do autor.
      </Secao>
      <Secao titulo="3. Google Analytics">
        Utilizamos o Google Analytics 4 para análise de uso anônima. Os dados coletados
        incluem visualizações de página, tipo de dispositivo, navegador e localização
        geográfica aproximada. Nenhum dado pessoal identificável é coletado ou armazenado
        pelo MyOrbita.
      </Secao>
      <Secao titulo="4. Dados das Vagas">
        As vagas exibidas são coletadas automaticamente de fontes públicas (Gupy e LinkedIn).
        O MyOrbita não garante a disponibilidade, atualidade ou veracidade das informações.
        Sempre verifique no site original antes de candidatar-se.
      </Secao>
      <Secao titulo="5. Propriedade Intelectual">
        O código-fonte do MyOrbita é de propriedade de Maicon Vitor Theodoro da Silva —
        todos os direitos reservados. As informações das vagas pertencem às respectivas
        empresas e plataformas de origem.
      </Secao>
      <Secao titulo="6. Isenção de Responsabilidade">
        O MyOrbita não se responsabiliza por vagas encerradas, informações desatualizadas
        ou quaisquer danos decorrentes do uso da plataforma.
      </Secao>
      <Secao titulo="7. Contato">
        <Email />
      </Secao>
      <Atualizacao />
    </Modal>
  );
}
