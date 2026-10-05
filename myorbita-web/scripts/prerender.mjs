// Pré-render das rotas públicas depois do `vite build`.
// Cada rota vira um HTML com o conteúdo e o <head> próprios (título, descrição,
// canônica, Open Graph e JSON-LD), para buscadores e prévias de link.
import { readFile, writeFile, rm } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dist = path.join(raiz, "dist");
const ssr = path.join(raiz, "dist-ssr");

const { SITE } = await import(pathToFileURL(path.join(raiz, "src/config/site.js")).href);

const ROTAS = [
  { url: "/", arquivo: "index.html" },
  { url: "/vagas-dev", arquivo: "vagas-dev.html" },
  { url: "/vagas-adv", arquivo: "vagas-adv.html" },
];

// Tags que pertencem à página e sobem do corpo para o <head>.
const DO_HEAD = [
  /<title>[\s\S]*?<\/title>/g,
  /<meta (?:name="description"|property="og:(?:title|description|url)")[^>]*\/?>/g,
  /<link rel="canonical"[^>]*\/?>/g,
  /<script type="application\/ld\+json">[\s\S]*?<\/script>/g,
];

const marcar = (tag) => tag.replace(/^<(\w+)/, '<$1 data-prerender=""');

const modelo = await readFile(path.join(dist, "index.html"), "utf8");
const { renderizar } = await import(pathToFileURL(path.join(ssr, "entry-server.js")).href);

for (const { url, arquivo } of ROTAS) {
  let corpo = await renderizar(url);
  const head = [];
  for (const re of DO_HEAD) {
    corpo = corpo.replace(re, (tag) => {
      head.push(marcar(tag));
      return "";
    });
  }
  if (!head.some((t) => t.startsWith("<title"))) throw new Error(`Rota ${url} sem <title>`);

  const html = modelo
    .replace(/\s*<[^>]+data-prerender[^>]*>(?:[^<]*<\/title>)?/g, "")
    .replace("</head>", `    ${head.join("\n    ")}\n  </head>`)
    .replace('<div id="root"></div>', `<div id="root">${corpo}</div>`);

  await writeFile(path.join(dist, arquivo), html);
  console.log(`pré-render: ${url} -> dist/${arquivo} (${(html.length / 1024).toFixed(1)} kB)`);
}

// Sitemap com as mesmas rotas; lastmod é a data do build, que acompanha a coleta diária.
const hoje = new Date().toISOString().slice(0, 10);
const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${ROTAS.map(({ url }) => `  <url><loc>${SITE.url}${url}</loc><lastmod>${hoje}</lastmod></url>`).join("\n")}
</urlset>
`;
await writeFile(path.join(dist, "sitemap.xml"), sitemap);
console.log(`sitemap: ${ROTAS.length} rotas -> dist/sitemap.xml`);

await rm(ssr, { recursive: true, force: true });
