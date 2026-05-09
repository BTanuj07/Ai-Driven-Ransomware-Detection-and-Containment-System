import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { supabase } from './lib/supabase.js'
import './index.css'

// Expose supabase globally for components that need it
window.supabase = supabase

// Note: StrictMode is disabled to prevent Supabase auth lock warnings in development
// Re-enable for production builds or when debugging component lifecycle issues
ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
)
