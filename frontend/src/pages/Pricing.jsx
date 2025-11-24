import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import Navbar from '../components/Navbar'

export default function Pricing() {
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [plans, setPlans] = useState([])
  const [currentSubscription, setCurrentSubscription] = useState(null)
  const [loading, setLoading] = useState(true)
  const [billingCycle, setBillingCycle] = useState('monthly') // monthly or yearly
  const [upgrading, setUpgrading] = useState(null)

  useEffect(() => {
    fetchPlans()
    if (user) {
      fetchCurrentSubscription()
    }
  }, [user])

  const fetchPlans = async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/subscriptions/plans')
    
    console.log('📋 API Response:', res.data)
    
    // ⭐ Le backend retourne directement un array de plans
    let plansArray = []
    
    if (Array.isArray(res.data)) {
      // Si c'est déjà un array
      plansArray = res.data
    } else if (res.data.plans && Array.isArray(res.data.plans)) {
      // Si c'est {plans: [...]}
      plansArray = res.data.plans
    }
    
    console.log('✅ Plans loaded:', plansArray.length, 'plans')
    
    // Vérifier que le plan FREE existe déjà
    const hasFree = plansArray.some(p => p.tier === 'free')
    
    if (!hasFree) {
      // Ajouter FREE uniquement s'il n'existe pas
      const freePlan = {
        id: 0,
        tier: 'free',
        name: 'Free Plan',
        description: 'Get started with basic features',
        price_monthly: 0,
        price_yearly: 0,
        badge: null,
        display_order: 0,
        limits: {
          quizzes_per_month: 5,
          questions_per_quiz: 5,
          subjects_access: 2,
          ai_hints_per_month: 0,
          analytics_history_days: 7,
          can_export_data: false
        },
        features: [
          '5 quizzes per month',
          '5 questions per quiz',
          '2 subjects access',
          '7-day analytics history',
          'Basic progress tracking'
        ]
      }
      
      plansArray = [freePlan, ...plansArray]
    }
    
    // Trier par display_order
    plansArray.sort((a, b) => (a.display_order || 0) - (b.display_order || 0))
    
    console.log('📦 Final plans:', plansArray.map(p => p.name))
    
    setPlans(plansArray)
    
  } catch (error) {
    console.error('❌ Error fetching plans:', error)
    
    // Fallback avec plans hardcodés
    const fallbackPlans = [
      {
        id: 0,
        tier: 'free',
        name: 'Free Plan',
        description: 'Get started with basic features',
        price_monthly: 0,
        price_yearly: 0,
        badge: null,
        display_order: 0,
        limits: {
          quizzes_per_month: 5,
          questions_per_quiz: 5,
          subjects_access: 2,
          ai_hints_per_month: 0,
          analytics_history_days: 7,
          can_export_data: false
        },
        features: [
          '5 quizzes per month',
          '5 questions per quiz',
          '2 subjects access',
          '7-day analytics'
        ]
      },
      {
        id: 2,
        tier: 'bronze',
        name: 'Bronze Plan',
        description: 'Perfect for learners getting started',
        price_monthly: 9.99,
        price_yearly: 99.99,
        badge: '🥉 Popular',
        display_order: 1,
        limits: {
          quizzes_per_month: 20,
          questions_per_quiz: 10,
          subjects_access: 5,
          ai_hints_per_month: 10,
          analytics_history_days: 30,
          can_export_data: true
        },
        features: [
          '20 quizzes/month',
          '10 questions/quiz',
          '5 subjects access',
          '10 AI hints/month',
          '30-day analytics',
          'Export data (PDF)'
        ]
      },
      {
        id: 3,
        tier: 'silver',
        name: 'Silver Plan',
        description: 'For serious learners',
        price_monthly: 19.99,
        price_yearly: 199.99,
        badge: '🥈 Best Value',
        display_order: 2,
        limits: {
          quizzes_per_month: 50,
          questions_per_quiz: 15,
          subjects_access: 999,
          ai_hints_per_month: 50,
          analytics_history_days: 90,
          can_export_data: true
        },
        features: [
          '50 quizzes/month',
          '15 questions/quiz',
          'All subjects access',
          '50 AI hints/month',
          '90-day analytics',
          'Priority support'
        ]
      },
      {
        id: 4,
        tier: 'gold',
        name: 'Gold Plan',
        description: 'Advanced learning features',
        price_monthly: 29.99,
        price_yearly: 399.99,
        badge: '🥇 Premium',
        display_order: 3,
        limits: {
          quizzes_per_month: 150,
          questions_per_quiz: 20,
          subjects_access: 999,
          ai_hints_per_month: 200,
          analytics_history_days: 365,
          can_export_data: true
        },
        features: [
          '150 quizzes/month',
          '20 questions/quiz',
          'All subjects access',
          '200 AI hints/month',
          '1-year analytics',
          'Custom learning paths'
        ]
      },
      {
        id: 5,
        tier: 'platinum',
        name: 'Platinum Plan',
        description: 'Unlimited everything',
        price_monthly: 49.99,
        price_yearly: 799.99,
        badge: '💎 Ultimate',
        display_order: 4,
        limits: {
          quizzes_per_month: 999,
          questions_per_quiz: 30,
          subjects_access: 999,
          ai_hints_per_month: 999,
          analytics_history_days: 999,
          can_export_data: true
        },
        features: [
          'Unlimited quizzes',
          '30 questions/quiz',
          'All subjects access',
          'Unlimited AI hints',
          'Lifetime analytics',
          'VIP support 24/7'
        ]
      }
    ]
    
    setPlans(fallbackPlans)
  } finally {
    setLoading(false)
  }
}

  const fetchCurrentSubscription = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await axios.get('http://localhost:8000/api/subscriptions/current', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setCurrentSubscription(res.data.subscription)
    } catch (error) {
      console.error('Error fetching subscription:', error)
    }
  }

  const handleUpgrade = async (plan) => {
    if (!user) {
      navigate('/signin', { state: { message: 'Please sign in to upgrade' } })
      return
    }

    if (currentSubscription?.tier === plan.tier) {
      alert('You are already on this plan!')
      return
    }

    // Si FREE, pas de paiement
    if (plan.tier === 'free') {
      alert('You are already on the FREE plan or cannot downgrade to FREE directly.')
      return
    }

    setUpgrading(plan.tier)

    try {
      const token = localStorage.getItem('access_token')
      
      // ⭐ Appeler Stripe Checkout
      const res = await axios.post(
        'http://localhost:8000/api/payment/create-checkout-session',
        { tier: plan.tier },
        { headers: { Authorization: `Bearer ${token}` } }
      )

      console.log('✅ Checkout URL:', res.data.checkout_url)
      
      // Rediriger vers Stripe Checkout
      window.location.href = res.data.checkout_url

    } catch (error) {
      console.error('Error upgrading:', error)
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          alert(error.response.data.detail)
        } else {
          alert(error.response.data.detail.message || 'Error processing upgrade')
        }
      } else {
        alert('Error processing upgrade. Please try again.')
      }
      
      setUpgrading(null)
    }
  }

  const getPrice = (plan) => {
    return billingCycle === 'monthly' ? plan.price_monthly : (plan.price_yearly || plan.price_monthly * 12)
  }

  const getSavings = (plan) => {
    if (billingCycle === 'yearly' && plan.price_yearly && plan.price_monthly > 0) {
      const monthlyCost = plan.price_monthly * 12
      const yearlyCost = plan.price_yearly
      const savings = monthlyCost - yearlyCost
      return savings.toFixed(2)
    }
    return 0
  }

  const getPlanColor = (tier) => {
    const colors = {
      free: 'from-gray-400 to-gray-500',
      bronze: 'from-orange-600 to-amber-700',
      silver: 'from-gray-400 to-gray-600',
      gold: 'from-yellow-400 to-yellow-600',
      platinum: 'from-purple-600 to-indigo-600'
    }
    return colors[tier] || 'from-indigo-600 to-purple-600'
  }

  const getPlanIcon = (tier) => {
    const icons = {
      free: '🎓',
      bronze: '🥉',
      silver: '🥈',
      gold: '🥇',
      platinum: '💎'
    }
    return icons[tier] || '📦'
  }

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600">Loading plans...</p>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <Navbar />

      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-6">
        <div className="max-w-7xl mx-auto">

          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              Choose Your Learning Journey 🚀
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Unlock your full potential with adaptive learning powered by AI
            </p>

            {/* Billing Toggle */}
            <div className="inline-flex items-center gap-4 bg-white rounded-full p-2 shadow-lg">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-full font-semibold transition-all ${
                  billingCycle === 'monthly'
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-6 py-2 rounded-full font-semibold transition-all relative ${
                  billingCycle === 'yearly'
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Yearly
                <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                  Save 20%
                </span>
              </button>
            </div>
          </div>

          {/* Current Plan Banner */}
          {currentSubscription && (
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl p-6 mb-8 text-center">
              <p className="text-lg">
                <span className="font-semibold">Your current plan:</span>{' '}
                <span className="text-2xl font-bold">
                  {getPlanIcon(currentSubscription.tier)} {currentSubscription.tier.toUpperCase()}
                </span>
              </p>
            </div>
          )}

          {/* Plans Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-16">
            {plans.map((plan) => {
              const isCurrentPlan = currentSubscription?.tier === plan.tier
              const price = getPrice(plan)
              const savings = getSavings(plan)

              return (
                <div
                  key={plan.id}
                  className={`relative bg-white rounded-2xl shadow-xl overflow-hidden transition-all duration-300 hover:scale-105 ${
                    plan.badge ? 'border-4 border-indigo-500' : ''
                  }`}
                >
                  {/* Badge */}
                  {plan.badge && (
                    <div className="absolute top-0 right-0 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-1 text-sm font-bold rounded-bl-xl">
                      {plan.badge}
                    </div>
                  )}

                  {/* Current Plan Badge */}
                  {isCurrentPlan && (
                    <div className="absolute top-0 left-0 bg-green-500 text-white px-4 py-1 text-sm font-bold rounded-br-xl">
                      ✓ Current Plan
                    </div>
                  )}

                  {/* Header */}
                  <div className={`bg-gradient-to-r ${getPlanColor(plan.tier)} p-6 text-center`}>
                    <div className="text-6xl mb-2">{getPlanIcon(plan.tier)}</div>
                    <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                    <p className="text-white text-opacity-90 text-sm">{plan.description}</p>
                  </div>

                  {/* Price */}
                  <div className="p-6 text-center border-b">
                    {price === 0 ? (
                      <div>
                        <div className="text-4xl font-bold text-gray-900">Free</div>
                        <div className="text-sm text-gray-500">Forever</div>
                      </div>
                    ) : (
                      <div>
                        <div className="text-4xl font-bold text-gray-900">
                          ${price}
                          <span className="text-lg text-gray-500">
                            /{billingCycle === 'monthly' ? 'mo' : 'yr'}
                          </span>
                        </div>
                        {billingCycle === 'yearly' && savings > 0 && (
                          <div className="text-sm text-green-600 font-semibold mt-1">
                            Save ${savings}/year
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Features */}
                  <div className="p-6">
                    <ul className="space-y-3">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <span className="text-green-500 flex-shrink-0 mt-0.5">✓</span>
                          <span className="text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* CTA Button */}
                  <div className="p-6 pt-0">
                    <button
                      onClick={() => handleUpgrade(plan)}
                      disabled={isCurrentPlan || upgrading === plan.tier}
                      className={`w-full py-3 rounded-lg font-bold transition-all ${
                        isCurrentPlan
                          ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                          : upgrading === plan.tier
                          ? 'bg-gray-400 text-white cursor-wait'
                          : plan.tier === 'free'
                          ? 'bg-gray-600 text-white hover:bg-gray-700'
                          : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-xl'
                      }`}
                    >
                      {isCurrentPlan
                        ? '✓ Current Plan'
                        : upgrading === plan.tier
                        ? '⏳ Processing...'
                        : plan.tier === 'free'
                        ? '🎓 Get Started'
                        : user
                        ? '🚀 Upgrade Now'
                        : '📝 Sign Up'}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Comparison Table */}
          <ComparisonTable plans={plans} />

          {/* FAQ */}
          <FAQ />

        </div>
      </div>
    </>
  )
}

// ========================================
// Comparison Table Component
// ========================================

function ComparisonTable({ plans }) {
  if (plans.length === 0) return null

  const features = [
    { key: 'quizzes_per_month', label: 'Quizzes per Month', icon: '📝' },
    { key: 'questions_per_quiz', label: 'Questions per Quiz', icon: '❓' },
    { key: 'subjects_access', label: 'Subjects Access', icon: '📚' },
    { key: 'ai_hints_per_month', label: 'AI Hints per Month', icon: '💡' },
    { key: 'analytics_history_days', label: 'Analytics History', icon: '📊' },
    { key: 'can_export_data', label: 'Export Data', icon: '📥' }
  ]

  const formatValue = (value, key) => {
    if (value === 999) return '∞ Unlimited'
    if (value === true) return '✓'
    if (value === false) return '✗'
    if (key === 'analytics_history_days') return `${value} days`
    if (key === 'subjects_access' && value === 999) return 'All'
    return value
  }

  return (
    <div className="mb-16">
      <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
        📋 Detailed Comparison
      </h2>

      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
              <tr>
                <th className="px-6 py-4 text-left font-bold">Feature</th>
                {plans.map((plan) => (
                  <th key={plan.id} className="px-6 py-4 text-center font-bold">
                    {plan.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {features.map((feature, idx) => (
                <tr
                  key={feature.key}
                  className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}
                >
                  <td className="px-6 py-4 font-semibold text-gray-700">
                    <span className="mr-2">{feature.icon}</span>
                    {feature.label}
                  </td>
                  {plans.map((plan) => (
                    <td key={plan.id} className="px-6 py-4 text-center text-gray-900 font-medium">
                      {formatValue(plan.limits[feature.key], feature.key)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// ========================================
// FAQ Component
// ========================================

function FAQ() {
  const [openIndex, setOpenIndex] = useState(null)

  const faqs = [
    {
      question: "Quelle est la différence entre les packs ?",
      answer: "Chaque pack offre des limites différentes. FREE est parfait pour débuter (5 quiz/mois). BRONZE convient aux apprenants occasionnels (20 quiz/mois). SILVER pour les étudiants dédiés (50 quiz/mois + tous les sujets). GOLD pour les apprenants sérieux (150 quiz/mois + analytics avancés). PLATINUM offre un accès illimité avec support VIP 24/7."
    },
    {
      question: "Puis-je changer de pack à tout moment ?",
      answer: "Oui ! Vous pouvez upgrader instantanément via Stripe. Si vous downgradez, le changement prendra effet à la fin de votre période de facturation actuelle."
    },
    {
      question: "Comment fonctionnent les quotas mensuels ?",
      answer: "Les quotas se réinitialisent automatiquement chaque mois. Par exemple, si vous avez le pack Bronze (20 quiz/mois), vous recevez 20 nouveaux quiz le 1er de chaque mois."
    },
    {
      question: "Qu'est-ce que les 'AI Hints' ?",
      answer: "Les AI Hints sont des indices personnalisés générés par l'IA pour vous aider quand vous êtes bloqué sur une question, sans vous donner directement la réponse."
    },
    {
      question: "Y a-t-il un engagement ?",
      answer: "Non ! Vous pouvez annuler à tout moment via le Customer Portal Stripe. Votre abonnement restera actif jusqu'à la fin de votre période payée."
    },
    {
      question: "Comment sont traités les paiements ?",
      answer: "Tous les paiements sont traités en toute sécurité par Stripe, le leader mondial du paiement en ligne. Nous n'enregistrons jamais vos informations de carte bancaire."
    },
    {
      question: "Que se passe-t-il si je dépasse mes quotas ?",
      answer: "Vous recevrez une notification vous invitant à upgrader. Vous pouvez également attendre le mois prochain pour que vos quotas se réinitialisent."
    }
  ]

  return (
    <div className="mb-16">
      <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
        ❓ Frequently Asked Questions
      </h2>

      <div className="max-w-3xl mx-auto space-y-4">
        {faqs.map((faq, idx) => (
          <div
            key={idx}
            className="bg-white rounded-xl shadow-md overflow-hidden"
          >
            <button
              onClick={() => setOpenIndex(openIndex === idx ? null : idx)}
              className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <span className="font-semibold text-gray-900">{faq.question}</span>
              <svg
                className={`w-5 h-5 text-gray-500 transition-transform ${
                  openIndex === idx ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {openIndex === idx && (
              <div className="px-6 py-4 bg-gray-50 border-t">
                <p className="text-gray-700">{faq.answer}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}