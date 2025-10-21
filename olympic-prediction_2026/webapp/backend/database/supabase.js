import { createClient } from '@supabase/supabase-js'
import { supabaseConfig } from './config.js'

// Configuration Supabase
const supabaseUrl = supabaseConfig.url
const supabaseKey = supabaseConfig.key

// Créer le client Supabase
const supabase = createClient(supabaseUrl, supabaseKey)

// Fonction pour tester la connexion
export const testConnection = async () => {
  try {
    // Test de connexion avec la table athlete existante
    const { data, error } = await supabase
      .from('athlete')
      .select('*')
      .limit(1)
    
    if (error) {
      console.error('Erreur de connexion Supabase:', error)
      return false
    }
    console.log('Connexion Supabase réussie!')
    return true
  } catch (err) {
    console.error('Erreur lors du test de connexion:', err)
    return false
  }
}

// Export du client Supabase
export default supabase

// Export des fonctions utilitaires
export const supabaseClient = supabase
