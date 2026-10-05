import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource-variable/unbounded/wght.css'
import '@fontsource-variable/manrope/wght.css'
import '@fontsource-variable/jetbrains-mono/wght.css'
import './index.css'
import App from './App.jsx'

// O <head> do pré-render sai antes: as páginas declaram o próprio título e metadados.
document.head.querySelectorAll('[data-prerender]').forEach((tag) => tag.remove())

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
