import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Cpu, Trophy, Rocket, Heart, Bot, Check, ArrowRight, Loader2 } from 'lucide-react'
import { api } from '../api/client'
import useAppStore from '../store/appStore'

const CATEGORIES = [
  {
    id: 'tech',
    label: 'Tech',
    description: 'AI, startups & gadgets',
    Icon: Cpu,
    color: '#0066FF',
    bg: '#EBF3FF',
  },
  {
    id: 'nba',
    label: 'NBA',
    description: 'Scores, trades & highlights',
    Icon: Trophy,
    color: '#FF6B35',
    bg: '#FFF0EB',
  },
  {
    id: 'space',
    label: 'Space',
    description: 'NASA, SpaceX & beyond',
    Icon: Rocket,
    color: '#7B61FF',
    bg: '#F0EEFF',
  },
  {
    id: 'health',
    label: 'Health',
    description: 'Fitness, nutrition & wellness',
    Icon: Heart,
    color: '#00D9A3',
    bg: '#E6FAF5',
  },
  {
    id: 'ai',
    label: 'AI',
    description: 'Machine learning & ChatGPT',
    Icon: Bot,
    color: '#FF61B6',
    bg: '#FFE8F5',
  },
]

export default function Onboarding() {
  const [step, setStep] = useState(1)
  const [selectedInterests, setSelectedInterests] = useState([])
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const navigate = useNavigate()
  const setUser = useAppStore((s) => s.setUser)

  const toggleInterest = (id) => {
    setSelectedInterests((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }

  const handleCreateAccount = async () => {
    if (!name.trim() || !email.trim()) {
      setError('Please fill in your name and email.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const user = await api.createUser({
        name: name.trim(),
        email: email.trim(),
        interests: selectedInterests,
      })
      setUser(user)
      navigate('/feed')
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-light flex flex-col items-center justify-start">
      <div className="w-full max-w-[480px] min-h-screen flex flex-col">

        {/* Step 1: Welcome */}
        {step === 1 && (
          <div className="flex flex-col items-center justify-center flex-1 px-6 py-12 text-center slide-up">
            {/* Icon */}
            <div className="w-20 h-20 rounded-3xl bg-blue flex items-center justify-center mb-8 shadow-lg shadow-blue/30">
              <svg viewBox="0 0 40 40" fill="none" width="44" height="44">
                <polygon points="12,8 12,32 34,20" fill="white" />
              </svg>
            </div>

            {/* Wordmark */}
            <h1 className="text-6xl font-black tracking-tight text-blue mb-2 leading-none">
              PACE
            </h1>

            {/* Tagline */}
            <p className="text-lg font-semibold text-navy mb-3">
              Run at your Pace
            </p>

            {/* Subtitle */}
            <p className="text-gray-dark text-sm leading-relaxed max-w-[280px] mb-12">
              Personalized 60-second audio snippets for your run. Stay informed while you move.
            </p>

            {/* Get Started */}
            <button
              onClick={() => setStep(2)}
              className="w-full max-w-[320px] bg-blue text-white font-bold py-4 px-8 rounded-2xl text-base shadow-lg shadow-blue/30 hover:bg-blue-600 active:scale-95 transition-all duration-200 flex items-center justify-center gap-2"
            >
              Get Started
              <ArrowRight size={18} />
            </button>

            <p className="text-xs text-gray-dark mt-6 opacity-60">
              Free forever · No credit card needed
            </p>
          </div>
        )}

        {/* Step 2: Interest selection */}
        {step === 2 && (
          <div className="flex flex-col flex-1 px-4 py-8 slide-up">
            <div className="mb-6 px-2">
              <p className="text-xs font-bold text-blue uppercase tracking-widest mb-2">
                Step 1 of 2
              </p>
              <h2 className="text-2xl font-black text-navy mb-1">
                What gets you moving?
              </h2>
              <p className="text-gray-dark text-sm">
                Pick at least 1 topic. We'll curate your daily feed.
              </p>
            </div>

            {/* Category grid */}
            <div className="grid grid-cols-2 gap-3 mb-8">
              {CATEGORIES.map(({ id, label, description, Icon, color, bg }) => {
                const selected = selectedInterests.includes(id)
                return (
                  <button
                    key={id}
                    onClick={() => toggleInterest(id)}
                    className={`relative text-left p-4 rounded-2xl border-2 transition-all duration-200 active:scale-95 ${
                      selected
                        ? 'border-blue shadow-md shadow-blue/20'
                        : 'border-gray-mid bg-white hover:border-gray-dark/40'
                    }`}
                    style={selected ? { backgroundColor: '#EBF3FF' } : {}}
                  >
                    {selected && (
                      <div className="absolute top-3 right-3 w-5 h-5 bg-blue rounded-full flex items-center justify-center">
                        <Check size={11} color="white" strokeWidth={3} />
                      </div>
                    )}

                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center mb-3"
                      style={{ backgroundColor: bg }}
                    >
                      <Icon size={20} style={{ color }} />
                    </div>

                    <p className="font-bold text-navy text-sm mb-0.5">{label}</p>
                    <p className="text-gray-dark text-xs leading-snug">{description}</p>
                  </button>
                )
              })}
            </div>

            {/* Continue button */}
            <div className="mt-auto px-2">
              <button
                onClick={() => setStep(3)}
                disabled={selectedInterests.length === 0}
                className={`w-full py-4 rounded-2xl font-bold text-base transition-all duration-200 ${
                  selectedInterests.length > 0
                    ? 'bg-blue text-white shadow-lg shadow-blue/30 hover:bg-blue-600 active:scale-95'
                    : 'bg-gray-mid text-gray-dark cursor-not-allowed opacity-60'
                }`}
              >
                Continue ({selectedInterests.length} selected)
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Account creation */}
        {step === 3 && (
          <div className="flex flex-col flex-1 px-4 py-8 slide-up">
            <div className="mb-8 px-2">
              <p className="text-xs font-bold text-blue uppercase tracking-widest mb-2">
                Step 2 of 2
              </p>
              <h2 className="text-2xl font-black text-navy mb-1">
                Almost there
              </h2>
              <p className="text-gray-dark text-sm">
                Create your free account to save your preferences.
              </p>
            </div>

            {/* Selected interests summary */}
            <div className="bg-white rounded-2xl p-4 mb-6 border border-gray-mid mx-2">
              <p className="text-xs font-semibold text-gray-dark mb-2">Your interests</p>
              <div className="flex flex-wrap gap-2">
                {selectedInterests.map((id) => {
                  const cat = CATEGORIES.find((c) => c.id === id)
                  if (!cat) return null
                  return (
                    <span
                      key={id}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold"
                      style={{ color: cat.color, backgroundColor: cat.bg }}
                    >
                      <cat.Icon size={11} />
                      {cat.label}
                    </span>
                  )
                })}
              </div>
            </div>

            {/* Form */}
            <div className="flex flex-col gap-4 px-2 mb-6">
              <div>
                <label className="block text-xs font-semibold text-navy mb-1.5 ml-1">
                  Your name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Alex Johnson"
                  className="w-full bg-white border-2 border-gray-mid rounded-xl px-4 py-3 text-navy text-sm font-medium placeholder-gray-dark/50 outline-none focus:border-blue transition-colors"
                  autoComplete="name"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-navy mb-1.5 ml-1">
                  Email address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex@example.com"
                  className="w-full bg-white border-2 border-gray-mid rounded-xl px-4 py-3 text-navy text-sm font-medium placeholder-gray-dark/50 outline-none focus:border-blue transition-colors"
                  autoComplete="email"
                />
              </div>
            </div>

            {error && (
              <div className="mx-2 mb-4 bg-red-50 border border-red-200 text-red-600 text-sm rounded-xl px-4 py-3">
                {error}
              </div>
            )}

            <div className="mt-auto px-2">
              <button
                onClick={handleCreateAccount}
                disabled={loading || !name.trim() || !email.trim()}
                className={`w-full py-4 rounded-2xl font-bold text-base transition-all duration-200 flex items-center justify-center gap-2 ${
                  !loading && name.trim() && email.trim()
                    ? 'bg-blue text-white shadow-lg shadow-blue/30 hover:bg-blue-600 active:scale-95'
                    : 'bg-gray-mid text-gray-dark cursor-not-allowed opacity-60'
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Creating account...
                  </>
                ) : (
                  <>
                    Start Running
                    <ArrowRight size={18} />
                  </>
                )}
              </button>

              <button
                onClick={() => setStep(2)}
                className="w-full mt-3 py-3 text-gray-dark text-sm font-medium hover:text-navy transition-colors"
              >
                ← Back
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
