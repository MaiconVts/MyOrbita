import { lazy, Suspense, useState } from "react";
import PageTransition from "../components/PageTransition";
import Hero from "../components/carta/home/Hero";
import Rotas from "../components/carta/home/Rotas";
import Radar from "../components/carta/home/Radar";
import Trajeto from "../components/carta/home/Trajeto";
import Faq from "../components/carta/home/Faq";
import { PERGUNTAS } from "../components/carta/home/perguntas";
import Chamada from "../components/carta/home/Chamada";
import { useResumoVagas } from "../hooks/useResumoVagas";
import { SITE } from "../config/site";

const VagaDetalhe = lazy(() => import("../components/VagaDetalhe"));

const TITULO = "MyOrbita | Vagas remotas em tecnologia e direito, atualizadas diariamente";
const DESCRICAO =
  "Agregador gratuito de vagas remotas, híbridas e presenciais de tecnologia e advocacia, coletadas todos os dias da Gupy e do LinkedIn. Sem cadastro.";

const JSON_LD = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${SITE.url}/#site`,
      name: "MyOrbita",
      url: `${SITE.url}/`,
      inLanguage: "pt-BR",
      description: DESCRICAO,
    },
    {
      "@type": "FAQPage",
      mainEntity: PERGUNTAS.map(({ pergunta, resposta }) => ({
        "@type": "Question",
        name: pergunta,
        acceptedAnswer: { "@type": "Answer", text: resposta },
      })),
    },
  ],
});

export default function Home() {
  const resumo = useResumoVagas(6);
  const [detalhe, setDetalhe] = useState(null);
  const total = resumo.areas.dev.total + resumo.areas.adv.total;

  return (
    <PageTransition>
      <title>{TITULO}</title>
      <meta name="description" content={DESCRICAO} />
      <link rel="canonical" href={`${SITE.url}/`} />
      <meta property="og:title" content={TITULO} />
      <meta property="og:description" content={DESCRICAO} />
      <meta property="og:url" content={`${SITE.url}/`} />
      <script type="application/ld+json">{JSON_LD}</script>

      <Hero resumo={resumo} />
      <Rotas resumo={resumo} />
      <Radar resumo={resumo} onAbrir={setDetalhe} />
      <Trajeto />
      <Faq />
      <Chamada total={total} carregando={resumo.carregando} />

      {detalhe && (
        <Suspense fallback={null}>
          <VagaDetalhe vaga={detalhe.vaga} luz={detalhe.luz} onClose={() => setDetalhe(null)} />
        </Suspense>
      )}
    </PageTransition>
  );
}
