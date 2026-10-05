import { ShieldCheck } from "lucide-react";
import Modal from "../Modal";
import { Secao, Atualizacao, Email } from "./partes";

export default function PoliticaPrivacidade({ onClose }) {
  return (
    <Modal titulo="Política de Privacidade" icone={ShieldCheck} onClose={onClose}>
      <Secao titulo="1. Dados Coletados">
        O MyOrbita não solicita cadastro nem coleta dados pessoais diretamente dos usuários.
        Nenhuma informação de identificação pessoal é armazenada pela plataforma.
      </Secao>
      <Secao titulo="2. Google Analytics 4">
        Utilizamos o Google Analytics 4 para entender como a plataforma é utilizada.
        Os dados coletados são anônimos e incluem: visualizações de página e navegação,
        tipo de dispositivo, sistema operacional e navegador, localização geográfica
        aproximada (nível de cidade) e idioma do navegador. Esses dados são processados
        pelo Google conforme a{" "}
        <a className="modal-link" href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">
          Política de Privacidade do Google
          <span className="so-leitor"> (abre em nova aba)</span>
        </a>
        .
      </Secao>
      <Secao titulo="3. Cookies">
        O Google Analytics utiliza cookies de sessão para análise de uso agregado.
        Esses cookies não identificam você pessoalmente.
      </Secao>
      <Secao titulo="4. Firebase">
        Os dados das vagas são armazenados no Firebase Realtime Database (Google).
        Nenhum dado do usuário é armazenado no Firebase — apenas os dados públicos
        das vagas coletadas.
      </Secao>
      <Secao titulo="5. Compartilhamento">
        Não compartilhamos dados com terceiros além do Google Analytics,
        conforme descrito nesta política.
      </Secao>
      <Secao titulo="6. Seus Direitos (LGPD)">
        Conforme a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), você tem
        o direito de confirmar a existência de tratamento de dados, solicitar acesso
        ou eliminação de dados. Entre em contato pelo e-mail abaixo para exercer
        esses direitos.
      </Secao>
      <Secao titulo="7. Encarregado (DPO)">
        Maicon Vitor Theodoro da Silva
        <br />
        <Email />
      </Secao>
      <Atualizacao />
    </Modal>
  );
}
