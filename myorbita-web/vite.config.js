import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Bibliotecas em pedaços próprios: mudam pouco e ficam no cache entre deploys.
const GRUPOS = [
  { name: 'react', test: /node_modules[/\\](react|react-dom|scheduler|react-router|react-router-dom)[/\\]/ },
  { name: 'motion', test: /node_modules[/\\](gsap|lenis)[/\\]/ },
  { name: 'firebase', test: /node_modules[/\\](@firebase|firebase)[/\\]/ },
]

export default defineConfig(({ isSsrBuild }) => ({
  plugins: [
    react(),
    tailwindcss(),
  ],
  build: isSsrBuild
    ? {}
    : { rolldownOptions: { output: { codeSplitting: { groups: GRUPOS } } } },
}))
