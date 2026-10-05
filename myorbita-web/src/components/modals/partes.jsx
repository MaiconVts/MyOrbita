// Peças de texto compartilhadas pelos modais institucionais.

export function Secao({ titulo, children }) {
  return (
    <section className="modal-secao">
      <h3 className="modal-secao__titulo voz-rotulo">{titulo}</h3>
      <div className="modal-secao__texto">{children}</div>
    </section>
  );
}

export function Atualizacao() {
  return <p className="modal-rodape voz-margem">Última atualização: Abril de 2026</p>;
}

export function Email() {
  return (
    <a className="modal-link" href="mailto:mvitor142@gmail.com">
      mvitor142@gmail.com
    </a>
  );
}
