// Cabeçalho comum das seções da Home: marcador numerado, título e texto de apoio.
export default function CabecaSecao({ marcador, id, titulo, texto, children }) {
  return (
    <header className="secao__cabeca" data-cabeca>
      <div>
        <p className="secao__marcador voz-coordenada">{marcador}</p>
        <h2 className="secao__titulo" id={id}>
          {titulo}
        </h2>
      </div>
      {texto && <p className="secao__texto">{texto}</p>}
      {children}
    </header>
  );
}
