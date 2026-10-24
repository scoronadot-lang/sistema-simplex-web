// Ambos: Punto de entrada común del frontend; carga React, el tema visual y el componente principal.
import React from 'react';
import { createRoot } from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
// Ambos: Carga los estilos base de Mantine y los estilos compartidos del proyecto.
import '@mantine/core/styles.css';
import './styles.css';
import './overrides.css';
import App from './App.jsx';

// Ambos: Monta App en el contenedor HTML y configura Mantine en tema oscuro con cian como color principal.
createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <MantineProvider defaultColorScheme="dark" theme={{ primaryColor: 'cyan', defaultRadius: 'md', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <App />
    </MantineProvider>
  </React.StrictMode>,
);
