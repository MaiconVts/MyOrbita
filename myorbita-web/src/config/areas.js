import { ROUTES } from "../constants/routes";

// Cada área é um rumo da carta: Tech segue a luz azul, Jurídico a âmbar.
// As rotas do Firebase ficam em arrays de módulo para manter a referência
// estável entre renders (useCacheVagas depende disso).

export const AREAS = {
  dev: {
    chave: "dev",
    caminho: ROUTES.VAGAS_DEV,
    rotasFirebase: [ROUTES.FIREBASE_VAGAS_DEV_GUPY, ROUTES.FIREBASE_VAGAS_DEV_LINKEDIN],
    nome: "Tecnologia",
    titulo: "Vagas Dev",
    subtitulo: "Tecnologia & Desenvolvimento",
    placeholderBusca: "Ex: C# .NET Pleno",
    luz: "tech",
    outraLuz: "adv",
    seo: {
      titulo: "Vagas remotas de tecnologia e desenvolvimento | MyOrbita",
      descricao:
        "Vagas remotas, híbridas e presenciais de tecnologia e desenvolvimento reunidas da Gupy e do LinkedIn, atualizadas todos os dias.",
    },
  },
  adv: {
    chave: "adv",
    caminho: ROUTES.VAGAS_ADV,
    rotasFirebase: [ROUTES.FIREBASE_VAGAS_ADV_GUPY, ROUTES.FIREBASE_VAGAS_ADV_LINKEDIN],
    nome: "Jurídico",
    titulo: "Vagas Jurídico",
    subtitulo: "Advocacia & Jurídico",
    placeholderBusca: "Ex: Advogado Trabalhista Pleno",
    luz: "adv",
    outraLuz: "tech",
    seo: {
      titulo: "Vagas remotas de advocacia e jurídico | MyOrbita",
      descricao:
        "Vagas remotas, híbridas e presenciais de advocacia e área jurídica reunidas da Gupy e do LinkedIn, atualizadas todos os dias.",
    },
  },
};

export const OPCOES_NIVEL = [
  { value: "estagio", label: "Estágio" },
  { value: "junior", label: "Júnior" },
  { value: "pleno", label: "Pleno" },
  { value: "senior", label: "Sênior" },
];

export const MODALIDADES = ["Remoto", "Híbrido", "Presencial"];

/** Luz de cada modalidade dentro de uma área: Remoto acende a luz da área. */
export function luzDaModalidade(area, modalidade) {
  if (modalidade === "Remoto") return area.luz;
  if (modalidade === "Híbrido") return area.outraLuz;
  return "neutra";
}
