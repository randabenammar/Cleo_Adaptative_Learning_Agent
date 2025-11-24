/**
 * Mapping des icônes pour les sujets.
 * Permet d'afficher des icônes personnalisées sans modifier la DB.
 */

export const subjectIconMap = {
  // Data Science & Analytics
  "big data": "📊",
  "data science": "📈",
  "data analytics": "📉",
  "statistics": "📊",
  
  // Cloud & Infrastructure
  "cloud computing": "☁️",
  "aws": "☁️",
  "azure": "☁️",
  "gcp": "☁️",
  "google cloud": "☁️",
  "devops": "⚙️",
  "docker": "🐳",
  "kubernetes": "☸️",
  
  // Security
  "cybersecurity": "🔒",
  "security": "🔐",
  "network security": "🛡️",
  "ethical hacking": "🕵️",
  
  // AI & ML
  "artificial intelligence": "🧠",
  "machine learning": "🤖",
  "deep learning": "🧠",
  "neural networks": "🧠",
  "nlp": "💬",
  "computer vision": "👁️",
  
  // Programming Languages
  "python": "🐍",
  "javascript": "💛",
  "java": "☕",
  "c++": "⚡",
  "c#": "🎯",
  "go": "🔵",
  "rust": "🦀",
  "ruby": "💎",
  "php": "🐘",
  "swift": "🍎",
  "kotlin": "🟣",
  
  // Web Development
  "web development": "🌐",
  "frontend": "🎨",
  "backend": "⚙️",
  "full stack": "🎯",
  "html": "🌐",
  "css": "🎨",
  "react": "⚛️",
  "vue": "💚",
  "angular": "🔺",
  "node.js": "🟢",
  "express": "🚂",
  "django": "🎸",
  "flask": "🧪",
  
  // Mobile
  "mobile development": "📱",
  "android": "🤖",
  "ios": "🍎",
  "react native": "⚛️📱",
  "flutter": "🦋",
  
  // Database
  "database": "🗄️",
  "sql": "💾",
  "mysql": "🐬",
  "postgresql": "🐘",
  "mongodb": "🍃",
  "redis": "🔴",
  
  // Blockchain & Crypto
  "blockchain": "⛓️",
  "cryptocurrency": "₿",
  "ethereum": "💎",
  "smart contracts": "📜",
  
  // IoT & Hardware
  "iot": "📡",
  "arduino": "🤖",
  "raspberry pi": "🥧",
  "robotics": "🦾",
  
  // Other
  "algorithms": "🧮",
  "data structures": "🏗️",
  "git": "📦",
  "linux": "🐧",
  "networking": "🌐",
  "api": "🔌",
  "microservices": "🎯",
  "graphql": "📊",
  "testing": "🧪",
  "agile": "🏃",
}

export const categoryIconMap = {
  "Data Science": "📊",
  "Technology": "💻",
  "Security": "🔐",
  "AI": "🤖",
  "Programming": "👨‍💻",
  "Cloud": "☁️",
  "Web": "🌐",
  "Mobile": "📱",
  "Database": "🗄️",
  "DevOps": "⚙️",
}

/**
 * Récupère l'icône pour un sujet donné.
 * @param {string} subjectName - Nom du sujet
 * @param {string} category - Catégorie du sujet (optionnel)
 * @returns {string} - Emoji représentant le sujet
 */
export function getSubjectIcon(subjectName, category = null) {
  if (!subjectName) return "📚"
  
  const nameLower = subjectName.toLowerCase()
  
  // Chercher une correspondance exacte
  if (subjectIconMap[nameLower]) {
    return subjectIconMap[nameLower]
  }
  
  // Chercher une correspondance partielle
  for (const [key, icon] of Object.entries(subjectIconMap)) {
    if (nameLower.includes(key) || key.includes(nameLower)) {
      return icon
    }
  }
  
  // Fallback sur la catégorie
  if (category && categoryIconMap[category]) {
    return categoryIconMap[category]
  }
  
  // Icône par défaut
  return "📚"
}