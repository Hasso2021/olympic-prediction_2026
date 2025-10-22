import dotenv from 'dotenv'

// Charger les variables d'environnement
dotenv.config()

// Configuration Supabase
export const supabaseConfig = {
  url: process.env.SUPABASE_URL || 'https://xecsougqsdyrrzscmtgn.supabase.co',
  key: process.env.SUPABASE_KEY || (() => {
    console.error('❌ SUPABASE_KEY environment variable is required!')
    console.error('Please create a .env file with your Supabase key')
    process.exit(1)
  })()
}

// Configuration du serveur
export const serverConfig = {
  port: process.env.PORT || 3001,
  nodeEnv: process.env.NODE_ENV || 'development'
}
