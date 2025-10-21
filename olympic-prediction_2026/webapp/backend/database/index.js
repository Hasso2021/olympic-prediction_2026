// Point d'entrée pour toutes les fonctionnalités de base de données
export { testConnection, default as supabase, supabaseClient } from './supabase.js'
export { supabaseConfig, serverConfig } from './config.js'

// Export par défaut de tous les modules de base de données
export default {
  supabase: () => import('./supabase.js'),
  config: () => import('./config.js')
}
