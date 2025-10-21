import { testConnection } from './database/index.js'

// Script simple pour tester la connexion à la base de données
async function testDatabaseConnection() {
  console.log('🔍 TEST DE CONNEXION À LA BASE DE DONNÉES')
  console.log('='.repeat(50))
  
  try {
    console.log('1️⃣ Test de connexion Supabase...')
    const isConnected = await testConnection()
    
    if (isConnected) {
      console.log('✅ Connexion Supabase réussie!')
      console.log('🎉 Base de données accessible')
      console.log('📊 Vous pouvez maintenant utiliser votre API')
    } else {
      console.log('❌ Échec de la connexion Supabase')
      console.log('🔧 Vérifiez vos variables d\'environnement')
    }
    
  } catch (error) {
    console.error('❌ Erreur lors du test:', error.message)
    console.log('💡 Solutions possibles:')
    console.log('   1. Vérifiez que le fichier .env existe')
    console.log('   2. Vérifiez que SUPABASE_KEY est défini')
    console.log('   3. Vérifiez que SUPABASE_URL est correct')
  }
}

// Exécuter le test
testDatabaseConnection()
