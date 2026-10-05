import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence, LazyMotion } from "framer-motion";
import Home from "./pages/Home";
import PlanetarySystem from "./components/PlanetarySystem";
import Header from "./components/Header";
import Rodape from "./components/Rodape";
import { useRolagemSuave } from "./hooks/useRolagemSuave";

// As listas carregam sob demanda: a Home não paga pelo código dos filtros.
const VagasDev = lazy(() => import("./pages/VagasDev"));
const VagasAdv = lazy(() => import("./pages/VagasAdv"));

export function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Suspense fallback={null} key={location.pathname}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Home />} />
          <Route path="/vagas-dev" element={<VagasDev />} />
          <Route path="/vagas-adv" element={<VagasAdv />} />
        </Routes>
      </Suspense>
    </AnimatePresence>
  );
}

// Os componentes `m` só ganham animação quando estes recursos chegam.
const carregarRecursos = () => import("./utils/recursosMotion").then((r) => r.default);

// Casca comum ao cliente e ao pré-render; o roteador vem de fora.
export function Casca() {
  useRolagemSuave();
  return (
    <LazyMotion features={carregarRecursos} strict>
      <a href="#conteudo" className="pular-conteudo">
        Pular para o conteúdo
      </a>
      <PlanetarySystem />
      <div className="app">
        <Header />
        <main id="conteudo" className="app__principal" tabIndex={-1}>
          <AnimatedRoutes />
        </main>
        <Rodape />
      </div>
    </LazyMotion>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Casca />
    </BrowserRouter>
  );
}

export default App;
