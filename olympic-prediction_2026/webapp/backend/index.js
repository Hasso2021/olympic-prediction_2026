import express from 'express'
import cors from 'cors'
import { testConnection, serverConfig } from './database/index.js'

const app = express()

// Middleware
app.use(cors())
app.use(express.json())

// Route de test
app.get('/api/health', async (req, res) => {
  try {
    const isConnected = await testConnection()
    res.json({
      status: 'OK',
      database: isConnected ? 'Connected' : 'Disconnected',
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    res.status(500).json({
      status: 'Error',
      message: error.message,
      timestamp: new Date().toISOString()
    })
  }
})

// Route de base
app.get('/', (req, res) => {
  res.json({
    message: 'API Olympic Prediction Backend',
    version: '1.0.0',
    endpoints: {
      health: '/api/health'
    }
  })
})

// Démarrer le serveur
const PORT = serverConfig.port
app.listen(PORT, () => {
  console.log(`🚀 Serveur démarré sur le port ${PORT}`)
  console.log(`📊 Test de connexion Supabase en cours...`)
  
  // Tester la connexion au démarrage
  testConnection().then(isConnected => {
    if (isConnected) {
      console.log('✅ Connexion Supabase établie avec succès!')
    } else {
      console.log('❌ Échec de la connexion Supabase')
    }
  })
})