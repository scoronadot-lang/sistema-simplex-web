import React from 'react';
import { createRoot } from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';
import './styles.css';
import './overrides.css';
import App from './App.jsx';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <MantineProvider defaultColorScheme="dark" theme={{ primaryColor: 'cyan', defaultRadius: 'md', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <App />
    </MantineProvider>
  </React.StrictMode>,
);
