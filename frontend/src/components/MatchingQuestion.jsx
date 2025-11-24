import React, { useState, useEffect } from 'react'

export default function MatchingQuestion({ question, onSubmit, disabled }) {
  const [matches, setMatches] = useState({})
  const [selectedLeft, setSelectedLeft] = useState(null)
  const [availableRightItems, setAvailableRightItems] = useState([])

  const leftItems = question.left_items || question.question_data?.left_items || []
  const rightItems = question.right_items || question.question_data?.right_items || []

  useEffect(() => {
    // Initialiser les items de droite disponibles
    setAvailableRightItems(rightItems.map(item => item.id))
  }, [rightItems])

  const handleLeftClick = (leftId) => {
    if (disabled) return
    setSelectedLeft(leftId)
  }

  const handleRightClick = (rightId) => {
    if (disabled || !selectedLeft) return

    // Créer le match
    const newMatches = { ...matches }
    
    // Retirer l'ancien match de cet item de gauche s'il existe
    if (newMatches[selectedLeft]) {
      const oldRightId = newMatches[selectedLeft]
      setAvailableRightItems([...availableRightItems, oldRightId])
    }
    
    // Retirer l'ancien match de cet item de droite s'il existe
    const leftIdWithThisRight = Object.keys(newMatches).find(
      key => newMatches[key] === rightId
    )
    if (leftIdWithThisRight) {
      delete newMatches[leftIdWithThisRight]
    }
    
    // Créer le nouveau match
    newMatches[selectedLeft] = rightId
    setMatches(newMatches)
    
    // Retirer de la liste des disponibles
    setAvailableRightItems(availableRightItems.filter(id => id !== rightId))
    
    // Désélectionner
    setSelectedLeft(null)
  }

  const handleRemoveMatch = (leftId) => {
    if (disabled) return
    const rightId = matches[leftId]
    const newMatches = { ...matches }
    delete newMatches[leftId]
    setMatches(newMatches)
    setAvailableRightItems([...availableRightItems, rightId])
  }

  const handleSubmit = () => {
    if (Object.keys(matches).length !== leftItems.length) {
      alert('Please match all items before submitting')
      return
    }
    
    // Convertir en format attendu par le backend
    const matchesArray = Object.entries(matches).map(([left, right]) => ({
      left,
      right
    }))
    
    onSubmit(matchesArray)
  }

  const getMatchedRightItem = (leftId) => {
    const rightId = matches[leftId]
    return rightItems.find(item => item.id === rightId)
  }

  // ⭐ Renommer cette fonction pour éviter confusion
  const checkIfMatched = (itemId, side) => {
    if (side === 'left') {
      return matches[itemId] !== undefined
    } else {
      return Object.values(matches).includes(itemId)
    }
  }

  const allMatched = Object.keys(matches).length === leftItems.length

  return (
    <div>
      {/* Bloom Level Badge */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-bold text-white ${
            question.bloom_level === 1 ? 'bg-blue-500' :
            question.bloom_level === 2 ? 'bg-green-500' :
            question.bloom_level === 3 ? 'bg-yellow-500' :
            question.bloom_level === 4 ? 'bg-orange-500' :
            question.bloom_level === 5 ? 'bg-red-500' :
            'bg-purple-500'
          }`}>
            Level {question.bloom_level} - {question.bloom_label}
          </span>
          <span className="text-xs text-gray-500">
            {question.points} points
          </span>
        </div>
        
        <span className="text-xs text-gray-500">Matching Question</span>
      </div>

      {/* Question Text */}
      <h3 className="text-xl font-bold text-gray-900 mb-4">
        {question.question_text}
      </h3>

      {/* Instructions */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6 rounded">
        <p className="text-sm text-blue-800">
          <span className="font-semibold">Instructions:</span> Click an item on the left, 
          then click its match on the right. You can change matches by clicking the ✕ button.
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-gray-700">
            Matched: {Object.keys(matches).length} / {leftItems.length}
          </span>
          {allMatched && (
            <span className="text-sm font-semibold text-green-600 flex items-center gap-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              All matched!
            </span>
          )}
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              allMatched ? 'bg-green-500' : 'bg-indigo-500'
            }`}
            style={{ width: `${(Object.keys(matches).length / leftItems.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Matching Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        
        {/* Left Column */}
        <div>
          <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">
            Items
          </h4>
          <div className="space-y-3">
            {leftItems.map((item, idx) => {
              const matched = getMatchedRightItem(item.id)
              const isSelected = selectedLeft === item.id
              
              return (
                <div
                  key={item.id}
                  className={`relative p-4 rounded-lg border-2 transition-all cursor-pointer ${
                    matched
                      ? 'bg-green-50 border-green-400 shadow-sm'
                      : isSelected
                      ? 'bg-indigo-100 border-indigo-500 shadow-md ring-2 ring-indigo-200'
                      : 'bg-white border-gray-300 hover:border-indigo-400 hover:shadow-sm'
                  } ${disabled ? 'cursor-not-allowed opacity-60' : ''}`}
                  onClick={() => handleLeftClick(item.id)}
                >
                  <div className="flex items-start gap-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      matched
                        ? 'bg-green-500 text-white'
                        : isSelected
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}>
                      {idx + 1}
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-800 font-medium">{item.text}</p>
                      
                      {/* Show matched item */}
                      {matched && (
                        <div className="mt-2 pt-2 border-t border-green-200">
                          <div className="flex items-center justify-between">
                            <p className="text-sm text-green-700">
                              ↔️ {matched.text}
                            </p>
                            {!disabled && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleRemoveMatch(item.id)
                                }}
                                className="text-red-500 hover:text-red-700 font-bold text-lg"
                                title="Remove match"
                              >
                                ✕
                              </button>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {isSelected && !matched && (
                    <div className="absolute -right-3 top-1/2 transform -translate-y-1/2">
                      <div className="bg-indigo-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold animate-pulse">
                        →
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Column */}
        <div>
          <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">
            Matches
          </h4>
          <div className="space-y-3">
            {rightItems.map((item, idx) => {
              const isAvailable = availableRightItems.includes(item.id)
              const itemIsMatched = checkIfMatched(item.id, 'right')  // ⭐ Utiliser la fonction renommée
              const canClick = !disabled && selectedLeft && isAvailable
              
              return (
                <div
                  key={item.id}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    itemIsMatched
                      ? 'bg-gray-100 border-gray-300 opacity-50'
                      : canClick
                      ? 'bg-white border-indigo-400 hover:bg-indigo-50 hover:shadow-md cursor-pointer ring-2 ring-indigo-100'
                      : isAvailable
                      ? 'bg-white border-gray-300'
                      : 'bg-gray-50 border-gray-200 opacity-50'
                  } ${disabled ? 'cursor-not-allowed' : ''}`}
                  onClick={() => canClick && handleRightClick(item.id)}
                >
                  <div className="flex items-start gap-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      itemIsMatched
                        ? 'bg-gray-400 text-white'
                        : canClick
                        ? 'bg-indigo-500 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {String.fromCharCode(65 + idx)}
                    </div>
                    <p className={`text-gray-800 flex-1 ${
                      itemIsMatched ? 'line-through' : 'font-medium'
                    }`}>
                      {item.text}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Helper Text */}
      {selectedLeft && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6 animate-pulse">
          <p className="text-sm text-indigo-800 text-center font-medium">
            👉 Now click the matching item on the right
          </p>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={disabled || !allMatched}
        className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? 'Submitting...' : allMatched ? '✓ Submit Answer' : `Match ${leftItems.length - Object.keys(matches).length} more`}
      </button>
    </div>
  )
}