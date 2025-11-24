import React, { useState } from 'react'
import axios from 'axios'

export default function Chat(){
  const [text, setText] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [learnerId, setLearnerId] = useState('demo_learner')

  const send = async () => {
    if (!text.trim()) return
    setLoading(true)
    setMessages(prev => [...prev, {from:'user', text}])
    
    try {
      const res = await axios.post('http://localhost:8000/api/query', {
        learner_id: learnerId, 
        text, 
        mode:'explain', 
        top_k:3
      }, {timeout: 30000})
      
      const d = res.data
      console.log('✅ Backend response:', d)  // Debug: voir la structure complète
      
      // ✅ CORRECTION: utiliser "response" au lieu de "text"
      setMessages(prev => [...prev, {
        from:'cleo', 
        text: d.response || d.text || 'Aucune réponse',  // Fallback si "response" absent
        emotion: d.emotion, 
        sources: d.sources
      }])
      
      setText('')
    } catch (e) {
      console.error('❌ Error calling /api/query:', e)
      setMessages(prev => [...prev, {
        from:'cleo', 
        text: `Erreur backend ou réseau: ${e.response?.data?.detail || e.message}`
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-4">
        <label className="text-sm font-medium text-gray-700">Learner ID</label>
        <input 
          className="ml-2 border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-indigo-500" 
          value={learnerId} 
          onChange={e=>setLearnerId(e.target.value)} 
        />
      </div>
      
      <div className="space-y-3 max-h-96 overflow-auto mb-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            Commencez une conversation avec CLEO...
          </div>
        )}
        
        {messages.map((m,i)=>(
          <div key={i} className={m.from==='user' ? 'text-right' : 'text-left'}>
            <div className={`inline-block px-4 py-2 rounded-lg max-w-[80%] ${
              m.from==='user' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-white text-gray-800 shadow-sm border border-gray-200'
            }`}>
              <div className="whitespace-pre-wrap">{m.text}</div>
              
              {m.emotion && (
                <div className="text-xs mt-2 pt-2 border-t border-gray-200 flex items-center gap-2">
                  <span className={`inline-block w-2 h-2 rounded-full ${
                    m.emotion.dominant_emotion === 'happy' ? 'bg-green-500' :
                    m.emotion.dominant_emotion === 'sad' ? 'bg-blue-500' :
                    m.emotion.dominant_emotion === 'angry' ? 'bg-red-500' :
                    'bg-gray-400'
                  }`}></span>
                  <span className="text-gray-600">
                    {m.emotion.dominant_emotion} ({(m.emotion.confidence*100||0).toFixed(0)}%)
                  </span>
                </div>
              )}
              
              {m.sources && m.sources.length>0 && (
                <div className="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-200">
                  <strong>Sources:</strong> {m.sources.map(s=>s.metadata?.source || 'N/A').join(', ')}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="text-left">
            <div className="inline-block px-4 py-2 rounded-lg bg-white shadow-sm border border-gray-200">
              <div className="flex items-center gap-2 text-gray-500">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                <span>CLEO réfléchit...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <textarea 
        className="w-full border border-gray-300 rounded-lg p-3 mb-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent" 
        rows="4" 
        placeholder="Posez votre question ici..."
        value={text} 
        onChange={e=>setText(e.target.value)}
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            send()
          }
        }}
      />
      
      <div className="flex gap-2">
        <button 
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors" 
          onClick={send} 
          disabled={loading || !text.trim()}
        >
          {loading ? 'Envoi en cours...' : 'Envoyer'}
        </button>
        
        <button 
          className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors" 
          onClick={() => {
            setMessages([])
            setText('')
          }}
        >
          Réinitialiser
        </button>
      </div>
    </div>
  )
}