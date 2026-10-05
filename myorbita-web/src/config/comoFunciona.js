// Texto factual de "Como funciona", usado no modal e na seção da Home.

export const ETAPAS = [
  {
    titulo: "Coleta Automática",
    icone: "Radar",
    texto:
      "Scrapers Python executam diariamente via GitHub Actions. O scraper da Gupy consome a API REST oficial. O scraper do LinkedIn faz parsing de HTML com técnicas de anti-detecção (TLS fingerprinting, delays gaussianos, circuit breaker).",
  },
  {
    titulo: "Deduplicação",
    icone: "Fingerprint",
    texto:
      "Cada vaga recebe um ID determinístico gerado a partir da URL. Vagas já existentes no banco não são duplicadas entre execuções — garantindo que os dados sejam sempre frescos e sem repetição.",
  },
  {
    titulo: "Armazenamento",
    icone: "Database",
    texto:
      "As vagas padronizadas são salvas no Firebase Realtime Database, organizadas por categoria (Dev / Jurídico) e plataforma (Gupy / LinkedIn).",
  },
  {
    titulo: "Exibição",
    icone: "MonitorSmartphone",
    texto:
      "O app React lê os dados diretamente do Firebase. Um cache local (TTL 1h) evita requisições desnecessárias. Os filtros são aplicados localmente, sem nenhuma chamada extra ao banco.",
  },
];

export const HORARIOS = [
  { plataforma: "Gupy", horario: "03h42" },
  { plataforma: "LinkedIn Dev", horario: "04h45" },
  { plataforma: "LinkedIn Jurídico", horario: "12h00" },
];
