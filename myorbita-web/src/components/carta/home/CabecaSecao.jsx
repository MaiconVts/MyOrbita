// Cabeçalho comum das seções da Home: título e texto de apoio.
export default function CabecaSecao({ id, titulo, texto, children }) {
  return (
    <header className="secao__cabeca" data-cabeca>
      <div>
        <h2 className="secao__titulo" id={id}>
          {titulo}
        </h2>
      </div>
      {texto && <p className="secao__texto">{texto}</p>}
      {children}
    </header>
  );
}
