import { useState } from "react";
import { Link } from "react-router-dom";
import { Scale, Code2 } from "lucide-react";
import PageTransition from "../components/PageTransition";
import CardVagas from "../components/CardVagas";
import TermosDeUso from "../components/modals/TermosDeUso";
import PoliticaPrivacidade from "../components/modals/PoliticaPrivacidade";
import Sobre from "../components/modals/Sobre";
import ComoUsar from "../components/modals/ComoUsar";
import ComoFunciona from "../components/modals/ComoFunciona";

const linksFooter = [
  { label: 'Termos de Uso', id: 'termos' },
  { label: 'Privacidade', id: 'privacidade' },
  { label: 'Sobre', id: 'sobre' },
  { label: 'Como Usar', id: 'como-usar' },
  { label: 'Como Funciona', id: 'como-funciona' },
];

export default function Home() {
  const [modalAberto, setModalAberto] = useState(null);

  return (
    <PageTransition>
      <div className="min-h-screen flex flex-col items-center justify-center px-6 sm:px-12 pt-20 pb-12"
        style={{ fontFamily: "'Space Grotesk', sans-serif" }}
      >

        {/* Eyebrow */}
        <p className="text-[11px] text-[#4FC3F7] tracking-[0.3em] uppercase font-medium mb-5 text-center">
          Agregador de Vagas Remotas
        </p>

        {/* Título */}
        <h1
          className="text-[44px] sm:text-[64px] lg:text-[80px] font-bold text-white leading-none text-center mb-6"
          style={{
            letterSpacing: '-1px',
            textShadow: '0 0 40px rgba(79,195,247,0.35), 0 0 80px rgba(79,195,247,0.15)',
          }}
        >
          MyOrbita
        </h1>

        {/* Subtítulo */}
        <p className="text-[16px] sm:text-[18px] text-[#A0AEC0] font-normal leading-[1.7] text-center max-w-110 mb-16">
          Encontre vagas remotas em tecnologia e direito — atualizadas diariamente.
        </p>

        {/* Cards */}
        <div className="flex items-stretch justify-center gap-6 flex-wrap w-full max-w-160">
          <CardVagas
            to="/vagas-dev"
            icone={<Code2 size={40} color="#4FC3F7" strokeWidth={1.5} />}
            titulo="Vagas Dev"
            descricao="Tecnologia & Desenvolvimento"
            corHover="#4FC3F7"
          />
          <CardVagas
            to="/vagas-adv"
            icone={<Scale size={40} color="#FFB703" strokeWidth={1.5} />}
            titulo="Vagas Jurídico"
            descricao="Direito & Advocacia"
            corHover="#FFB703"
          />
        </div>

        {/* Footer informativo */}
        <div
          style={{
            marginTop: '48px',
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', gap: '14px',
          }}
        >
          <p style={{ fontSize: '11px', color: '#2e2e4a', letterSpacing: '0.2em', textTransform: 'uppercase', margin: 0, textAlign: 'center' }}>
            Fonte: Gupy · LinkedIn · Atualizado diariamente
          </p>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', justifyContent: 'center' }}>
            {linksFooter.map(({ label, id }, i) => (
              <span key={id} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                {i > 0 && (
                  <span style={{ color: '#2e2e4a', fontSize: '11px', userSelect: 'none' }}>·</span>
                )}
                <button
                  onClick={() => setModalAberto(id)}
                  style={{
                    background: 'none', border: 'none', cursor: 'pointer',
                    fontSize: '11px', color: '#4a4a6a',
                    letterSpacing: '0.1em', textTransform: 'uppercase',
                    padding: '2px 0', transition: 'color 0.2s',
                    fontFamily: "'Space Grotesk', sans-serif",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#A0AEC0')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = '#4a4a6a')}
                >
                  {label}
                </button>
              </span>
            ))}
          </div>
        </div>

      </div>

      {/* Modais */}
      {modalAberto === 'termos' && <TermosDeUso onClose={() => setModalAberto(null)} />}
      {modalAberto === 'privacidade' && <PoliticaPrivacidade onClose={() => setModalAberto(null)} />}
      {modalAberto === 'sobre' && <Sobre onClose={() => setModalAberto(null)} />}
      {modalAberto === 'como-usar' && <ComoUsar onClose={() => setModalAberto(null)} />}
      {modalAberto === 'como-funciona' && <ComoFunciona onClose={() => setModalAberto(null)} />}

    </PageTransition>
  );
}
