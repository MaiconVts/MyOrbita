import { StrictMode } from "react";
import { prerenderToNodeStream } from "react-dom/static";
import { StaticRouter } from "react-router-dom";
import { Casca } from "./App";

// Gera o HTML de uma rota no build. O prerender espera as rotas lazy
// resolverem, então o conteúdo da página já sai completo no HTML.
export async function renderizar(url) {
  const { prelude } = await prerenderToNodeStream(
    <StrictMode>
      <StaticRouter location={url}>
        <Casca />
      </StaticRouter>
    </StrictMode>,
  );
  let html = "";
  for await (const pedaco of prelude) html += pedaco;
  return html;
}
